-- Additive migration. Existing access codes/expiry/quotas are retained.
begin;
create table if not exists public.hwt_essay_jobs (
 id uuid primary key, code_id integer not null references public.access_codes(id),
 created_at timestamptz not null default now(), expires_at timestamptz not null default now()+interval '2 hours',
 status text not null default 'draft' check(status in ('draft','complete','cancelled')),
 input jsonb not null default '{}', result jsonb not null default '{}',
 lease uuid, lease_until timestamptz, submission_id integer
);
create index if not exists hwt_essay_jobs_owner on public.hwt_essay_jobs(code_id,created_at desc);
alter table public.hwt_essay_jobs enable row level security;
revoke all on public.hwt_essay_jobs from anon,authenticated;
grant select,insert,update on public.hwt_essay_jobs to service_role;
-- Only the authenticated edge handler can execute this function. Lock both code and job.
create or replace function public.hwt_essay_job(p_hash text,p_id uuid,p_action text,p_data jsonb default '{}')
returns jsonb language plpgsql security invoker set search_path='' as $$
declare c public.access_codes%rowtype; j public.hwt_essay_jobs%rowtype;
 day_s text:=to_char(now() at time zone 'Asia/Singapore','YYYY-MM-DD'); used_today int; active_jobs int; a_id int; s_id int;
begin
 select * into c from public.access_codes where code_hash=p_hash for update;
 if not found or c.is_active is distinct from 1 then return jsonb_build_object('error','访问码无效或已停用。'); end if;
 if c.expiry is not null and c.expiry<>'' and c.expiry<day_s then return jsonb_build_object('error','访问码已过期，请联系老师。'); end if;
 select * into j from public.hwt_essay_jobs where id=p_id and code_id=c.id for update;
 if p_action='create' and j.id is null then
  select count(*) into used_today from public.code_usage_log where code_id=c.id and used_at like day_s||'%';
  select count(*) into active_jobs from public.hwt_essay_jobs where code_id=c.id and status='draft' and expires_at>now();
  if active_jobs>0 then return jsonb_build_object('error','有一份作文尚未完成，请恢复该次批改或取消后重试。'); end if;
  if c.essays_used>=c.essays_total or (coalesce(c.new_essays_total,0)>0 and coalesce(c.new_essays_used,0)>=c.new_essays_total) or used_today>=5 then
   return jsonb_build_object('error','新作文额度、总次数或今日五次额度已用完。'); end if;
  insert into public.hwt_essay_jobs(id,code_id,input) values(p_id,c.id,p_data) returning * into j;
 elsif j.id is null then return jsonb_build_object('error','批改记录不存在。');
 elsif p_action='cancel' and j.status='draft' then
  if j.lease_until>now() then return jsonb_build_object('error','正在处理，请稍后再取消。');end if;
  update public.hwt_essay_jobs set status='cancelled' where id=j.id returning * into j;
 elsif p_action not in ('get','create') then
  if j.status='complete' then return to_jsonb(j)-'code_id'-'lease';end if;
  if j.status<>'draft' or j.expires_at<now() then return jsonb_build_object('error','本次批改已结束或超时，请重新上传。');end if;
  if p_action='claim' then
   if j.lease_until>now() then return jsonb_build_object('error','仍在处理，请稍后重试。');end if;
   update public.hwt_essay_jobs set lease=(p_data->>'lease')::uuid,lease_until=now()+interval '150 seconds' where id=j.id returning * into j;
  elsif p_action in ('patch','release','complete') then
   if j.lease is null or j.lease<>(p_data->>'lease')::uuid then return jsonb_build_object('error','处理状态已改变，请刷新重试。');end if;
   if p_action='complete' then
    if c.essays_used>=c.essays_total or (coalesce(c.new_essays_total,0)>0 and coalesce(c.new_essays_used,0)>=c.new_essays_total) then return jsonb_build_object('error','额度已用完。');end if;
    select count(*) into used_today from public.code_usage_log where code_id=c.id and used_at like day_s||'%';
    if used_today>=5 then return jsonb_build_object('error','今日批改额度已用完。');end if;
    insert into public.assignments(title,exam_level,genre,prompt,requirements,created_at,is_active)
     values('华文通照片批改',j.input->>'exam',j.input->>'genre',j.input->>'prompt',j.input->>'requirements',now()::text,0) returning id into a_id;
    insert into public.submissions(assignment_id,student_id,student_name,submitted_at,ocr_text,feedback_json)
     values(a_id,'AC'||c.id,coalesce(nullif(c.nickname,''),'同学'),now()::text,p_data->>'text',(p_data->'feedback')::text) returning id into s_id;
    insert into public.code_usage_log(code_id,used_at,submission_id) values(c.id,day_s||'T'||to_char(now() at time zone 'Asia/Singapore','HH24:MI:SS')||'+08:00',s_id);
    update public.access_codes set essays_used=coalesce(essays_used,0)+1,new_essays_used=coalesce(new_essays_used,0)+1 where id=c.id;
    update public.hwt_essay_jobs set status='complete',submission_id=s_id,result=result||jsonb_build_object('feedback',p_data->'feedback'),lease=null,lease_until=null where id=j.id returning * into j;
   else
    update public.hwt_essay_jobs set result=result||coalesce(p_data->'patch','{}'),lease=null,lease_until=null where id=j.id returning * into j;
   end if;
  else return jsonb_build_object('error','未知操作。');end if;
 end if;
 return to_jsonb(j)-'code_id'-'lease';
end;$$;
revoke all on function public.hwt_essay_job(text,uuid,text,jsonb) from public,anon,authenticated;
grant execute on function public.hwt_essay_job(text,uuid,text,jsonb) to service_role;
commit;
