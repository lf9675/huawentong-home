-- Real database integration checks. Every fixture and mutation is rolled back.
begin;
do $$
declare
 session_s text:=md5(random()::text)||md5(random()::text);
 hash1 text:=md5(random()::text)||md5(random()::text);
 hash2 text:=md5(random()::text)||md5(random()::text);
 hash3 text:=md5(random()::text)||md5(random()::text);
 request uuid:=gen_random_uuid(); data jsonb; r jsonb; again jsonb; code_id integer; before_n integer; c public.access_codes%rowtype;
 job_id uuid:=gen_random_uuid();
begin
 if has_function_privilege('anon','public.hwt_essay_manage_codes(text,text,jsonb)','EXECUTE')
  or has_function_privilege('authenticated','public.hwt_essay_manage_codes(text,text,jsonb)','EXECUTE')
  or has_table_privilege('anon','public.hwt_essay_code_requests','SELECT')
  or has_table_privilege('authenticated','public.access_codes','SELECT')
  or not has_function_privilege('service_role','public.hwt_essay_manage_codes(text,text,jsonb)','EXECUTE') then raise exception 'privilege isolation failed';end if;
 select count(*) into before_n from public.access_codes;
 insert into public.hwt_sessions(token_hash,expires_at) values(session_s,now()+interval '5 minutes');
 data:=jsonb_build_object('request_id',request,'fingerprint',repeat('1',64),'hashes',jsonb_build_array(hash1,hash2),
  'essays_total',8,'new_essays_total',5,'expiry','2099-12-31','exam_level','HCL','note','rollback-only integration fixture');
 -- Exercise actual service-role permissions, not a privileged bypass of the function.
 set local role service_role;
 r:=public.hwt_essay_manage_codes(null,'create',data);
 if r->>'status'<>'401' then raise exception 'anonymous create allowed';end if;
 r:=public.hwt_essay_manage_codes(session_s,'create',data);
 if r ? 'error' or jsonb_array_length(r->'codes')<>2 or (r->'codes'->0) ? 'code_hash' then raise exception 'batch creation failed: %',r;end if;
 code_id:=(r->'codes'->0->>'id')::integer;
 if (select code_hash from public.access_codes where id=code_id)<>hash1 then raise exception 'batch ordering changed';end if;
 again:=public.hwt_essay_manage_codes(session_s,'create',data);
 if again<>r or (select count(*) from public.access_codes)<>before_n+2 then raise exception 'retry created duplicate codes';end if;
 again:=public.hwt_essay_manage_codes(session_s,'create',data||jsonb_build_object('fingerprint',repeat('2',64)));
 if again->>'status'<>'409' then raise exception 'request mutation was accepted';end if;
 -- A collision part-way through a batch must roll back every row in that batch.
 begin
  perform public.hwt_essay_manage_codes(session_s,'create',data||jsonb_build_object('request_id',gen_random_uuid(),'hashes',jsonb_build_array(hash3,hash1)));
  raise exception 'duplicate hash accepted';
 exception when unique_violation then null;end;
 if exists(select 1 from public.access_codes where code_hash=hash3) then raise exception 'partial batch survived';end if;
 -- Simulate usage after the teacher loaded the page, including preserved legacy history.
 update public.access_codes set essays_used=2,new_essays_used=1 where id=code_id;
 insert into public.code_usage_log(code_id,used_at,submission_id) values(code_id,'2026-10-05T12:00:00+08:00',null);
 data:=jsonb_build_object('id',code_id,'revision',0,'request_id',gen_random_uuid(),'fingerprint',repeat('3',64),
  'essays_total',1,'new_essays_total',1,'expiry','2099-12-31','exam_level','HCL','note','updated','nickname','fixture');
 r:=public.hwt_essay_manage_codes(session_s,'update',data);
 if r->>'status'<>'409' then raise exception 'cap below latest usage was accepted';end if;
 data:=data||jsonb_build_object('essays_total',7,'new_essays_total',3,'request_id',gen_random_uuid());
 r:=public.hwt_essay_manage_codes(session_s,'update',data);
 if r ? 'error' or r->'code'->>'essays_used'<>'2' or r->'code'->>'new_essays_used'<>'1' or r->'code'->>'admin_revision'<>'1' then raise exception 'quota edit reset usage';end if;
 again:=public.hwt_essay_manage_codes(session_s,'update',data||jsonb_build_object('request_id',gen_random_uuid()));
 if again->>'status'<>'409' then raise exception 'stale browser overwrote changes';end if;
 r:=public.hwt_essay_manage_codes(session_s,'set_active',jsonb_build_object('id',code_id,'revision',1,'is_active',0,'request_id',gen_random_uuid(),'fingerprint',repeat('4',64)));
 if r->'code'->>'is_active'<>'0' then raise exception 'disable failed';end if;
 again:=public.hwt_essay_job(hash1,job_id,'create','{}');
 if not (again ? 'error') then raise exception 'disabled code can create job';end if;
 r:=public.hwt_essay_manage_codes(session_s,'rotate',jsonb_build_object('id',code_id,'revision',2,'code_hash',hash3,'request_id',gen_random_uuid(),'fingerprint',repeat('5',64)));
 if r ? 'error' or r->'code'->>'id'<>code_id::text or r->'code'->>'is_active'<>'0' or r->'code'->>'essays_used'<>'2' or r->'code'->>'new_essays_total'<>'3' then raise exception 'rotation lost quotas or state';end if;
 if exists(select 1 from public.access_codes where code_hash=hash1) then raise exception 'old code remains valid';end if;
 again:=public.hwt_essay_manage_codes(session_s,'detail',jsonb_build_object('id',code_id));
 if jsonb_array_length(again->'usage')<>1 or (again->'code') ? 'code_hash' then raise exception 'rotation lost history or leaked hash';end if;
 r:=public.hwt_essay_manage_codes(session_s,'set_active',jsonb_build_object('id',code_id,'revision',3,'is_active',1,'request_id',gen_random_uuid(),'fingerprint',repeat('6',64)));
 if r->'code'->>'is_active'<>'1' then raise exception 'enable failed';end if;
 again:=public.hwt_essay_job(hash3,job_id,'create','{}');
 if again ? 'error' then raise exception 'new code rejected by student job: %',again;end if;
 r:=public.hwt_essay_manage_codes(session_s,'list',jsonb_build_object('query_hash',hash3,'page',1,'status','available'));
 if r->>'total'<>'1' or (r->'codes'->0) ? 'code_hash' then raise exception 'search/status failed: %',r;end if;
 r:=public.hwt_essay_manage_codes(session_s,'update',data||jsonb_build_object('request_id',gen_random_uuid(),'revision',4,'new_essays_total',0,'expiry',''));
 if r ? 'error' then raise exception 'legacy shared quota rejected';end if;
 reset role;
 update public.hwt_sessions set expires_at=now()-interval '1 second' where token_hash=session_s;
 r:=public.hwt_essay_manage_codes(session_s,'create',jsonb_build_object('request_id',request,'fingerprint',repeat('1',64)));
 if r->>'status'<>'401' then raise exception 'expired session replay disclosed old result';end if;
end;$$;
rollback;
select 'PASS: authorization, atomic batches, retries, stale edits, quotas, disable/enable, rotation, student compatibility, history, search, legacy settings' as result;
