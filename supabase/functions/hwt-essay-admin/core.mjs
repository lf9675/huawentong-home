export const CODE_RE = /^HW-[A-Z2-9]{4}-[A-Z2-9]{4}$/;
export const SESSION_RE = /^[0-9a-f]{64}$/;
export const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
export function fail(message, status = 400) { throw Object.assign(new Error(message), {status}); }
export async function digest(value) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value)))].map(v => v.toString(16).padStart(2, '0')).join('');
}
const integer = (v, min, max, label) => { if (!Number.isInteger(v) || v < min || v > max) fail(label + '超出范围。'); return v; };
const text = (v, max, label) => { if (typeof v !== 'string' || v.length > max) fail(label + '过长或格式不正确。'); return v.trim(); };
const date = v => {
  if (v === '') return v;
  if (typeof v !== 'string' || !/^20\d\d-\d{2}-\d{2}$/.test(v) || Number.isNaN(Date.parse(v)) || new Date(v).toISOString().slice(0,10) !== v) fail('请选择有效的到期日期。');
  return v;
};
export const singaporeDay = () => new Intl.DateTimeFormat('en-CA', {timeZone:'Asia/Singapore',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
function settings(b, create) {
  const result = {essays_total:integer(b.essays_total,1,10000,'总次数'),new_essays_total:integer(b.new_essays_total,create?1:0,10000,'新作文额度'),expiry:date(b.expiry),exam_level:b.exam_level,note:text(b.note,500,'备注')};
  if (!['HCL','O_CL','N_CL'].includes(result.exam_level)) fail('考试段无效。');
  if (result.new_essays_total > result.essays_total) fail('新作文额度不能超过总次数。');
  if (create && (!result.expiry || result.expiry < singaporeDay())) fail('新访问码的有效期不能早于今天（新加坡时间）。');
  if (!create) result.nickname = text(b.nickname,100,'使用者称呼');
  return result;
}
// Never forward raw passwords, session tokens, or plaintext access codes to the database.
export async function normalize(action, b) {
  if (action === 'list') {
    const query = text(b.query ?? '',100,'搜索内容');
    const status = b.status ?? 'all';
    if (!['all','available','disabled','expired','exhausted'].includes(status)) fail('筛选条件无效。');
    return {query:CODE_RE.test(query.toUpperCase())?'':query,query_hash:CODE_RE.test(query.toUpperCase())?await digest(query.toUpperCase()):'',status,page:integer(b.page??1,1,100000,'页码')};
  }
  if (action === 'detail') return {id:integer(b.id,1,2147483647,'访问码编号')};
  if (!['create','update','set_active','rotate'].includes(action)) fail('未知操作。');
  if (!UUID_RE.test(b.request_id || '')) fail('缺少操作编号，请刷新重试。');
  let data;
  if (action === 'create') {
    if (!Array.isArray(b.codes) || b.codes.length < 1 || b.codes.length > 100 || b.codes.some(c=>typeof c!=='string'||!CODE_RE.test(c)) || new Set(b.codes).size !== b.codes.length) fail('一次只能生成 1 至 100 个不同的访问码。');
    data = {...settings(b,true),hashes:await Promise.all(b.codes.map(digest))};
  } else {
    data = {id:integer(b.id,1,2147483647,'访问码编号'),revision:integer(b.revision,0,2147483647,'记录版本')};
    if (action === 'update') Object.assign(data,settings(b,false));
    if (action === 'set_active') data.is_active = integer(b.is_active,0,1,'状态');
    if (action === 'rotate') { if (!CODE_RE.test(b.code||'')) fail('访问码格式无效。'); data.code_hash = await digest(b.code); }
  }
  return {...data,request_id:b.request_id,fingerprint:await digest(JSON.stringify({action,...data}))};
}
