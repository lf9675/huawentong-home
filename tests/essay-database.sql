-- Integration test; all test-only rows are rolled back. Never uses a student code.
begin;
do $$
declare cid int; other_id int; jid uuid:=gen_random_uuid(); token uuid:=gen_random_uuid(); r jsonb; n int;
 h text:=encode(sha256(gen_random_uuid()::text::bytea),'hex'); h2 text:=encode(sha256(gen_random_uuid()::text::bytea),'hex');
begin
 if has_function_privilege('anon','public.hwt_essay_job(text,uuid,text,jsonb)','execute') or has_table_privilege('anon','public.hwt_essay_jobs','select') then raise exception 'anonymous access';end if;
 insert into public.access_codes(code_hash,essays_total,new_essays_total,expiry) values(h,3,2,'2099-01-01') returning id into cid;
 insert into public.access_codes(code_hash,essays_total,new_essays_total,expiry) values(h2,3,2,'2099-01-01') returning id into other_id;
 r:=public.hwt_essay_job(h,jid,'create','{"exam":"HCL","genre":"记叙文","prompt":"数据库事务测试","requirements":"","pageCount":1}');
 if r->>'status'<>'draft' then raise exception 'create failed %',r;end if;
 r:=public.hwt_essay_job(h2,jid,'get');if not r?'error' then raise exception 'cross-owner read';end if;
 r:=public.hwt_essay_job(h,jid,'claim',jsonb_build_object('lease',token));if r?'error' then raise exception 'claim failed';end if;
 r:=public.hwt_essay_job(h,jid,'claim',jsonb_build_object('lease',gen_random_uuid()));if not r?'error' then raise exception 'double lease';end if;
 r:=public.hwt_essay_job(h,jid,'patch',jsonb_build_object('lease',gen_random_uuid(),'patch','{"bad":true}'::jsonb));if not r?'error' then raise exception 'stale write';end if;
 r:=public.hwt_essay_job(h,jid,'patch',jsonb_build_object('lease',token,'patch','{"ocr_0":{"text":"测试"}}'::jsonb));if r?'error' then raise exception 'patch failed';end if;
 r:=public.hwt_essay_job(h,jid,'claim',jsonb_build_object('lease',token));
 r:=public.hwt_essay_job(h,jid,'complete',jsonb_build_object('lease',token,'text','测试','feedback','{"annotations":[]}'::jsonb));if r->>'status'<>'complete' then raise exception 'complete failed %',r;end if;
 r:=public.hwt_essay_job(h,jid,'complete',jsonb_build_object('lease',token,'text','测试','feedback','{}'::jsonb));
 select essays_used into n from public.access_codes where id=cid;if n<>1 then raise exception 'double charge';end if;
 select count(*) into n from public.code_usage_log where code_id=cid;if n<>1 then raise exception 'double usage log';end if;
 select count(*) into n from public.submissions where student_id='AC'||cid;if n<>1 then raise exception 'double submission';end if;
end;$$;
rollback;
