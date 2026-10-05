import {fail,digest,SESSION_RE,normalize} from './core.mjs';
const ORIGINS = new Set(['https://huawentong-home.lyqlym2015.workers.dev','https://huawentong-home.pages.dev','http://localhost:4173','http://127.0.0.1:4173']);
const secret = (key:string) => Deno.env.get(key)?.trim();
async function db(path:string,body?:unknown) {
  const key=secret('SUPABASE_SERVICE_ROLE_KEY'),url=secret('SUPABASE_URL');
  if(!key||!url)fail('管理服务尚未配置。',503);
  const response=await fetch(url+'/rest/v1/'+path,{method:body===undefined?'GET':'POST',headers:{apikey:key!,Authorization:'Bearer '+key,'Content-Type':'application/json'},...(body===undefined?{}:{body:JSON.stringify(body)}),signal:AbortSignal.timeout(15000)});
  if(!response.ok) {
    const error=await response.json().catch(()=>({}));
    if(error.code==='23505')fail('访问码重复，未保存。请重新生成。',409);
    fail('数据库暂时不可用；请重试同一次操作。',503);
  }
  return response.json();
}
// Gateway JWT verification is disabled only because every action requires the
// existing, expiring hwt-classroom teacher session. A student code grants no access.
export async function handle(req:Request) {
  const origin=req.headers.get('origin')||'';
  const headers:Record<string,string>={'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','Vary':'Origin','Access-Control-Allow-Headers':'content-type,x-hwt-session','Access-Control-Allow-Methods':'POST,OPTIONS'};
  if(ORIGINS.has(origin))headers['Access-Control-Allow-Origin']=origin;
  try {
    if(origin&&!ORIGINS.has(origin))fail('此网页无权访问管理服务。',403);
    if(req.method==='OPTIONS')return new Response(null,{status:204,headers});
    if(req.method!=='POST')fail('请使用 POST。',405);
    const token=req.headers.get('x-hwt-session')||'';
    if(!SESSION_RE.test(token))fail('请先用华文通教师密码登录。',401);
    const session=await digest(token);
    const sessions=await db('hwt_sessions?token_hash=eq.'+session+'&expires_at=gt.'+encodeURIComponent(new Date().toISOString())+'&select=expires_at');
    if(!sessions.length)fail('教师登录已过期，请重新登录。',401);
    const raw=await req.text();if(raw.length>40000)fail('提交资料过多。',413);
    let b:any;try{b=JSON.parse(raw);}catch{fail('资料格式不正确。');}
    if(!b||typeof b!=='object'||Array.isArray(b)||typeof b.action!=='string')fail('缺少操作。');
    const data=await normalize(b.action,b);
    if(!await db('rpc/hwt_take_rate',{bucket:'essay-admin-'+session,maximum:240,seconds:900}))fail('操作过于频繁，请稍后重试。',429);
    const result=await db('rpc/hwt_essay_manage_codes',{p_session:session,p_action:b.action,p_data:data});
    if(result.error)fail(result.error,result.status||400);
    return Response.json(result,{headers});
  }catch(error:any){const status=Number.isInteger(error.status)?error.status:503;return Response.json({error:status===503?'管理服务暂时不可用；请保留此页并重试同一次操作。':error.message},{status,headers});}
}
Deno.serve(handle);
