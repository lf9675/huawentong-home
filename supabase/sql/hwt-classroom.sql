-- New learning-sheet records are isolated from the existing essay application.
create table public.hwt_settings (key text primary key, value text not null);
create table public.hwt_sessions (token_hash text primary key, expires_at timestamptz not null);
create table public.hwt_rate_limits (key text primary key, window_start timestamptz not null, hits integer not null);
create table public.hwt_lessons (
 id uuid primary key default gen_random_uuid(), content_hash text not null unique,
 title text not null, mode text not null, input jsonb not null, bank jsonb not null,
 publish_token text not null, created_at timestamptz not null default now()
);
create table public.hwt_attempts (
 id uuid primary key, lesson_id uuid not null references public.hwt_lessons(id),
 class_name text not null, student_no text not null, student_name text not null, group_name text not null,
 records jsonb not null, created_at timestamptz not null default now()
);
create index hwt_attempts_lesson_created on public.hwt_attempts(lesson_id,created_at,id);
alter table public.hwt_settings enable row level security;
alter table public.hwt_sessions enable row level security;
alter table public.hwt_rate_limits enable row level security;
alter table public.hwt_lessons enable row level security;
alter table public.hwt_attempts enable row level security;
revoke all on public.hwt_settings,public.hwt_sessions,public.hwt_rate_limits,public.hwt_lessons,public.hwt_attempts from anon,authenticated;
grant all on public.hwt_settings,public.hwt_sessions,public.hwt_rate_limits,public.hwt_lessons,public.hwt_attempts to service_role;
create function public.hwt_take_rate(bucket text, maximum integer, seconds integer) returns boolean
language plpgsql security definer set search_path = '' as $$
declare n integer;
begin
 insert into public.hwt_rate_limits as r(key,window_start,hits) values(bucket,now(),1)
 on conflict(key) do update set
 hits=case when r.window_start < now()-make_interval(secs=>seconds) then 1 else r.hits+1 end,
 window_start=case when r.window_start < now()-make_interval(secs=>seconds) then now() else r.window_start end
 returning hits into n;
 return n<=maximum;
end $$;
revoke all on function public.hwt_take_rate(text,integer,integer) from public,anon,authenticated;
grant execute on function public.hwt_take_rate(text,integer,integer) to service_role;
