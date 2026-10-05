import {freshCodes,csv,statusOf,remaining} from './teacher-core.mjs';
const $=id=>document.getElementById(id);
const endpoint='https://rodtizxezbtlhnuljzsc.supabase.co/functions/v1/';
const studentURL=new URL('./',location.href).href;
const sessionKey='hwt_teacher_session';
let token=sessionStorage.getItem(sessionKey)||'',busy=false,page=1,total=0,today=sgDay(),selected=null,pending=null,issued=[],unsaved=false,query='',filter='all';
const escape=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function sgDay(){return new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Singapore',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());}
function say(message,error=false){for(const id of ['message','detailMessage']){$(id).textContent=message;$(id).classList.toggle('error',error);}}
function locked(){ $('generateFields').disabled=!!pending||issued.length>0; $('editFields').disabled=!!pending; $('pendingPanel').hidden=!pending; $('toggleActive').disabled=!!pending;$('rotateCode').disabled=!!pending; }
function showLogin(){ $('workspace').hidden=true;$('teacherLogin').hidden=false;if($('detailDialog').open)$('detailDialog').close(); }
async function api(service,action,data={}){
  let response;
  try{response=await fetch(endpoint+service,{method:'POST',headers:{'Content-Type':'application/json',...(token?{'x-hwt-session':token}:{})},body:JSON.stringify({action,...data}),signal:AbortSignal.timeout(25000)});}catch{throw Object.assign(Error('连接中断，尚未收到操作结果。请保留此页重试。'),{uncertain:true});}
  const result=await response.json().catch(()=>null);
  if(!response.ok||!result){const error=Object.assign(Error(result?.error||'服务响应不完整，请重试。'),{status:response.status,uncertain:response.status>=500||!result});
    if(response.status===401&&service==='hwt-essay-admin'){token='';sessionStorage.removeItem(sessionKey);showLogin();}
    throw error;
  }
  return result;
}
async function run(fn){if(busy)return;busy=true;document.body.setAttribute('aria-busy','true');$('workspace').setAttribute('aria-busy','true');try{await fn();}catch(error){say(error.message,true);}finally{busy=false;document.body.removeAttribute('aria-busy');$('workspace').removeAttribute('aria-busy');locked();}}
async function list(){
  const data=await api('hwt-essay-admin','list',{query,status:filter,page});total=data.total;today=data.today;
  if(page>1&&(page-1)*30>=total){page=Math.max(1,Math.ceil(total/30));return list();}
  $('listSummary').textContent=`找到 ${total} 个访问码 · 状态截至 ${today}（新加坡时间）`;
  $('codeRows').innerHTML=data.codes.length?data.codes.map(c=>{const [status,cls]=statusOf(c,today);return `<tr><td class="name"><b>#${c.id}</b><br>${escape(c.nickname||'未填写称呼')}</td><td><span class="badge ${cls}">${status}</span></td><td>${c.new_essays_used||0} / ${c.new_essays_total>0?c.new_essays_total:'共用总次数'}</td><td>${c.essays_used||0} / ${c.essays_total}</td><td>${escape(c.exam_level)}</td><td>${escape(c.expiry||'不限期')}</td><td class="note">${escape(c.note||'—')}</td><td><button class="quiet" data-manage="${c.id}">管理</button></td></tr>`;}).join(''):'<tr><td colspan="8">没有符合条件的访问码。</td></tr>';
  $('pageLabel').textContent=`第 ${page} / ${Math.max(1,Math.ceil(total/30))} 页`;
  $('previousPage').disabled=page<=1;$('nextPage').disabled=page*30>=total;
}
async function enter(){await list();$('teacherLogin').hidden=true;$('workspace').hidden=false;say('已连接原有访问码数据，可以发码和管理。');}
function renderDetail(data){selected=data.code;const c=selected;
  $('detailTitle').textContent='管理访问码 #'+c.id;
  $('detailSummary').textContent=`${statusOf(c,today)[0]} · 已用总次数 ${c.essays_used||0} / ${c.essays_total} · 已用新作文 ${c.new_essays_used||0} / ${c.new_essays_total>0?c.new_essays_total:'共用总次数'}`;
  for(const [field,key] of [['Nickname','nickname'],['Exam','exam_level'],['New','new_essays_total'],['Total','essays_total'],['Expiry','expiry'],['Note','note']])$('edit'+field).value=c[key]??'';
  $('toggleActive').textContent=c.is_active===1?'停用此码':'启用此码';$('rotateConfirm').hidden=true;$('detailMessage').textContent='';
  $('usageSummary').textContent=data.usage.length?'只显示最近 20 次；更换访问码后，历史记录继续保留。':'尚无使用记录。';
  $('usageRows').innerHTML=data.usage.map(v=>`<tr><td>${escape(time(v.used_at))}</td><td>${escape(v.submission_id??'—')}</td></tr>`).join('');locked();
}
function time(s){const d=new Date(s);return Number.isNaN(+d)?s:new Intl.DateTimeFormat('zh-SG',{timeZone:'Asia/Singapore',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}).format(d);}
async function detail(id){const result=await api('hwt-essay-admin','detail',{id});renderDetail(result);if(!$('detailDialog').open)$('detailDialog').showModal();}
function createSettings(){return {essays_total:Number($('createTotal').value),new_essays_total:Number($('createNew').value),expiry:$('createExpiry').value,exam_level:$('createExam').value,note:$('createNote').value};}
function showIssued(rows,codes,rotated){
  issued=rows.map((row,i)=>({...row,plaintext:codes[i]}));unsaved=true;
  $('issuedPanel').hidden=false;$('issuedNote').textContent=rotated?'新访问码已生效；旧码已失效。若原记录已停用、过期或额度用完，仍需在管理中调整。':`已生成 ${issued.length} 个访问码。可用 CSV 保存完整记录，再将访问码逐一发给学生。`;
  $('issuedRows').innerHTML=issued.map(c=>{const left=remaining(c);return `<tr><td>#${c.id}</td><td class="mono">${escape(c.plaintext)}</td><td>${left.fresh}</td><td>${left.total}</td><td>${escape(c.expiry||'不限期')}</td><td class="note">${escape(c.note||'—')}</td></tr>`;}).join('');
  $('issuedPanel').scrollIntoView({behavior:'smooth',block:'start'});
}
async function mutate(action,data){
  if(pending)throw Error('请先重试并完成上一项操作。');
  if((action==='create'||action==='rotate')&&issued.length)throw Error('请先保存并关闭上一批访问码清单。');
  pending={action,data:{...data,request_id:crypto.randomUUID()}};locked();await retryMutation();
}
async function retryMutation(){
  if(!pending)return;const operation=pending;let result;
  say('正在保存，请稍候……');
  try{result=await api('hwt-essay-admin',operation.action,operation.data);}
  catch(error){if(!error.uncertain&&error.status!==401&&error.status!==429)pending=null;locked();if($('detailDialog').open&&pending)$('detailDialog').close();throw error;}
  pending=null;locked();
  if(operation.action==='create'){showIssued(result.codes,operation.data.codes,false);query='';filter='all';page=1;$('searchQuery').value='';$('statusFilter').value='all';}
  if(operation.action==='rotate'){if($('detailDialog').open)$('detailDialog').close();showIssued([result.code],[operation.data.code],true);}
  let refreshError='';
  try{await list();if(['update','set_active'].includes(operation.action))await detail(result.code.id);}catch{refreshError=' 列表未刷新，请点击“查询／刷新”；保存已经成功。';}
  say((operation.action==='create'?'访问码已生成，请先下载保存。':operation.action==='rotate'?'访问码已更换，请保存新码。':'调整已保存。')+refreshError);
}
async function copy(text){try{await navigator.clipboard.writeText(text);}catch{throw Error('浏览器未允许复制，请下载 CSV，或手动选择需要的内容。');}}
function download(){const headers=['编号','访问码','新作文额度','新作文已用','新作文剩余','总次数(含重交)','总次数已用','总次数剩余','有效期至','考试段','备注','学生网址'];const rows=issued.map(c=>[c.id,c.plaintext,c.new_essays_total||'共用总次数',c.new_essays_used||0,remaining(c).fresh,c.essays_total,c.essays_used||0,remaining(c).total,c.expiry||'不限期',c.exam_level,c.note,studentURL]);const url=URL.createObjectURL(new Blob([csv([headers,...rows])],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='华文通作文访问码-'+today+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);say('CSV 已开始下载，请确认文件已保存。');}
$('teacherLoginForm').addEventListener('submit',event=>{event.preventDefault();run(async()=>{say('正在验证教师密码……');const data=await api('hwt-classroom','login',{password:$('teacherPassword').value});token=data.token;sessionStorage.setItem(sessionKey,token);sessionStorage.setItem('hwt_teacher_auth','1');$('teacherPassword').value='';await enter();});});
$('teacherLogout').onclick=()=>run(async()=>{
  if(pending)throw Error('请先重试并确认上一项操作，再退出。');
  if(issued.length)throw Error('请先保存访问码，并点击“已保存，关闭清单”。');
  await api('hwt-classroom','logout');token='';sessionStorage.removeItem(sessionKey);sessionStorage.removeItem('hwt_teacher_auth');$('codeRows').replaceChildren();$('usageRows').replaceChildren();selected=null;showLogin();say('已退出教师登录。');
});
$('generateForm').addEventListener('submit',event=>{event.preventDefault();run(async()=>{const data=createSettings();if(data.new_essays_total>data.essays_total)throw Error('新作文额度不能超过总次数。');await mutate('create',{...data,codes:freshCodes(Number($('createCount').value))});});});
$('searchForm').addEventListener('submit',event=>{event.preventDefault();run(async()=>{query=$('searchQuery').value.trim();filter=$('statusFilter').value;page=1;await list();say('访问码列表已刷新。');});});
$('previousPage').onclick=()=>run(async()=>{if(page>1){page--;await list();}});
$('nextPage').onclick=()=>run(async()=>{if(page*30<total){page++;await list();}});
$('codeRows').onclick=event=>{const button=event.target.closest('[data-manage]');if(button)run(()=>detail(Number(button.dataset.manage)));};
$('closeDetail').onclick=()=>{if(!busy)$('detailDialog').close();};
$('detailDialog').addEventListener('cancel',event=>{if(busy)event.preventDefault();});
$('editForm').addEventListener('submit',event=>{event.preventDefault();run(()=>mutate('update',{id:selected.id,revision:selected.admin_revision,essays_total:Number($('editTotal').value),new_essays_total:Number($('editNew').value),expiry:$('editExpiry').value,exam_level:$('editExam').value,nickname:$('editNickname').value,note:$('editNote').value}));});
$('toggleActive').onclick=()=>run(()=>mutate('set_active',{id:selected.id,revision:selected.admin_revision,is_active:selected.is_active===1?0:1}));
$('rotateCode').onclick=()=>{if(issued.length){say('请先保存并关闭上一批访问码清单。',true);return;}$('rotateConfirm').hidden=false;};
$('cancelRotate').onclick=()=>{$('rotateConfirm').hidden=true;};
$('confirmRotate').onclick=()=>run(()=>mutate('rotate',{id:selected.id,revision:selected.admin_revision,code:freshCodes(1)[0]}));
$('retryPending').onclick=()=>run(async()=>{if(!token){showLogin();throw Error('请重新登录，再点击重试；原操作会保留在此页。');}await retryMutation();});
$('downloadCodes').onclick=()=>download();
$('copyCodes').onclick=()=>run(async()=>{await copy(issued.map(c=>`${c.id}\t${c.plaintext}`).join('\n'));say('访问码已复制，请粘贴到安全的位置保存。');});
$('copyStudentLink').onclick=()=>run(async()=>{await copy(studentURL);say('学生网址已复制。');});
$('dismissIssued').onclick=()=>{issued=[];unsaved=false;$('issuedRows').replaceChildren();$('issuedPanel').hidden=true;locked();say('清单已关闭。已生成的访问码仍可在列表中管理。');};
window.addEventListener('beforeunload',event=>{if(unsaved||pending){event.preventDefault();event.returnValue='';}});
const defaultExpiry=new Date(today+'T00:00:00Z');defaultExpiry.setUTCDate(defaultExpiry.getUTCDate()+30);$('createExpiry').value=defaultExpiry.toISOString().slice(0,10);$('createExpiry').min=today;
if(token)run(enter);else{showLogin();say('请用现有的华文通教师密码登录。');}
