begin;
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
values('hwt-essay-pages','hwt-essay-pages',false,10000000,array['image/jpeg'])
on conflict(id) do nothing;
create table if not exists public.hwt_essay_reviews(
 job_id uuid primary key references public.hwt_essay_jobs(id),
 revision integer not null default 0, annotations jsonb not null default '{}',
 updated_at timestamptz not null default now()
);
create table if not exists public.hwt_essay_lessons(
 id uuid primary key, source_hash text not null, input jsonb not null,
 status text not null default 'draft' check(status in ('draft','generating','complete')),
 result jsonb, lease uuid, lease_until timestamptz,
 created_at timestamptz not null default now(),updated_at timestamptz not null default now()
);
alter table public.hwt_essay_reviews enable row level security;
alter table public.hwt_essay_lessons enable row level security;
revoke all on public.hwt_essay_reviews,public.hwt_essay_lessons from anon,authenticated;
grant select,insert,update on public.hwt_essay_reviews,public.hwt_essay_lessons to service_role;
create or replace function public.hwt_essay_review_save(p_session text,p_job uuid,p_revision integer,p_key text,p_edit jsonb)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare r public.hwt_essay_reviews%rowtype;
begin
 if not exists(select 1 from public.hwt_sessions where token_hash=p_session and expires_at>now()) then return jsonb_build_object('error','教师登录已过期。','status',401);end if;
 if not exists(select 1 from public.hwt_essay_jobs where id=p_job and status='complete') then return jsonb_build_object('error','作文不存在。','status',404);end if;
 insert into public.hwt_essay_reviews(job_id) values(p_job) on conflict do nothing;
 select * into r from public.hwt_essay_reviews where job_id=p_job for update;
 if r.revision<>p_revision then return jsonb_build_object('error','记录已更新，请重新打开作文后再保存。','status',409);end if;
 update public.hwt_essay_reviews set annotations=annotations||jsonb_build_object(p_key,p_edit),revision=revision+1,updated_at=now() where job_id=p_job returning * into r;
 return to_jsonb(r);
end;$$;
create or replace function public.hwt_essay_lesson_claim(p_session text,p_id uuid,p_hash text,p_input jsonb,p_lease uuid)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare r public.hwt_essay_lessons%rowtype;
begin
 if not exists(select 1 from public.hwt_sessions where token_hash=p_session and expires_at>now()) then return jsonb_build_object('error','教师登录已过期。','status',401);end if;
 insert into public.hwt_essay_lessons(id,source_hash,input) values(p_id,p_hash,p_input) on conflict do nothing;
 select * into r from public.hwt_essay_lessons where id=p_id for update;
 if r.source_hash<>p_hash then return jsonb_build_object('error','选材已更新，请重新生成。','status',409);end if;
 if r.status='complete' then return to_jsonb(r);end if;
 if r.lease_until>now() then return jsonb_build_object('error','讲评材料正在生成，请稍后再打开。','status',409);end if;
 update public.hwt_essay_lessons set status='generating',lease=p_lease,lease_until=now()+interval '150 seconds',updated_at=now() where id=p_id returning * into r;
 return to_jsonb(r);
end;$$;
revoke all on function public.hwt_essay_review_save(text,uuid,integer,text,jsonb),public.hwt_essay_lesson_claim(text,uuid,text,jsonb,uuid) from public,anon,authenticated;
grant execute on function public.hwt_essay_review_save(text,uuid,integer,text,jsonb),public.hwt_essay_lesson_claim(text,uuid,text,jsonb,uuid) to service_role;

create or replace function public.hwt_essay_error_counts()
returns table(category text,error_count bigint,essay_count bigint,student_count bigint)
language sql stable security invoker set search_path='' as $$
 select coalesce(nullif(e.value->>'category',''),'其他'),count(*),count(distinct r.job_id),count(distinct j.code_id)
 from public.hwt_essay_reviews r join public.hwt_essay_jobs j on j.id=r.job_id
 cross join lateral jsonb_each(r.annotations) e
 where e.value->>'review_state'='teacher_confirmed' and coalesce(e.value->>'kind','error')<>'praise'
 group by 1 order by 2 desc;
$$;
revoke all on function public.hwt_essay_error_counts() from public,anon,authenticated;
grant execute on function public.hwt_essay_error_counts() to service_role;
commit;
