-- The existing essay application uses a server-side psycopg2 Postgres connection.
-- Prevent public PostgREST roles accessing student records; no rows are changed.
-- A database owner/BYPASSRLS role retains its existing server-side access.
alter table public.assignments enable row level security;
alter table public.submissions enable row level security;
alter table public.essay_records enable row level security;
alter table public.error_tags enable row level security;
alter table public.access_codes enable row level security;
alter table public.code_usage_log enable row level security;
alter table public.student_prompts enable row level security;
alter table public.app_settings enable row level security;
