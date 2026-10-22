-- Additive textbook collection schema. Existing hwt_* records are untouched.
create table public.hwt_tb_assignments (
 id uuid primary key, class_name text not null check(length(class_name) between 1 and 60),
 lesson_id text not null, content_version text not null, lesson jsonb not null,
 is_open boolean not null default true, expires_at timestamptz not null,
 created_at timestamptz not null default now(), closed_at timestamptz
);
create table public.hwt_tb_students (
 id uuid primary key, assignment_id uuid not null references public.hwt_tb_assignments(id),
 student_no text not null check(length(student_no) between 1 and 30),
 token_hash text not null check(token_hash ~ '^[a-f0-9]{64}$'),
 revision integer not null default 0, last_seen_at timestamptz,
 submitted_at timestamptz, read_paragraphs jsonb not null default '[]',
 unique(assignment_id, student_no)
);
create table public.hwt_tb_receipts (
 request_id uuid primary key, student_id uuid not null references public.hwt_tb_students(id),
 payload_hash text not null, revision integer not null, payload jsonb not null,
 created_at timestamptz not null default now()
);
create index hwt_tb_receipts_student on public.hwt_tb_receipts(student_id, created_at);
create table public.hwt_tb_responses (
 student_id uuid not null references public.hwt_tb_students(id), task_id text not null,
 first_answer jsonb not null, first_result jsonb not null,
 latest_answer jsonb not null, latest_result jsonb not null,
 revision_text text not null default '', hint_count integer not null default 0,
 first_received_at timestamptz not null default now(), updated_at timestamptz not null default now(),
 primary key(student_id,task_id)
);
create table public.hwt_tb_reviews (
 student_id uuid not null, task_id text not null,
 verdict text not null check(verdict in ('达到','部分达到','需帮助')),
 note text not null check(length(note)<=2000), revision integer not null,
 reviewed_at timestamptz not null default now(),
 primary key(student_id,task_id),
 foreign key(student_id,task_id) references public.hwt_tb_responses(student_id,task_id)
);
alter table public.hwt_tb_assignments enable row level security;
alter table public.hwt_tb_students enable row level security;
alter table public.hwt_tb_receipts enable row level security;
alter table public.hwt_tb_responses enable row level security;
alter table public.hwt_tb_reviews enable row level security;
revoke all on public.hwt_tb_assignments,public.hwt_tb_students,public.hwt_tb_receipts,public.hwt_tb_responses,public.hwt_tb_reviews from public,anon,authenticated;
grant all on public.hwt_tb_assignments,public.hwt_tb_students,public.hwt_tb_receipts,public.hwt_tb_responses,public.hwt_tb_reviews to service_role;

-- Transactional creation: never expose a half-created roster. Only the authenticated edge service invokes this.
create function public.hwt_tb_create(p_assignment jsonb,p_students jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare s jsonb;
begin
 insert into public.hwt_tb_assignments(id,class_name,lesson_id,content_version,lesson,expires_at)
 values((p_assignment->>'id')::uuid,p_assignment->>'class_name',p_assignment->>'lesson_id',p_assignment->>'content_version',p_assignment->'lesson',(p_assignment->>'expires_at')::timestamptz);
 for s in select * from jsonb_array_elements(p_students) loop
 insert into public.hwt_tb_students(id,assignment_id,student_no,token_hash) values((s->>'id')::uuid,(p_assignment->>'id')::uuid,s->>'student_no',s->>'token_hash');
 end loop;
 return jsonb_build_object('saved',true,'id',p_assignment->>'id');
end $$;

-- Lock one learner, acknowledge retries, and preserve first answers atomically.
create function public.hwt_tb_submit(p_student uuid,p_token_hash text,p_request uuid,p_hash text,p_base integer,p_payload jsonb) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare s public.hwt_tb_students; a public.hwt_tb_assignments; prior public.hwt_tb_receipts; r jsonb; n integer;
begin
 select * into s from public.hwt_tb_students where id=p_student for update;
 if not found or s.token_hash<>p_token_hash then return jsonb_build_object('error','unauthorized'); end if;
 select * into a from public.hwt_tb_assignments where id=s.assignment_id for share;
 select * into prior from public.hwt_tb_receipts where request_id=p_request;
 if found then
   if prior.student_id<>p_student or prior.payload_hash<>p_hash then return jsonb_build_object('error','request_conflict'); end if;
   return jsonb_build_object('saved',true,'revision',prior.revision,'receivedAt',prior.created_at,'duplicate',true);
 end if;
 if not a.is_open or a.expires_at<now() then return jsonb_build_object('error','closed'); end if;
 if s.revision<>p_base then return jsonb_build_object('error','revision_conflict','revision',s.revision); end if;
 for r in select * from jsonb_array_elements(p_payload->'records') loop
 insert into public.hwt_tb_responses as old(student_id,task_id,first_answer,first_result,latest_answer,latest_result,revision_text,hint_count)
 values(p_student,r->>'taskId',r->'first',r->'firstResult',r->'latest',r->'latestResult',r->>'revision',(r->>'hintCount')::integer)
 on conflict(student_id,task_id) do update set latest_answer=excluded.latest_answer,latest_result=excluded.latest_result,revision_text=excluded.revision_text,hint_count=greatest(old.hint_count,excluded.hint_count),updated_at=now();
 end loop;
 select count(*) into n from public.hwt_tb_responses where student_id=p_student;
 if (p_payload->>'final')::boolean and n<>jsonb_array_length(a.lesson->'tasks') then raise exception 'incomplete final submission'; end if;
 update public.hwt_tb_students set revision=revision+1,last_seen_at=now(),
 read_paragraphs=(select coalesce(jsonb_agg(v),'[]'::jsonb) from (select distinct v from jsonb_array_elements(s.read_paragraphs||(p_payload->'readParagraphs')) as x(v)) as merged),
 submitted_at=case when (p_payload->>'final')::boolean then now() else submitted_at end where id=p_student;
 insert into public.hwt_tb_receipts(request_id,student_id,payload_hash,revision,payload) values(p_request,p_student,p_hash,s.revision+1,p_payload);
 return jsonb_build_object('saved',true,'revision',s.revision+1,'receivedAt',now(),'duplicate',false);
end $$;

create function public.hwt_tb_review(p_student uuid,p_task text,p_verdict text,p_note text,p_base integer) returns jsonb
language plpgsql security invoker set search_path='' as $$
declare old public.hwt_tb_reviews; s public.hwt_tb_students; l jsonb;
begin
 select * into s from public.hwt_tb_students where id=p_student for update;
 select lesson into l from public.hwt_tb_assignments where id=s.assignment_id;
 if not exists(select 1 from jsonb_array_elements(l->'tasks') t where t->>'id'=p_task and t->>'mode'='written') then raise exception 'not a written task'; end if;
 select * into old from public.hwt_tb_reviews where student_id=p_student and task_id=p_task;
 if coalesce(old.revision,0)<>p_base then return jsonb_build_object('error','review_conflict'); end if;
 insert into public.hwt_tb_reviews(student_id,task_id,verdict,note,revision) values(p_student,p_task,p_verdict,p_note,p_base+1)
 on conflict(student_id,task_id) do update set verdict=excluded.verdict,note=excluded.note,revision=excluded.revision,reviewed_at=now();
 return jsonb_build_object('saved',true,'revision',p_base+1);
end $$;
revoke all on function public.hwt_tb_create(jsonb,jsonb),public.hwt_tb_submit(uuid,text,uuid,text,integer,jsonb),public.hwt_tb_review(uuid,text,text,text,integer) from public,anon,authenticated;
grant execute on function public.hwt_tb_create(jsonb,jsonb),public.hwt_tb_submit(uuid,text,uuid,text,integer,jsonb),public.hwt_tb_review(uuid,text,text,text,integer) to service_role;
