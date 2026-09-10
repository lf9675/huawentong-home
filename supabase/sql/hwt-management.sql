-- Teacher review and per-lesson class lists; original answers are immutable.
begin;
create unique index hwt_attempts_id_lesson on public.hwt_attempts(id,lesson_id);
create table public.hwt_reviews (
 attempt_id uuid not null, lesson_id uuid not null, question_id text not null,
 score integer not null check(score between 0 and 5), feedback text not null default '' check(length(feedback)<=2000),
 revision integer not null default 1, reviewed_at timestamptz not null default now(),
 primary key(attempt_id,question_id),
 foreign key(attempt_id,lesson_id) references public.hwt_attempts(id,lesson_id)
);
create index hwt_reviews_lesson on public.hwt_reviews(lesson_id,attempt_id,question_id);
create table public.hwt_rosters (
 lesson_id uuid not null references public.hwt_lessons(id), class_name text not null,
 students jsonb not null check(jsonb_typeof(students)='array' and jsonb_array_length(students)<=300),
 updated_at timestamptz not null default now(), primary key(lesson_id,class_name)
);
alter table public.hwt_reviews enable row level security;
alter table public.hwt_rosters enable row level security;
revoke all on public.hwt_reviews,public.hwt_rosters from public,anon,authenticated;
grant all on public.hwt_reviews,public.hwt_rosters to service_role;
create function public.hwt_save_review(p_attempt uuid,p_question text,p_score integer,p_feedback text,p_revision integer)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare l uuid; maximum integer; saved public.hwt_reviews;
begin
 select a.lesson_id,(q->>'points')::integer into l,maximum
 from public.hwt_attempts a join public.hwt_lessons b on b.id=a.lesson_id
 cross join lateral jsonb_array_elements(b.bank->'questions') q
 where a.id=p_attempt and q->>'id'=p_question and q->>'type'='open';
 if l is null or p_score is null or p_score<0 or p_score>maximum or p_revision is null or p_revision<0 or p_feedback is null or length(p_feedback)>2000 then
  raise exception 'Invalid review';
 end if;
 if p_revision=0 then
  insert into public.hwt_reviews(attempt_id,lesson_id,question_id,score,feedback)
  values(p_attempt,l,p_question,p_score,p_feedback) on conflict do nothing returning * into saved;
 else
  update public.hwt_reviews set score=p_score,feedback=p_feedback,revision=revision+1,reviewed_at=now()
  where attempt_id=p_attempt and question_id=p_question and revision=p_revision returning * into saved;
 end if;
 if saved.attempt_id is null then
  select * into saved from public.hwt_reviews where attempt_id=p_attempt and question_id=p_question;
  if saved.score is distinct from p_score or saved.feedback is distinct from p_feedback then
   return jsonb_build_object('conflict',true);
  end if;
 end if;
 return to_jsonb(saved);
end $$;
revoke all on function public.hwt_save_review(uuid,text,integer,text,integer) from public,anon,authenticated;
grant execute on function public.hwt_save_review(uuid,text,integer,text,integer) to service_role;
commit;
