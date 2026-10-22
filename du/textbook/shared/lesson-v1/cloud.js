(()=>{'use strict';
const randomId=()=>{const b=crypto.getRandomValues(new Uint8Array(16));b[6]=(b[6]&15)|64;b[8]=(b[8]&63)|128;const h=Array.from(b,x=>x.toString(16).padStart(2,'0')).join('');return h.slice(0,8)+'-'+h.slice(8,12)+'-'+h.slice(12,16)+'-'+h.slice(16,20)+'-'+h.slice(20)};
const L=window.LESSON,engine=window.LessonEngine,c=window.HWTTextbookConnection,endpoint='https://rodtizxezbtlhnuljzsc.supabase.co/functions/v1/hwt-textbook';
const host=document.createElement('section');host.className='paper cloud-collection';host.setAttribute('aria-label','课堂收件');(document.querySelector('main')||document.querySelector('.wrap')).prepend(host);
const make=(tag,text,parent=host)=>{const n=document.createElement(tag);n.textContent=text;parent.append(n);return n};
make('strong','课堂收件');const status=make('p',''),actions=make('div','');actions.className='actions';status.setAttribute('role','status');
if(!c){status.textContent='当前为个人练习，记录保存在本机。课堂作答请打开教师发给你的专属学习链接。';return}
const sync=make('button','立即同步',actions),final=make('button','交齐本课',actions),restore=make('button','从云端恢复',actions),leave=make('button','退出课堂',actions);final.className='primary';restore.hidden=true;
document.body.classList.add('hwt-classroom');const style=document.createElement('style');style.textContent='.hwt-classroom .identity,.hwt-classroom #resetLesson,.hwt-classroom #reset{display:none}.cloud-collection{margin-bottom:20px;padding:16px;background:#fff;border:1px solid #bacfe3;border-radius:12px}.hwt-classroom .idbar,.hwt-classroom #clearAll{display:none}.cloud-collection button{min-height:44px}';document.head.append(style);
const metaKey=window.LESSON_STORAGE_KEY+'-sync',pendingKey=metaKey+'-pending';let meta={},pending=null,connected=false,busy=false,timer=null,dirty=false,disposed=false,finalWanted=false;
try{meta=JSON.parse(localStorage.getItem(metaKey))||{};pending=JSON.parse(localStorage.getItem(pendingKey))}catch{}
const storage=(key,value)=>{try{localStorage.setItem(key,JSON.stringify(value));return true}catch{return false}};
const setStatus=s=>status.textContent=s;
async function call(action,body={}){const ac=new AbortController(),timeout=setTimeout(()=>ac.abort(),20000);try{const r=await fetch(endpoint,{method:'POST',signal:ac.signal,headers:{'Content-Type':'application/json','x-hwt-student':c.token},body:JSON.stringify({action,assignmentId:c.assignmentId,studentId:c.studentId,...body})});const data=await r.json();if(!r.ok)throw Object.assign(new Error(data.error||'同步暂时失败。'),{status:r.status});return data}finally{clearTimeout(timeout)}}
function body(isFinal=false){const s=engine.state();return {lessonId:L.id,contentVersion:L.version,records:L.tasks.filter(t=>s.answers[t.id]?.first).map(t=>{const x=s.answers[t.id];return {taskId:t.id,first:x.first,latest:x.attempts?.at(-1)||x.first,revision:x.revision||'',hintCount:x.hintCount||0}}),readParagraphs:s.cloudReadParagraphs||[],final:isFinal};}
const signature=b=>JSON.stringify({lessonId:b.lessonId,contentVersion:b.contentVersion,records:b.records,readParagraphs:b.readParagraphs});
function applyCloud(data){
 const state=engine.state();const answers={};for(const r of data.responses)answers[r.task_id]={summary:r.latest_answer.summary||'',fields:r.latest_answer.fields,choices:r.latest_answer.choices,evidence:r.latest_answer.evidence,attempts:[{...r.latest_answer,correct:r.latest_result.correct}],hintCount:r.hint_count,revision:r.revision_text,points:[],unlocked:r.latest_result.correct!==false,first:r.first_answer,firstCorrect:r.first_result.correct};
 engine.restore({...state,identity:{name:'',class:data.assignment.className,number:data.student.student_no},answers,cloudReadParagraphs:data.student.read_paragraphs});
 meta={revision:data.student.revision,signature:signature(body()),lastReceived:data.student.last_seen_at,submittedAt:data.student.submitted_at};storage(metaKey,meta);
}
function label(data){if(c.volatile)make('p','本机无法记住课堂身份，请保持页面打开。');make('p',data.assignment.className+' · 学号 '+data.student.student_no+' · '+data.assignment.title);const banner=document.querySelector('.identity-banner');if(banner)banner.hidden=true;}
async function connect(replace=false){
 if(busy)return;busy=true;sync.disabled=final.disabled=true;setStatus('正在连接课堂……');
 try{const data=await call('connect');if(data.assignment.lessonId!==L.id||data.assignment.contentVersion!==L.version)throw Error('课文版本不符，请联系教师。');
 const s=engine.state();if(replace){if(!storage(window.LESSON_STORAGE_KEY+'-before-cloud-restore-'+Date.now(),engine.backup?.()||s))throw Error('本机备份失败，未覆盖本机答案。');applyCloud(data);pending=null;try{localStorage.removeItem(pendingKey)}catch{}}
 else if(!Object.values(s.answers).some(x=>x.first)&&!pending&&data.responses.length)applyCloud(data);
 else if(meta.revision===undefined)meta.revision=data.student.revision;
 else if(meta.revision!==data.student.revision&&!pending){restore.hidden=false;throw Error('另一台设备有更新。点“从云端恢复”继续；当前答案会先留作本机备份。');}
 if(!host.dataset.labelled){label(data);host.dataset.labelled='true'}
 connected=true;restore.hidden=true;storage(metaKey,meta);setStatus('已连接课堂。每次提交题目后自动同步；全部做完再点“交齐本课”。');
 }catch(e){connected=false;setStatus(e.status===410||e.status===403?e.message:'尚未连接：'+e.message+' 本机答案保留。');}finally{busy=false;sync.disabled=false;final.disabled=!connected}
 if(connected)await flush();
}
async function flush(isFinal=false){
 if(isFinal)finalWanted=true;
 if(disposed||!connected||busy){dirty=true;return}const b=body(finalWanted);
 if(finalWanted&&b.records.length!==L.tasks.length){finalWanted=false;setStatus('还有'+(L.tasks.length-b.records.length)+'个步骤未提交，请完成后再交齐。');return}
 if(!pending&&!finalWanted&&signature(b)===meta.signature)return;
 busy=true;dirty=false;sync.disabled=final.disabled=true;
 try{
 if(!pending){pending={...b,baseRevision:meta.revision||0,requestId:randomId()};storage(pendingKey,pending)}
 setStatus('正在同步，请稍候……');const sent=pending,result=await call('submit',pending);if(result.saved!==true)throw Error('未收到保存确认。');
 meta.revision=result.revision;meta.signature=signature(sent);meta.lastReceived=result.receivedAt;if(sent.final)meta.submittedAt=result.receivedAt;
 storage(metaKey,meta);pending=null;try{localStorage.removeItem(pendingKey)}catch{}
 setStatus((sent.final?'本课已交齐，':'已同步，')+'教师已收到（'+new Date(result.receivedAt).toLocaleTimeString('zh-SG')+'）。');
 if(sent.final)finalWanted=false;dirty=signature(body())!==meta.signature||finalWanted;
 }catch(e){setStatus('尚未同步：'+(e.name==='AbortError'?'网络响应超时。':e.message)+' 本机答案保留，联网后可重试。');
 if([401,403,409,410].includes(e.status)){connected=false;restore.hidden=e.status!==409;}
 }finally{busy=false;sync.disabled=false;final.disabled=!connected;if(dirty&&connected)setTimeout(()=>flush(finalWanted),500)}
}
function changed(){if(disposed)return;const s=engine.state();if(s.position.view==='read'){if(engine.recordRead){engine.recordRead(s.position.p)}else{const seen=new Set(s.cloudReadParagraphs||[]);seen.add(s.position.p);s.cloudReadParagraphs=[...seen];try{localStorage.setItem(window.LESSON_STORAGE_KEY,JSON.stringify(s))}catch{}}}
 dirty=true;clearTimeout(timer);timer=setTimeout(()=>flush(),1800);}
sync.onclick=()=>connected?flush():connect();restore.onclick=()=>{if(confirm('将先保留本机备份，再恢复教师已收到的记录。继续吗？'))connect(true)};final.onclick=()=>{if(engine.prepareFinal&&!engine.prepareFinal()){setStatus('请先补齐开放题，再交齐本课。');return}flush(true)};window.addEventListener('hwt:lesson-final',()=>final.onclick());
leave.onclick=()=>{if(!confirm('退出后返回个人练习。课堂记录仍保留；下次需重新打开自己的学习链接。'))return;disposed=true;clearTimeout(timer);try{localStorage.removeItem('hwt-textbook-connection-'+L.id)}catch{}location.replace(location.pathname)};
window.addEventListener('hwt:lesson-saved',changed);window.addEventListener('online',()=>connected?flush():connect());window.addEventListener('focus',()=>{if(!connected)connect();else flush()});
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible'&&connected)flush()});
// Retry while the page remains open. Do not claim background sync after the browser closes.
setInterval(()=>{if(!document.hidden&&connected&&pending&&!busy)flush()},15000);
changed();connect();
})();
