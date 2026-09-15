// Activated only after the dedicated Google receiver has been deployed and verified.
(async function(){
 'use strict';
 const ids=['56','57','58A','58B','59','60'],book='1NzoDK1KUuw-KW65S2Zs0R2RDYRXkIDDBFisfMhVxXO8',lesson='2024-1hcl-narrative-shandaishengming',configURL=new URL('shandai-sheet-config.json',document.currentScript.src);
 let cfg;
 try{const r=await fetch(configURL,{cache:'no-store'});if(!r.ok)return;cfg=await r.json();}catch{return;}
 if(!cfg.enabled||cfg.spreadsheetId!==book||cfg.lesson!==lesson||!/^https:\/\/script\.google\.com\/macros\/s\/[A-Za-z0-9_-]+\/exec$/.test(cfg.endpoint))return;
 if(!S.student)S.student={className:'',number:'',name:''};
 const panel=document.createElement('section');panel.className='submission-panel';panel.innerHTML='<div class="identity"><label>班级 / Class<input name="className" maxlength="30" autocomplete="off"></label><label>学号 / No.<input name="number" inputmode="numeric" maxlength="3" autocomplete="off"></label><label>姓名 / Name<input name="name" maxlength="80" autocomplete="name"></label></div><button type="button" class="primary" id="sendWork">提交给老师 / Submit</button><p class="status" id="sendStatus" role="status"></p>';
 document.querySelector('header nav').before(panel);
 const fields=[...panel.querySelectorAll('input')],button=panel.querySelector('button'),status=panel.querySelector('#sendStatus');let busy=false;
 fields.forEach(input=>{input.value=S.student[input.name]||'';input.oninput=()=>{S.student[input.name]=input.value;save();showStatus();};});
 function current(){return {lesson,student:{className:S.student.className.trim(),number:S.student.number.trim(),name:S.student.name.trim()},answers:Object.fromEntries(D.tasks.map(t=>[t.id,w(t.id).draft])),first:Object.fromEntries(D.tasks.map(t=>[t.id,w(t.id).first?.answer||w(t.id).draft])),references:D.tasks.filter(t=>S.exposures.some(x=>x.type==='reference'&&x.task===t.id)).map(t=>t.id),version:D.version};}
 function showStatus(){if(busy)return;button.textContent=S.pendingSheet?'重试提交 / Retry':'提交给老师 / Submit';status.textContent=S.pendingSheet?'上次提交未确认；请重试。 / Please retry.':S.lastSheet?JSON.stringify(current())===S.lastSheet.signature?'已提交给老师 / Submitted':'有新修改，尚未提交 / Changes not submitted':'';}
 document.querySelector('#work').addEventListener('input',showStatus);
 function transmit(payload){return new Promise((resolve,reject)=>{
  const nonce=crypto.randomUUID(),frame=document.createElement('iframe'),form=document.createElement('form'),input=document.createElement('textarea');
  frame.name='hwt_'+nonce;frame.hidden=true;frame.title='Submission receipt';form.hidden=true;form.method='POST';form.action=cfg.endpoint;form.target=frame.name;input.name='payload';input.value=JSON.stringify({...payload,nonce});form.append(input);
  let timer;const cleanup=()=>{clearTimeout(timer);window.removeEventListener('message',message);form.remove();frame.remove();};
  function message(event){const d=event.data;if(!/^https:\/\/[a-z0-9-]+(?:\.[a-z0-9-]+)*\.googleusercontent\.com$/i.test(event.origin)&&event.origin!=='https://script.google.com')return;if(!d||d.kind!=='hwt-reading-shandai-v1'||d.requestId!==payload.requestId||d.nonce!==nonce||d.spreadsheetId!==book)return;cleanup();d.ok===true?resolve(d):reject(Error('not saved'));}
  window.addEventListener('message',message);timer=setTimeout(()=>{cleanup();reject(Error('not confirmed'));},60000);document.body.append(frame,form);try{form.submit();}catch(e){cleanup();reject(e);}
 });}
 button.onclick=async()=>{
  if(busy)return;
  if(!S.pendingSheet){
   const p=current();const invalid=fields.find(input=>!input.value.trim()||(input.name==='number'&&!/^\d{1,3}$/.test(input.value.trim())));if(invalid){status.textContent='请填写班级、学号和姓名 / Enter class, number and name.';invalid.focus();return;}
   const missing=ids.find(id=>!chars(w(id).draft));if(missing){status.textContent='请完成第 '+missing+' 题 / Complete Q'+missing+'.';S.current=missing;go(2);document.querySelector('#draft-'+missing).focus();return;}
   if(D.tasks.some(t=>w(t.id).draft.length>5000||(w(t.id).first?.answer||'').length>5000)){status.textContent='答案过长，请联系老师 / Please check the answer length with your teacher.';return;}
   if(S.lastSheet?.signature===JSON.stringify(p)){status.textContent='这份答案已提交 / This answer has been submitted.';return;}
   D.tasks.forEach(t=>{if(chars(w(t.id).draft)&&!w(t.id).first)w(t.id).first={answer:w(t.id).draft,help:clone(S.help),exposures:clone(S.exposures),time:now()};});
   S.pendingSheet={...current(),requestId:crypto.randomUUID()};save();
  }
  const payload=clone(S.pendingSheet);busy=true;button.disabled=true;fields.forEach(i=>i.disabled=true);status.textContent='正在提交… / Sending…';
  try{await transmit(payload);const {requestId,...body}=payload;S.lastSheet={requestId,signature:JSON.stringify(body),time:now()};delete S.pendingSheet;save();}
  catch{status.textContent='尚未确认收到；答案仍保存在本机，请重试。 / Not confirmed. Your work is kept; retry.';}
  finally{busy=false;button.disabled=false;fields.forEach(i=>i.disabled=false);showStatus();}
 };
 const oldReset=document.querySelector('#reset').onclick;document.querySelector('#reset').onclick=()=>{if(busy){status.textContent='请等待提交完成 / Please wait for submission.';return;}const before=S;oldReset();if(S!==before){S.student={className:'',number:'',name:''};fields.forEach(i=>i.value='');save();showStatus();}};
 showStatus();
})();
