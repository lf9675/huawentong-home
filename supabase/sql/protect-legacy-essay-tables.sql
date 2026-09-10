-- Applied to zuowenpigai (rodtizxezbtlhnuljzsc) on 2026-09-10 with explicit user authorization.
-- Existing Streamlit code uses server-side psycopg2; postgres/service_role access is retained.
-- No records, policies, backend grants, or hwt_* tables are changed.
-- Do not FORCE RLS: the legacy database owner must retain server-side access.
begin;
set local lock_timeout = '5s';
alter table public.assignments enable row level security;
alter table public.submissions enable row level security;
alter table public.essay_records enable row level security;
alter table public.error_tags enable row level security;
alter table public.access_codes enable row level security;
alter table public.code_usage_log enable row level security;
alter table public.student_prompts enable row level security;
alter table public.app_settings enable row level security;
revoke all privileges on table public.assignments,public.submissions,public.essay_records,public.error_tags,public.access_codes,public.code_usage_log,public.student_prompts,public.app_settings from anon,authenticated;
commit;
