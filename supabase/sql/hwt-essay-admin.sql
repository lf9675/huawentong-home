-- Additive: share the original codes, usage counters and teacher sessions.
begin;
alter table public.access_codes add column if not exists admin_revision integer not null default 0;
create index if not exists hwt_code_usage_recent on public.code_usage_log(code_id,used_at desc);
create table if not exists public.hwt_essay_code_requests (
 request_id uuid primary key,
 fingerprint text not null,
 action text not null,
 result jsonb not null,
 created_at timestamptz not null default now()
);
comment on table public.hwt_essay_code_requests is 'Idempotent teacher operations; contains metadata and hashes only, never plaintext codes or teacher sessions.';
alter table public.hwt_essay_code_requests enable row level security;
revoke all on public.hwt_essay_code_requests from public,anon,authenticated;
grant select,insert on public.hwt_essay_code_requests to service_role;

create or replace function public.hwt_essay_manage_codes(p_session text,p_action text,p_data jsonb default '{}')
returns jsonb language plpgsql security invoker set search_path='' as $$
declare
 c public.access_codes%rowtype; result jsonb; previous public.hwt_essay_code_requests%rowtype;
 request uuid; fingerprint text; total_n integer; new_n integer; expiry_s text; exam_s text;
 day_s text:=to_char(now() at time zone 'Asia/Singapore','YYYY-MM-DD');
 query_s text:=coalesce(p_data->>'query',''); filter_s text:=coalesce(p_data->>'status','all');
 page_n integer:=coalesce((p_data->>'page')::integer,1);
begin
 -- Check again inside the transaction, including retries of already completed operations.
 if p_session is null or p_session !~ '^[0-9a-f]{64}$' or not exists(
  select 1 from public.hwt_sessions where token_hash=p_session and expires_at>now()
 ) then return jsonb_build_object('error','教师登录已过期，请重新登录。','status',401);end if;

 if p_action='list' then
  if page_n<1 or page_n>100000 or length(query_s)>100 or filter_s not in ('all','available','disabled','expired','exhausted') then
   return jsonb_build_object('error','筛选条件无效。');end if;
  with filtered as (
   select a.* from public.access_codes a where
    (query_s='' or strpos(lower(coalesce(a.nickname,'')),lower(query_s))>0 or strpos(lower(coalesce(a.note,'')),lower(query_s))>0 or a.id::text=query_s)
    and (coalesce(p_data->>'query_hash','')='' or a.code_hash=p_data->>'query_hash')
    and (filter_s='all'
     or (filter_s='disabled' and a.is_active is distinct from 1)
     or (filter_s='expired' and a.is_active=1 and nullif(a.expiry,'')<day_s)
     or (filter_s='exhausted' and a.is_active=1 and (nullif(a.expiry,'') is null or a.expiry>=day_s)
      and (coalesce(a.essays_used,0)>=a.essays_total or (coalesce(a.new_essays_total,0)>0 and coalesce(a.new_essays_used,0)>=a.new_essays_total)))
     or (filter_s='available' and a.is_active=1 and (nullif(a.expiry,'') is null or a.expiry>=day_s)
      and coalesce(a.essays_used,0)<a.essays_total and (coalesce(a.new_essays_total,0)=0 or coalesce(a.new_essays_used,0)<a.new_essays_total)))
  ), paged as (select * from filtered order by id desc limit 30 offset (page_n-1)*30)
  select jsonb_build_object('total',(select count(*) from filtered),'page',page_n,'page_size',30,'today',day_s,
   'codes',coalesce((select jsonb_agg((to_jsonb(p)-'code_hash')||jsonb_build_object('last_used',(select max(l.used_at) from public.code_usage_log l where l.code_id=p.id)) order by p.id desc) from paged p),'[]'::jsonb)) into result;
  return result;
 end if;
 if p_action='detail' then
  select * into c from public.access_codes where id=(p_data->>'id')::integer;
  if not found then return jsonb_build_object('error','访问码记录不存在。','status',404);end if;
  return jsonb_build_object('code',to_jsonb(c)-'code_hash','usage',coalesce((select jsonb_agg(to_jsonb(l) order by l.used_at desc,l.id desc)
   from (select id,used_at,submission_id from public.code_usage_log where code_id=c.id order by used_at desc,id desc limit 20) l),'[]'::jsonb));
 end if;
 if p_action not in ('create','update','set_active','rotate') then return jsonb_build_object('error','未知操作。');end if;
 request:=(p_data->>'request_id')::uuid;fingerprint:=p_data->>'fingerprint';
 if request is null or fingerprint is null or fingerprint !~ '^[0-9a-f]{64}$' then return jsonb_build_object('error','操作编号无效。');end if;
 -- Serialize duplicate retries before locking the code. No mutation is repeated.
 perform pg_advisory_xact_lock(hashtextextended(request::text,0));
 select * into previous from public.hwt_essay_code_requests where request_id=request;
 if found then
  if previous.fingerprint<>fingerprint or previous.action<>p_action then return jsonb_build_object('error','此操作编号已使用，请刷新后重新操作。','status',409);end if;
  return previous.result;
 end if;
 if p_action in ('create','update') then
  total_n:=(p_data->>'essays_total')::integer;new_n:=(p_data->>'new_essays_total')::integer;
  expiry_s:=p_data->>'expiry';exam_s:=p_data->>'exam_level';
  if total_n is null or total_n<1 or total_n>10000 or new_n is null or new_n<0 or new_n>total_n
   or exam_s is null or exam_s not in ('HCL','O_CL','N_CL') or expiry_s is null
   or (expiry_s<>'' and (expiry_s !~ '^20[0-9]{2}-[0-9]{2}-[0-9]{2}$' or to_char(expiry_s::date,'YYYY-MM-DD')<>expiry_s))
   or p_data->>'note' is null or length(p_data->>'note')>500 then return jsonb_build_object('error','额度、日期、考试段或备注无效。');end if;
 end if;
 if p_action='create' then
  if new_n<1 or expiry_s='' or expiry_s<day_s or jsonb_typeof(p_data->'hashes') is distinct from 'array' then return jsonb_build_object('error','新访问码的额度、有效期或格式无效。');end if;
  if jsonb_array_length(p_data->'hashes') not between 1 and 100 or exists(select 1 from jsonb_array_elements_text(p_data->'hashes') h where h !~ '^[0-9a-f]{64}$')
   or (select count(distinct h) from jsonb_array_elements_text(p_data->'hashes') h)<>jsonb_array_length(p_data->'hashes') then return jsonb_build_object('error','一次只能生成 1 至 100 个不同的访问码。');end if;
  with added as (
   insert into public.access_codes(code_hash,nickname,exam_level,essays_total,essays_used,new_essays_total,new_essays_used,expiry,is_active,note,created_at)
   select h,'',exam_s,total_n,0,new_n,0,expiry_s,1,p_data->>'note',to_char(now() at time zone 'Asia/Singapore','YYYY-MM-DD"T"HH24:MI:SS')||'+08:00'
   from jsonb_array_elements_text(p_data->'hashes') h returning *
  ) select jsonb_build_object('codes',jsonb_agg(to_jsonb(a)-'code_hash' order by h.ordinality)) into result
   from added a join jsonb_array_elements_text(p_data->'hashes') with ordinality h(value,ordinality) on a.code_hash=h.value;
 else
  -- Same row lock as grading completion: editing a cap never resets usage counters.
  select * into c from public.access_codes where id=(p_data->>'id')::integer for update;
  if not found then return jsonb_build_object('error','访问码记录不存在。','status',404);end if;
  if (p_data->>'revision')::integer is distinct from c.admin_revision then return jsonb_build_object('error','记录已被另一页面修改，请关闭详情并重新打开。','status',409);end if;
  if p_action='update' then
   if total_n<coalesce(c.essays_used,0) or (new_n>0 and new_n<coalesce(c.new_essays_used,0)) then return jsonb_build_object('error','额度不能小于已使用的次数，请刷新记录。','status',409);end if;
   if p_data->>'nickname' is null or length(p_data->>'nickname')>100 then return jsonb_build_object('error','使用者称呼过长。');end if;
   update public.access_codes set essays_total=total_n,new_essays_total=new_n,expiry=expiry_s,exam_level=exam_s,nickname=p_data->>'nickname',note=p_data->>'note',admin_revision=admin_revision+1 where id=c.id returning * into c;
  elsif p_action='set_active' then
   if p_data->>'is_active' is null or p_data->>'is_active' not in ('0','1') then return jsonb_build_object('error','状态无效。');end if;
   update public.access_codes set is_active=(p_data->>'is_active')::integer,admin_revision=admin_revision+1 where id=c.id returning * into c;
  else
   if p_data->>'code_hash' is null or p_data->>'code_hash' !~ '^[0-9a-f]{64}$' or p_data->>'code_hash'=c.code_hash then return jsonb_build_object('error','新访问码格式无效或与旧码相同。');end if;
   update public.access_codes set code_hash=p_data->>'code_hash',admin_revision=admin_revision+1 where id=c.id returning * into c;
  end if;
  result:=jsonb_build_object('code',to_jsonb(c)-'code_hash');
 end if;
 insert into public.hwt_essay_code_requests(request_id,fingerprint,action,result) values(request,fingerprint,p_action,result);
 return result;
end;$$;
revoke all on function public.hwt_essay_manage_codes(text,text,jsonb) from public,anon,authenticated;
grant execute on function public.hwt_essay_manage_codes(text,text,jsonb) to service_role;
commit;
