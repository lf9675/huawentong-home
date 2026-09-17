"use strict";
const DATA=window.CLOZE_DATA, SET_ID=window.CLOZE_ID||"cloze";
if(!DATA||!Array.isArray(DATA.questions))throw new Error("Missing cloze data");
const STORAGE_KEY="hwt-cloze-"+SET_ID, TOTAL=DATA.questions.length;
const $=(sel,root=document)=>root.querySelector(sel);
const $$=(sel,root=document)=>[...root.querySelectorAll(sel)];
const esc=s=>String(s).replace(/[&<>"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
const norm=s=>String(s||"").normalize("NFKC").replace(/[\s\u200b\uFEFF]/g,"");
const questionById=new Map(DATA.questions.map(q=>[String(q.num),q]));
function blankState(){return {answers:{},first:{},currentStatus:{},mistakes:{},retryAnswers:{},retryStatus:{},firstAnswers:{},checkedAnswers:{},history:{}};}
let state=blankState(), storageBlocked=false, statusTimer=null, bookFilter="pending";
let reviewDrafts={};
try{
 const saved=JSON.parse(localStorage.getItem(STORAGE_KEY)||"null");
 if(saved){
  if(typeof saved!=="object"||Array.isArray(saved))throw Error("Invalid saved record");
  for(const key of Object.keys(state))if(saved[key]&&typeof saved[key]==="object"&&!Array.isArray(saved[key]))state[key]=saved[key];
  for(const q of DATA.questions){
   const n=q.num, value=norm(state.answers[n]), status=state.currentStatus[n];
   if(status){
    const consistent=value&&((status==="correct") === (value===norm(q.answer)));
    if(!consistent||(state.checkedAnswers[n]!==undefined&&state.checkedAnswers[n]!==value))state.currentStatus[n]="";
    else state.checkedAnswers[n]=value;
   }
   if(state.first[n]===false)state.mistakes[n]=true;
   if(state.mistakes[n]&&!state.history[n])state.history[n]={firstWrong:"（旧版未记录原词）",lastWrong:status==="wrong"&&value!==norm(q.answer)?value:"（旧版未记录原词）",wrongCount:1,reviews:[],legacy:true};
  }
 }
}catch{storageBlocked=true;}
function flashStatus(message){
 clearTimeout(statusTimer);
 $("#save-status").textContent=storageBlocked?"本机保存暂不可用，请保留此页面":message;
 if(!storageBlocked)statusTimer=setTimeout(()=>$("#save-status").textContent="答案自动保存在本机",1400);
}
function saveState(){
 if(storageBlocked){flashStatus("");return;}
 try{localStorage.setItem(STORAGE_KEY,JSON.stringify(state));flashStatus("已保存");}
 catch{storageBlocked=true;flashStatus("");}
}
window.addEventListener("pagehide",saveState);

// Keyword emphasis and glossary explanations can overlap without hiding each other.
function decorateText(text,q){
 const marked=Array(text.length).fill(false);
 for(const term of q.keywords||[]){if(!term)continue;let at=text.indexOf(term);while(at>=0){marked.fill(true,at,at+term.length);at=text.indexOf(term,at+term.length);}}
 const styled=(start,end)=>{let result="",i=start;while(i<end){let j=i+1;while(j<end&&marked[j]===marked[i])j++;const part=esc(text.slice(i,j));result+=marked[i]?`<strong class="keyword">${part}</strong>`:part;i=j;}return result;};
 const glosses=Object.entries(q.glosses||{}).filter(([term])=>term).sort((a,b)=>b[0].length-a[0].length);
 let i=0,out="";
 while(i<text.length){
  const match=glosses.find(([term])=>text.startsWith(term,i));
  if(match){const [term,tip]=match;out+=`<span class="gloss" role="button" tabindex="0" data-term="${esc(term)}" data-tip="${esc(tip)}" aria-expanded="false" aria-label="${esc(term)}：查看词义">${styled(i,i+term.length)}</span>`;i+=term.length;}
  else{let end=i+1;while(end<text.length&&!glosses.some(([term])=>text.startsWith(term,end)))end++;out+=styled(i,end);i=end;}
 }
 return out;
}
function draftFor(num){return reviewDrafts[num]||(reviewDrafts[num]={value:"",checked:null});}
function sentenceParts(q,retry){
 const [before,after]=q.sentence.split(/_+/),value=retry?draftFor(q.num).value:state.answers[q.num]||"";
 return `${decorateText(before,q)}<input class="answer-input ${retry?"retry-input":"main-input"}" data-num="${esc(q.num)}" value="${esc(value)}" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" enterkeyhint="done" aria-label="第${esc(q.num)}题答案">${decorateText(after||"",q)}`;
}
function feedbackHTML(q,ok){return `<p class="fb-title">${ok?"✓ 正确":"× 答错"}</p><p>正确答案：<span class="answer-word">${esc(q.answer)}</span></p><p>为什么：${esc(q.whyZh)}</p><p lang="en">${esc(q.whyEn)}</p>`;}
function historyHTML(num){
 const h=state.history[num];if(!h)return "";
 return `<details class="wrong-history"><summary>查看原来的错答（${h.legacy?"至少 ":""}${h.wrongCount} 次）</summary><p>首次错答：<span class="answer-word">${esc(h.firstWrong)}</span><br>最近错答：<span class="answer-word">${esc(h.lastWrong)}</span></p></details>`;
}
function cardHTML(q,retry){
 const checked=retry?draftFor(q.num).checked:null;
 const status=retry?(checked?(checked.correct?"correct":"wrong"):""):(state.currentStatus[q.num]||"");
 const label=status==="correct"?(retry?"✓ 重做正确":"✓ 答对"):status==="wrong"?"× 答错":retry?"答案已隐藏":"未核对";
 return `<article class="question ${status}" id="${retry?"book-q-":"q-"}${esc(q.num)}"><div class="question-head"><span class="qno">Q${esc(q.num)}</span><span class="qstatus">${label}</span></div><div class="sentence">${sentenceParts(q,retry)}</div><div class="actions"><button type="button" class="check ${retry?"retry-check":"main-check"}" data-num="${esc(q.num)}">${retry?"重新核对":"核对"}</button><span class="micro">${retry?"先看语境，再选词":Object.hasOwn(state.first,q.num)?"已保存初答":"先自己试一试"}</span></div><p class="field-error" role="status" hidden></p><div class="feedback" role="status" ${status?"":"hidden"}>${status?feedbackHTML(q,status==="correct"):""}</div>${retry?historyHTML(q.num):""}</article>`;
}
function clearCard(card,message){
 card.classList.remove("correct","wrong");$(".qstatus",card).textContent=message;
 $(".feedback",card).hidden=true;$(".field-error",card).hidden=true;$("input",card).removeAttribute("aria-invalid");
}
function bindInputs(host,retry){
 $$(".answer-input",host).forEach(input=>{
  let composing=false;const n=input.dataset.num,card=input.closest(".question");
  input.addEventListener("compositionstart",()=>composing=true);
  input.addEventListener("compositionend",()=>composing=false);
  input.addEventListener("input",()=>{
   if(retry){const draft=draftFor(n);draft.value=input.value;if(draft.checked&&norm(input.value)!==draft.checked.answer)draft.checked=null;}
   else{state.answers[n]=input.value;if(norm(input.value)!==state.checkedAnswers[n])state.currentStatus[n]="";saveState();updateDashboard();}
   if(retry?!draftFor(n).checked:!state.currentStatus[n])clearCard(card,"已修改 · 待核对");
  });
  const check=()=>{if(!composing)(retry?checkRetry:checkMain)(n);};
  input.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.isComposing&&!composing&&e.keyCode!==229){e.preventDefault();check();}});
  $(".check",card).addEventListener("click",check);
 });
}
function renderPractice(){
 $("#practice-questions").innerHTML=DATA.questions.map(q=>cardHTML(q,false)).join("");bindInputs($("#practice-questions"),false);
}
function validWord(input,card){
 if(/[\p{L}\p{N}]/u.test(norm(input.value))){$(".field-error",card).hidden=true;return true;}
 const error=$(".field-error",card);error.hidden=false;error.textContent="请先填入一个词语，再核对。 / Enter a word first.";input.focus();return false;
}
function recordMistake(n,answer){
 state.mistakes[n]=true;state.retryStatus[n]="";
 const history=state.history[n]||(state.history[n]={firstWrong:answer,lastWrong:answer,wrongCount:0,reviews:[]});
 history.lastWrong=answer;history.wrongCount++;
}
function checkMain(num){
 const q=questionById.get(String(num));
 // getElementById takes the literal ID, never CSS.escape(number).
 const card=document.getElementById(`q-${num}`);if(!q||!card)return;
 const input=$(".main-input",card);if(!validWord(input,card))return;
 const value=norm(input.value),ok=value===norm(q.answer);
 if(state.currentStatus[num]&&state.checkedAnswers[num]===value){updateCard(card,q,ok,false);return;}
 state.answers[num]=input.value;
 if(!Object.hasOwn(state.first,num)){state.first[num]=ok;state.firstAnswers[num]=value;}
 if(!ok)recordMistake(num,value);
 state.checkedAnswers[num]=value;state.currentStatus[num]=ok?"correct":"wrong";
 saveState();updateCard(card,q,ok,false);updateDashboard();
}
function updateCard(card,q,ok,retry){
 card.classList.remove("correct","wrong");card.classList.add(ok?"correct":"wrong");
 $(".qstatus",card).textContent=ok?(retry?"✓ 重做正确":"✓ 答对"):"× 答错";
 $(".micro",card).textContent=retry?"原来的错答仍保留":"已保存初答";
 $("input",card).setAttribute("aria-invalid",String(!ok));
 const feedback=$(".feedback",card);feedback.innerHTML=feedbackHTML(q,ok)+(retry&&ok?"<p>已记录重做正确，初答记录保持不变。</p>":!ok?"<p>已收录错题本，可重新尝试。</p>":"");feedback.hidden=false;
}
function renderNav(){
 const nav=$("#question-nav");nav.innerHTML=DATA.questions.map(q=>{const status=state.currentStatus[q.num]||"";return `<button type="button" class="${status}" data-num="${esc(q.num)}" aria-label="第${esc(q.num)}题，${status==="correct"?"答对":status==="wrong"?"答错":"未核对"}">${status==="correct"?"✓":status==="wrong"?"×":""}${esc(q.num)}</button>`;}).join("");
 $$("button",nav).forEach(button=>button.addEventListener("click",()=>{setTab("practice");const card=document.getElementById(`q-${button.dataset.num}`);card.scrollIntoView({behavior:"auto",block:"start"});$("input",card).focus({preventScroll:true});}));
}
function updateBookSummary(){
 const all=DATA.questions.filter(q=>state.mistakes[q.num]),pending=all.filter(q=>state.retryStatus[q.num]!=="correct").length;
 $("#book-summary").textContent=all.length?`${pending} 题待重做 · 共 ${all.length} 题错题`:"目前没有错题";
}
function updateDashboard(){
 const attempted=DATA.questions.filter(q=>Object.hasOwn(state.first,q.num)).length,correct=DATA.questions.filter(q=>state.first[q.num]===true).length;
 $("#score").innerHTML=`初答答对 <b>${attempted?`${correct} / ${TOTAL}`:"—"}</b>`;
 $("#checked-count").textContent=`已核对 ${attempted} / ${TOTAL}`;
 const progress=$("#progress");progress.setAttribute("aria-valuenow",attempted);$("span",progress).style.width=`${attempted/TOTAL*100}%`;
 $("#mistake-count").textContent=DATA.questions.filter(q=>state.mistakes[q.num]).length;renderNav();updateBookSummary();
}
function renderNotebook(){
 const all=DATA.questions.filter(q=>state.mistakes[q.num]),visible=bookFilter==="pending"?all.filter(q=>state.retryStatus[q.num]!=="correct"):all;
 const host=$("#book-questions");
 host.innerHTML=visible.length?visible.map(q=>cardHTML(q,true)).join(""):`<div class="empty-book">${all.length?"本轮错题已重做正确，可查看“全部错题”。":"答错的题会自动收进这里。"}<br><span lang="en">${all.length?"Review completed. Earlier mistakes are kept.":"Wrong answers will appear here automatically."}</span></div>`;
 bindInputs(host,true);updateBookSummary();
}
function checkRetry(num){
 const q=questionById.get(String(num)),card=document.getElementById(`book-q-${num}`);if(!q||!card)return;
 const input=$(".retry-input",card);if(!validWord(input,card))return;
 const value=norm(input.value),ok=value===norm(q.answer),draft=draftFor(num);
 if(draft.checked?.answer===value){updateCard(card,q,ok,true);return;}
 draft.value=input.value;draft.checked={answer:value,correct:ok};
 if(!ok)recordMistake(num,value);
 state.history[num].reviews.push({answer:value,correct:ok});
 state.retryAnswers[num]=input.value;state.retryStatus[num]=ok?"correct":"wrong";
 if(ok){state.answers[num]=input.value;state.checkedAnswers[num]=value;state.currentStatus[num]="correct";}
 saveState();updateCard(card,q,ok,true);const history=$(".wrong-history",card);if(history)history.outerHTML=historyHTML(num);
 renderPractice();updateDashboard();
}
function setTab(which){
 closeGloss();const practice=which==="practice";
 $("#practice").hidden=!practice;$("#notebook").hidden=practice;
 for(const name of ["practice","notebook"]){const button=$("#"+name+"-tab");button.setAttribute("aria-selected",String(name===which));button.tabIndex=name===which?0:-1;}
 if(!practice){reviewDrafts={};renderNotebook();}
}
$("#practice-tab").addEventListener("click",()=>setTab("practice"));$("#notebook-tab").addEventListener("click",()=>setTab("notebook"));
$(".tabs").addEventListener("keydown",e=>{if(["ArrowLeft","ArrowRight","Home","End"].includes(e.key)){e.preventDefault();const next=e.key==="Home"?"practice":e.key==="End"?"notebook":$("#practice").hidden?"practice":"notebook";setTab(next);$("#"+next+"-tab").focus();}});
$$(".book-controls button").forEach(button=>button.addEventListener("click",()=>{closeGloss();bookFilter=button.dataset.filter;reviewDrafts={};$$(".book-controls button").forEach(b=>b.setAttribute("aria-pressed",String(b===button)));renderNotebook();}));
$("#reset").addEventListener("click",()=>{if(confirm("确定要清除这份练习的答案、进度和错题记录吗？")){closeGloss();state=blankState();reviewDrafts={};storageBlocked=false;saveState();renderPractice();updateDashboard();renderNotebook();setTab("practice");}});

// One viewport-positioned glossary works on touch, mouse and keyboard.
const glossary=document.createElement("div");glossary.id="cloze-glossary";glossary.className="glossary-popup";glossary.setAttribute("role","tooltip");glossary.hidden=true;
glossary.innerHTML='<button type="button" aria-label="关闭词义">×</button><strong></strong><p></p><p lang="en"></p>';document.body.append(glossary);
let activeGloss=null,hideTimer=null;
function closeGloss(){clearTimeout(hideTimer);if(activeGloss){activeGloss.setAttribute("aria-expanded","false");activeGloss.removeAttribute("aria-describedby");}activeGloss=null;glossary.hidden=true;}
function openGloss(element){
 clearTimeout(hideTimer);if(activeGloss&&activeGloss!==element)closeGloss();activeGloss=element;
 const tip=element.dataset.tip,split=tip.indexOf("；");
 $("strong",glossary).textContent=element.dataset.term;$("p",glossary).textContent=split<0?tip:tip.slice(0,split);$("[lang=en]",glossary).textContent=split<0?"":tip.slice(split+1);
 glossary.hidden=false;element.setAttribute("aria-expanded","true");element.setAttribute("aria-describedby",glossary.id);
 const r=element.getBoundingClientRect(),w=glossary.offsetWidth,h=glossary.offsetHeight;
 glossary.style.left=Math.max(12,Math.min(r.left,window.innerWidth-w-12))+"px";
 glossary.style.top=Math.max(12,r.bottom+8+h>window.innerHeight-12?r.top-h-8:r.bottom+8)+"px";
}
document.addEventListener("click",e=>{const element=e.target.closest(".gloss");if(element){activeGloss===element&&e.pointerType!=="mouse"?closeGloss():openGloss(element);}else if(!glossary.contains(e.target))closeGloss();});
document.addEventListener("pointerover",e=>{const element=e.target.closest(".gloss");if(element&&e.pointerType==="mouse")openGloss(element);});
document.addEventListener("pointerout",e=>{if(e.target.closest(".gloss")&&e.pointerType==="mouse")hideTimer=setTimeout(closeGloss,220);});
glossary.addEventListener("pointerenter",()=>clearTimeout(hideTimer));glossary.addEventListener("pointerleave",e=>{if(e.pointerType==="mouse")hideTimer=setTimeout(closeGloss,220);});
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeGloss();const element=e.target.closest(".gloss");if(element&&(e.key==="Enter"||e.key===" ")){e.preventDefault();activeGloss===element?closeGloss():openGloss(element);}});
document.addEventListener("focusout",e=>{if(e.target.closest(".gloss")&&!glossary.contains(e.relatedTarget))hideTimer=setTimeout(closeGloss,220);});
$("button",glossary).addEventListener("click",()=>{const last=activeGloss;closeGloss();last?.focus();});
window.addEventListener("scroll",closeGloss,{passive:true});window.addEventListener("resize",closeGloss);

document.title=DATA.title+"｜华文通";$("#page-title").textContent=DATA.title;$("#section-count").textContent=`共${TOTAL}题 · 共${TOTAL}分`;$("#progress").setAttribute("aria-valuemax",TOTAL);
$("#word-bank").innerHTML=DATA.wordBank.map(w=>`<div class="word">${esc(w)}</div>`).join("");
renderPractice();updateDashboard();renderNotebook();if(storageBlocked)flashStatus("");
