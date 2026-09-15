"use strict";
const DATA=window.CLOZE_DATA;
const SET_ID=window.CLOZE_ID||"cloze";
if(!DATA||!Array.isArray(DATA.questions)) throw new Error("Missing cloze data");
const STORAGE_KEY="hwt-cloze-"+SET_ID;
const TOTAL=DATA.questions.length;
document.title=DATA.title+"｜华文通";
document.getElementById("page-title").textContent=DATA.title;
document.getElementById("section-count").textContent=`共${TOTAL}题 · 共${TOTAL}分`;
document.getElementById("checked-count").textContent=`已核对 0 / ${TOTAL}`;
const progress=document.getElementById("progress"); progress.setAttribute("aria-valuemax",TOTAL);

function blankState(){return {answers:{},first:{},currentStatus:{},mistakes:{},retryAnswers:{},retryStatus:{}}}
let state=blankState();
try{const saved=JSON.parse(localStorage.getItem(STORAGE_KEY)||"null");if(saved&&typeof saved==="object")state=Object.assign(blankState(),saved)}catch(e){state=blankState()}
const $=(sel,root=document)=>root.querySelector(sel);
const $$=(sel,root=document)=>[...root.querySelectorAll(sel)];
const esc=s=>String(s).replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
const norm=s=>String(s||"").replace(/\s+/g,"").trim();

function decorateText(text,q){
 const items=[];(q.keywords||[]).forEach(t=>items.push({t,kind:"keyword"}));
 Object.entries(q.glosses||{}).forEach(([t,tip])=>items.push({t,kind:"gloss",tip}));
 items.sort((a,b)=>b.t.length-a.t.length);let i=0,out="";
 while(i<text.length){const m=items.find(x=>text.startsWith(x.t,i));
  if(m){out+=m.kind==="keyword"?`<span class="keyword">${esc(m.t)}</span>`:`<span class="gloss" tabindex="0" data-tip="${esc(m.tip)}" title="${esc(m.tip)}">${esc(m.t)}</span>`;i+=m.t.length}
  else{out+=esc(text[i]);i++}}
 return out
}
function sentenceParts(q,mode){
 const m=q.sentence.match(/^(.*?)(_+)(.*)$/s),before=m?m[1]:q.sentence,after=m?m[3]:"";
 const val=mode==="retry"?(state.retryAnswers[q.num]||""):(state.answers[q.num]||"");
 const cls=mode==="retry"?"retry-input":"main-input";
 return `${decorateText(before,q)}<input class="answer-input ${cls}" data-num="${esc(q.num)}" value="${esc(val)}" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" aria-label="第${esc(q.num)}题答案">${decorateText(after,q)}`
}
function feedbackHTML(q,ok){return `<p class="fb-title">${ok?"✓ 正确":"× 再想一想"}</p><p>正确答案：<span class="answer-word">${esc(q.answer)}</span></p><p>为什么：${esc(q.whyZh)}</p><p lang="en">${esc(q.whyEn)}</p>`}
function renderWordBank(){$("#word-bank").innerHTML=DATA.wordBank.map(w=>`<div class="word">${esc(w)}</div>`).join("")}
function renderPractice(){
 $("#practice-questions").innerHTML=DATA.questions.map(q=>{const st=state.currentStatus[q.num]||"",checked=q.num in state.first,cls=st==="correct"?"correct":st==="wrong"?"wrong":"",fb=st?feedbackHTML(q,st==="correct"):"",status=st==="correct"?"✓ 答对":st==="wrong"?"× 答错":"";
 return `<article class="question ${cls}" id="q-${esc(q.num)}"><div class="question-head"><span class="qno">Q${esc(q.num)}</span><span class="qstatus">${status}</span></div><div class="sentence">${sentenceParts(q,"main")}</div><div class="actions"><button type="button" class="check main-check" data-num="${esc(q.num)}">核对</button><span class="micro">${checked?"已保存初答":"先自己试一试"}</span></div><div class="feedback" ${st?"":"hidden"}>${fb}</div></article>`}).join("");
 $$(".main-input").forEach(inp=>{inp.addEventListener("input",e=>{state.answers[e.target.dataset.num]=e.target.value;saveState()});inp.addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();checkMain(e.target.dataset.num)}})});
 $$(".main-check").forEach(btn=>btn.addEventListener("click",()=>checkMain(btn.dataset.num)))
}
function checkMain(num){
 const q=DATA.questions.find(x=>x.num===num),card=document.getElementById(`q-${CSS.escape(num)}`),input=$(".main-input",card),value=norm(input.value);
 if(!value){flashStatus("先填一个词语再核对。");input.focus();return}
 const ok=value===norm(q.answer);state.answers[num]=input.value;
 if(!(num in state.first)){state.first[num]=ok;if(!ok)state.mistakes[num]=true}
 state.currentStatus[num]=ok?"correct":"wrong";saveState();updateCard(card,q,ok);updateDashboard();renderNotebook()
}
function updateCard(card,q,ok){card.classList.remove("correct","wrong");card.classList.add(ok?"correct":"wrong");$(".qstatus",card).textContent=ok?"✓ 答对":"× 答错";$(".micro",card).textContent="已保存初答";const fb=$(".feedback",card);fb.innerHTML=feedbackHTML(q,ok);fb.hidden=false}
function renderNav(){
 const nav=$("#question-nav");nav.innerHTML=DATA.questions.map(q=>{const st=state.currentStatus[q.num]||"",cls=st==="correct"?"correct":st==="wrong"?"wrong":"",mark=st==="correct"?"✓":st==="wrong"?"×":"";return `<button type="button" class="${cls}" data-num="${esc(q.num)}">${mark}${esc(q.num)}</button>`}).join("");
 $$("button",nav).forEach(btn=>btn.addEventListener("click",()=>document.getElementById(`q-${btn.dataset.num}`)?.scrollIntoView({behavior:"smooth",block:"start"})))
}
function updateDashboard(){
 const attempted=Object.keys(state.first).length,firstCorrect=Object.values(state.first).filter(Boolean).length;
 $("#score").innerHTML=`初答答对 <b>${attempted?`${firstCorrect} / ${TOTAL}`:"—"}</b>`;
 $("#checked-count").textContent=`已核对 ${attempted} / ${TOTAL}`;progress.setAttribute("aria-valuenow",attempted);$("span",progress).style.width=`${Math.round(attempted/TOTAL*100)}%`;
 $("#mistake-count").textContent=Object.keys(state.mistakes).length;renderNav()
}
let bookFilter="pending";
function renderNotebook(){
 const all=DATA.questions.filter(q=>state.mistakes[q.num]),items=bookFilter==="pending"?all.filter(q=>state.retryStatus[q.num]!=="correct"):all,pending=all.filter(q=>state.retryStatus[q.num]!=="correct").length;
 $("#book-summary").textContent=all.length?`${pending} 题待重做 · 共 ${all.length} 题错题`:"目前没有错题";
 const host=$("#book-questions");if(!items.length){host.innerHTML=`<div class="empty-book">${all.length?"这部分已经重做完成。可以查看“全部错题”。":"答错的题会自动收进这里。"}<br><span lang="en">${all.length?"Review completed.":"Wrong answers will appear here automatically."}</span></div>`;return}
 host.innerHTML=items.map(q=>{const st=state.retryStatus[q.num]||"",cls=st==="correct"?"correct":st==="wrong"?"wrong":"",status=st==="correct"?"✓ 已重做":st==="wrong"?"× 再试":"答案已隐藏",fb=st?feedbackHTML(q,st==="correct"):"";
 return `<article class="question ${cls}" id="book-q-${esc(q.num)}"><div class="question-head"><span class="qno">Q${esc(q.num)}</span><span class="qstatus">${status}</span></div><div class="sentence">${sentenceParts(q,"retry")}</div><div class="actions"><button type="button" class="check retry-check" data-num="${esc(q.num)}">重新核对</button><span class="micro">先看语境，再选词</span></div><div class="feedback" ${st?"":"hidden"}>${fb}</div></article>`}).join("");
 $$(".retry-input",host).forEach(inp=>{inp.addEventListener("input",e=>{state.retryAnswers[e.target.dataset.num]=e.target.value;saveState()});inp.addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();checkRetry(e.target.dataset.num)}})});
 $$(".retry-check",host).forEach(btn=>btn.addEventListener("click",()=>checkRetry(btn.dataset.num)))
}
function checkRetry(num){
 const q=DATA.questions.find(x=>x.num===num),card=document.getElementById(`book-q-${num}`),input=$(".retry-input",card),value=norm(input.value);
 if(!value){flashStatus("先填一个词语再核对。");input.focus();return}
 const ok=value===norm(q.answer);state.retryAnswers[num]=input.value;state.retryStatus[num]=ok?"correct":"wrong";
 if(ok){state.answers[num]=input.value;state.currentStatus[num]="correct"}saveState();
 if(ok&&bookFilter==="pending"){renderPractice();updateDashboard();renderNotebook()}else{card.classList.remove("correct","wrong");card.classList.add(ok?"correct":"wrong");$(".qstatus",card).textContent=ok?"✓ 已重做":"× 再试";const fb=$(".feedback",card);fb.innerHTML=feedbackHTML(q,ok);fb.hidden=false;renderPractice();updateDashboard()}
}
function saveState(){try{localStorage.setItem(STORAGE_KEY,JSON.stringify(state));flashStatus("已保存")}catch(e){$("#save-status").textContent="本机保存暂不可用"}}
let statusTimer;function flashStatus(msg){const el=$("#save-status");el.textContent=msg;clearTimeout(statusTimer);statusTimer=setTimeout(()=>el.textContent="答案自动保存在本机",1200)}
function setTab(which){const practice=which==="practice";$("#practice").hidden=!practice;$("#notebook").hidden=practice;$("#practice-tab").setAttribute("aria-selected",String(practice));$("#notebook-tab").setAttribute("aria-selected",String(!practice));$("#practice-tab").tabIndex=practice?0:-1;$("#notebook-tab").tabIndex=practice?-1:0;if(!practice)renderNotebook()}
$("#practice-tab").addEventListener("click",()=>setTab("practice"));$("#notebook-tab").addEventListener("click",()=>setTab("notebook"));
$$(".book-controls button").forEach(btn=>btn.addEventListener("click",()=>{bookFilter=btn.dataset.filter;$$(".book-controls button").forEach(b=>b.setAttribute("aria-pressed",String(b===btn)));renderNotebook()}));
$("#reset").addEventListener("click",()=>{if(confirm("确定要清除这份练习的答案、进度和错题记录吗？")){localStorage.removeItem(STORAGE_KEY);state=blankState();renderPractice();updateDashboard();renderNotebook();flashStatus("已重置")}});
renderWordBank();renderPractice();updateDashboard();renderNotebook();
