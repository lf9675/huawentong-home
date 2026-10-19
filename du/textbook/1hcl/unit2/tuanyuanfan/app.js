const $=s=>document.querySelector(s);
const KEY="huawentong-tuanyuanfan-v1";
const blank=()=>({stage:"read",chunk:0,current:1,read:[],answers:{},showComic:false,comicPage:1});
let state;try{state=JSON.parse(localStorage.getItem(KEY))||blank()}catch{state=blank()}
let selected=null,lockUntil=0;
const esc=s=>String(s??"").replace(/[&<>"\x27]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","\x27":"&#39;"}[c]));
const bi=(z,e,cls="")=>`<div class="explain ${cls}">${esc(z)}<small lang="en">${esc(e)}</small></div>`;
const kw=(s,words=[])=>{let h=esc(s);[...new Set(words)].sort((a,b)=>b.length-a.length).forEach(w=>h=h.split(esc(w)).join(`<strong class="keyword">${esc(w)}</strong>`));return h};
function save(){updateRoute();try{localStorage.setItem(KEY,JSON.stringify(state));$("#saveState").textContent="已保存在本机 · Saved on this device"}catch{$("#saveState").textContent="本机保存不可用，请保持页面开启 · Keep this page open"}}
function a(id){return state.answers[id]||(state.answers[id]={values:{},evidence:{},text:"",revision:"",attempts:0,hints:0,unlocked:false,order:[]})}
function task(){return DATA.tasks.find(t=>t.id===state.current)}
function saveInput(key,value){const x=a(state.current);x[key]=value;save()}
function sentenceHTML(text,p){let parts=text.match(/[^。！？]+[。！？]?/g)||[text];if(p===14)parts=parts.flatMap(s=>s.split(/(?=我一边)|(?=一边不停)|(?=希望我的)/));return parts.map((s,i)=>`<span class="sentence" role="button" tabindex="0" draggable="true" data-p="${p}" data-i="${i}" data-text="${esc(s)}">${gloss(s)}</span>`).join("")}
function gloss(s){let h=esc(s);Object.keys(DATA.glossary).sort((a,b)=>b.length-a.length).forEach(w=>h=h.split(w).join(`<span class="word" role="button" tabindex="0" data-word="${w}">${w}</span>`));return h}
function source(){const t=task();let transfer=state.stage!=="read"&&state.current===10;
 const [lo,hi]=DATA.chunks[state.chunk];
 $("#sourceTitle").textContent=transfer?"新短文 · Independent reading":`原文 · 第${lo}—${hi}段`;
 $("#chunkNav").hidden=transfer;
 $("#source").innerHTML=transfer?`<p class="source-note explain">本练习自编短文 <small lang="en">A new passage for transfer practice</small></p><p class="kaiti passage">${sentenceHTML(DATA.transfer,0)}</p>`:DATA.paragraphs.slice(lo-1,hi).map((p,i)=>`<div class="paragraph"><div class="paragraph-tools"><span class="pnum">${lo+i}</span><button class="read-paragraph" data-read-paragraph="${lo+i}" aria-label="朗读第${lo+i}段">听</button></div><p class="kaiti passage">${sentenceHTML(p,lo+i)}</p></div>`).join("");
 $("#chunkSelect").value=String(state.chunk);$("#rangeLabel").textContent=transfer?"根据新短文作答":state.stage==="read"?"初读时连贯读完全文":`本题范围：第${t.range[0]}—${t.range[1]}段`;
 $("#source").scrollTop=0;
}
function comic(n,panel){if(!panel)return `<img class="comic-full" src="${ASSETS[n-1]}" alt="《团圆饭》第${n}部分，校订漫画" loading="lazy">`;
 const i=(panel-1)%10,col=i%2,row=Math.floor(i/2),x=col?517:5,y=[[102,374,663,950,1222],[102,372,630,892,1172],[102,373,634,897,1174]][n-1][row],w=503,h=[[264,282,282,267,302],[264,252,256,273,354],[264,255,256,269,351]][n-1][row];
 return `<div class="comic-panel" style="aspect-ratio:${w}/${h};--comic:url(\x27${ASSETS[n-1]}\x27);background-size:${1024/w*100}% ${1536/h*100}%;background-position:${x/(1024-w)*100}% ${y/(1536-h)*100}%" role="img" aria-label="漫画第${panel}格"></div>`;
}
function render(){
 document.querySelectorAll("[data-stage]").forEach(b=>b.classList.toggle("active",b.dataset.stage===state.stage));
 const total=Object.values(state.answers).filter(x=>x.unlocked).length;$("#progress").textContent=`已完成 ${total} / 10 项任务`;
 $("#taskNav").hidden=state.stage==="read"||state.stage==="review";
 $("#taskNav").innerHTML=DATA.tasks.filter(t=>state.stage==="lesson1"?t.id<=4:t.id>=5).map(t=>`<button class="${t.id===state.current?"active":""}" data-task="${t.id}" aria-current="${t.id===state.current?"step":"false"}">${t.id} ${esc(t.title)}${a(t.id).unlocked?" ✓":""}</button>`).join("");
 document.querySelectorAll("[data-task]").forEach(b=>b.onclick=()=>go(+b.dataset.task));
 $("#workspace").hidden=state.stage==="review";$("#review").hidden=state.stage!=="review";
 if(state.stage==="review"){renderReview();return}
 source();if(state.stage==="read"){renderRead();return}renderTask();
}
function renderRead(){const [lo,hi]=DATA.chunks[state.chunk];const seen=state.read.includes(state.chunk);
 $("#activity").innerHTML=`<div class="eyebrow">初读 · Read the text</div><h2>今年的团圆饭，有什么不同？</h2>${bi("先连贯读完，遇到难词可点开简释。","Read through first. Tap an underlined word if needed.")}<div class="read-actions"><button class="primary" id="markRead">${seen?"已读本组 ✓":"我已读完这组"} <small>Mark as read</small></button><button id="nextRead">${state.chunk===5?"进入第一课":"下一组原文"} <small>${state.chunk===5?"Lesson 1":"Next paragraphs"}</small></button></div><p class="muted">已读 ${state.read.length} / 6 组</p><details ${state.showComic?"open":""}><summary>配套漫画 <small>Comic reference</small></summary><div class="comic-tabs">${[1,2,3].map(n=>`<button data-comic="${n}" class="${state.comicPage===n?"active":""}">第${n}部分</button>`).join("")}</div>${comic(state.comicPage)}<button id="zoomComic">放大漫画 <small>Enlarge</small></button></details>`;
 $("#markRead").onclick=()=>{if(!state.read.includes(state.chunk))state.read.push(state.chunk);save();renderRead()};
 $("#nextRead").onclick=()=>{if(state.chunk<5){state.chunk++;state.comicPage=state.chunk<2?1:state.chunk<4?2:3}else{state.stage="lesson1";state.current=1;state.chunk=0}updateRoute();save();render()};
 document.querySelectorAll("[data-comic]").forEach(b=>b.onclick=()=>{state.comicPage=+b.dataset.comic;save();renderRead()});
 $("#zoomComic").onclick=()=>openDialog(comic(state.comicPage),"comic-dialog");
}
function field(c,x){return `<fieldset><legend class="kaiti">${kw(c.label,c.keywords)}</legend>${c.options.map((s,i)=>`<label class="option ${String(x.values[c.id])===String(i)?"chosen":""}"><input type="radio" name="${c.id}" value="${i}" ${String(x.values[c.id])===String(i)?"checked":""}><span class="kaiti">${esc(s)}</span></label>`).join("")}</fieldset>`}
function matchField(c,x){return `<label class="match-row"><span class="kaiti">${kw(c.label,c.keywords)}</span><select class="kaiti" data-check="${c.id}" aria-label="${esc(c.label)}"><option value="">请选择 · Choose</option>${c.options.map((s,i)=>`<option value="${i}" ${String(x.values[c.id])===String(i)?"selected":""}>${esc(s)}</option>`).join("")}</select></label>`}
function renderTask(){const t=task(),x=a(t.id);let form="";
 if(t.slots)form+=bi("从左侧点选或拖入相关原句，可随时移除。","Tap a sentence then a box, or drag it into a box.")+`<div class="evidence-grid">${t.slots.map((name,i)=>`<div class="evidence-wrap"><div class="explain">${esc(name)} <small>Text evidence ${i+1}</small></div><button class="evidence kaiti" data-slot="${i}">${x.evidence[i]?esc(x.evidence[i].text):"点这里放入原句"}</button>${x.evidence[i]?`<button class="remove" data-remove="${i}">移除 · Remove</button>`:""}</div>`).join("")}</div>`;
 if(t.type==="order"){const rest=t.initialOrder.filter(i=>!x.order.includes(i));form+=`<div class="order-bank">${rest.map(i=>`<button class="kaiti" data-order="${i}">${esc(t.cards[i])}</button>`).join("")}</div><ol class="order-result">${x.order.map(i=>`<li class="kaiti">${esc(t.cards[i])}</li>`).join("")}</ol><button id="undoOrder" ${!x.order.length?"disabled":""}>撤回一步 · Undo</button>`}
 if(t.checks)form+=t.checks.map(c=>["match","classify"].includes(t.type)?matchField(c,x):field(c,x)).join("");
 if(t.type==="write")form+=`<label class="answer-label explain" for="answerText">完整作答 <small>Write a complete answer</small></label><textarea id="answerText" class="kaiti" rows="6" placeholder="用两三句回答，可复制原文后整理。">${esc(x.text)}</textarea>`;
 if(t.type==="open")form+=`<fieldset><legend class="explain">我的立场 <small>My position</small></legend>${["认同","部分认同","不认同"].map((s,i)=>`<label class="option"><input type="radio" name="stance" value="${i}" ${String(x.values.stance)===String(i)?"checked":""}><span class="kaiti">${s}</span></label>`).join("")}</fieldset><label class="oral-confirm explain"><input type="checkbox" id="oralDone" ${x.oral?"checked":""}> 我已结合课文说出理由，并提出一个可行行动。<small lang="en">I have explained my view using the text and suggested a practical action.</small></label><details><summary>简短笔记（可选） <small>Optional notes</small></summary><textarea id="noteText" class="kaiti" rows="3" placeholder="记下自己的理由或建议。">${esc(x.text)}</textarea></details>`;
 $("#activity").innerHTML=`<div class="eyebrow">${t.id<=4?"第一课":"第二课"} · 任务 ${t.id} / 10</div><h2>${esc(t.title)}</h2><p class="question kaiti">${kw(t.question,t.keywords)}</p>${bi(...t.guide)}<div class="kind explain">${esc(t.kind)}</div>${t.comic?`<details class="task-comic"><summary>查看对应漫画 <small>Comic reference</small></summary>${comic(t.comic,t.panel)}</details>`:""}${form}<div class="action-row"><button id="checkAnswer" class="primary">${t.type==="write"?"提交并比较":t.type==="open"?"完成讨论，查看参考":"检查选择"} <small>Check</small></button><button id="hintBtn">需要提示 <small>Hint</small></button></div><div id="feedback" aria-live="polite"></div><div id="solution">${x.unlocked?solution(t,x):""}</div><div class="task-footer"><button id="prevTask" ${t.id===1?"disabled":""}>上一项 · Previous</button><button id="nextTask">${t.id===10?"查看学习记录":"下一项"} <small>${t.id===10?"Review":"Next"}</small></button></div>`;
 $("#activity").querySelectorAll("input[type=radio]").forEach(el=>el.onchange=()=>{x.values[el.name]=el.value;save();el.closest("fieldset").querySelectorAll(".option").forEach(o=>o.classList.toggle("chosen",o.querySelector("input").checked))});
 document.querySelectorAll("[data-check]").forEach(el=>el.onchange=()=>{x.values[el.dataset.check]=el.value;save()});
 $("#answerText")?.addEventListener("input",e=>saveInput("text",e.target.value));$("#noteText")?.addEventListener("input",e=>saveInput("text",e.target.value));
 $("#oralDone")?.addEventListener("change",e=>{x.oral=e.target.checked;save()});
 document.querySelectorAll("[data-order]").forEach(b=>b.onclick=()=>{x.order.push(+b.dataset.order);save();renderTask()});
 $("#undoOrder")?.addEventListener("click",()=>{x.order.pop();save();renderTask()});
 document.querySelectorAll("[data-slot]").forEach(el=>{el.onclick=()=>putEvidence(+el.dataset.slot);el.ondragover=e=>{e.preventDefault();el.classList.add("drop")};el.ondragleave=()=>el.classList.remove("drop");el.ondrop=e=>{e.preventDefault();try{selected=JSON.parse(e.dataTransfer.getData("text/plain"))}catch{}putEvidence(+el.dataset.slot)}});
 document.querySelectorAll("[data-remove]").forEach(el=>el.onclick=()=>{delete x.evidence[el.dataset.remove];save();renderTask()});
 $("#checkAnswer").onclick=check;$("#hintBtn").onclick=()=>hint();$("#prevTask").onclick=()=>go(t.id-1);$("#nextTask").onclick=()=>t.id===10?stage("review"):go(t.id+1);
 wireSolution();if(x.hints&&!x.unlocked)hint(false);
}
function putEvidence(i){if(!selected){$("#feedback").innerHTML=bi("请先点左侧原文中的一句话。","Select a sentence from the passage first.","notice");return}a(state.current).evidence[i]={...selected};selected=null;save();renderTask();document.querySelectorAll(".selected").forEach(e=>e.classList.remove("selected"))}
function hint(add=true){const x=a(state.current),t=task();if(add){x.hints++;save()}const idx=Math.min(Math.max(0,x.hints-1),1);$("#feedback").innerHTML=bi(...t.hints[idx],"notice");}
function validate(t,x){if(t.checks?.some(c=>x.values[c.id]===undefined||x.values[c.id]===""))return ["请完成本题的选择。","Complete the choices for this task."];
 if(t.type==="order"&&x.order.length!==4)return ["请排好四张卡片。","Place all four cards in order."];
 if(t.type==="evidence"&&Object.keys(x.evidence).length<2)return ["请选入两项行为证据。","Add evidence for both actions."];
 if(t.type==="write"&&x.text.trim().length<12)return ["请先写出有内容的回答，再与参考答案比较。","Write a meaningful answer before comparing it."];
 if(t.type==="open"&&(x.values.stance===undefined||!x.oral))return ["请先选择立场并完成口头说明。","Choose a position and explain it aloud first."];return null}
function objective(t,x){let ok=!t.checks||t.checks.every(c=>+x.values[c.id]===c.correct);if(t.type==="order")ok=ok&&x.order.join(",")==="0,1,2,3";if(t.type==="evidence"){let e=Object.values(x.evidence).map(o=>o.text);ok=ok&&e.some(s=>s.includes("夹菜"))&&e.some(s=>s.includes("讲")&&s.includes("学校"));}return ok}
function check(){if(Date.now()<lockUntil)return;const t=task(),x=a(t.id),missing=validate(t,x);if(missing){$("#feedback").innerHTML=bi(...missing,"notice");return}
 if(!x.first){x.first={text:x.text,values:{...x.values},evidence:{...x.evidence},order:[...x.order],assisted:x.hints>0};x.firstCorrect=["write","open"].includes(t.type)?null:objective(t,x)}
 x.attempts++;const open=["write","open"].includes(t.type),ok=open||objective(t,x);
 if(ok){x.unlocked=true;save();$("#feedback").innerHTML=bi(open?"已保存首次作答。请比较、再订正。":"选择正确。请看文字依据与解释。",open?"Your first response is saved. Compare and revise.":"Correct. Now check the evidence and explanation.","success");$("#solution").innerHTML=solution(t,x);wireSolution();$("#progress").textContent=`已完成 ${Object.values(state.answers).filter(x=>x.unlocked).length} / 10 项任务`;return}
 save();const idx=Math.min(x.attempts-1,1);$("#feedback").innerHTML=bi(...t.hints[idx],"notice")+(x.attempts>=2?`<button id="revealAfterTry">读完提示后查看讲解 · View explanation</button>`:"");lockUntil=Date.now()+5000;$("#checkAnswer").disabled=true;
 const reveal=$("#revealAfterTry");if(reveal){reveal.disabled=true;reveal.onclick=()=>{x.unlocked=true;x.guided=true;save();renderTask()}}setTimeout(()=>{if($("#checkAnswer"))$("#checkAnswer").disabled=false;if($("#revealAfterTry"))$("#revealAfterTry").disabled=false},5000);
}
function solution(t,x){return `<section class="solution"><h3>答案从哪里来？ <small>How the answer is built</small></h3>${t.source.map(s=>bi(...s)).join("")}<h3>参考答案 <small>Model answer</small></h3><p class="kaiti model">${esc(t.answer)}</p>${t.points?`<div class="selfcheck"><h3>逐点自检 <small>Check each meaning point</small></h3>${t.points.map((p,i)=>`<label><input type="checkbox" data-point="${i}" ${x.points?.includes(i)?"checked":""}><span class="kaiti">${esc(p)}</span><span class="muted">1分</span></label>`).join("")}${bi("这是自评记录，不是自动评分。","This records your self-check, not an automatic mark.")}</div>`:""}${bi(...t.compare,"compare")}${t.extra?bi(...t.extra):""}${t.type==="write"?`<h3>订正答案 <small>Revise your answer</small></h3><textarea class="kaiti" id="revisionText" rows="5" placeholder="保留首次答案，在这里补足或修改。">${esc(x.revision)}</textarea>`:""}</section>`}
function wireSolution(){const x=a(state.current);$("#revisionText")?.addEventListener("input",e=>{x.revision=e.target.value;save()});document.querySelectorAll("[data-point]").forEach(el=>el.onchange=()=>{let p=new Set(x.points||[]);el.checked?p.add(+el.dataset.point):p.delete(+el.dataset.point);x.points=[...p];save()})}
function go(id){state.current=id;state.stage=id<=4?"lesson1":"lesson2";const r=task().range;state.chunk=Math.max(0,DATA.chunks.findIndex(([lo,hi])=>r[0]>=lo&&r[0]<=hi));selected=null;updateRoute();save();render();$("#activity").scrollTop=0}
function stage(s){if(s==="lesson1"){go(Math.min(4,state.current));return}if(s==="lesson2"){go(Math.max(5,state.current));return}state.stage=s;updateRoute();save();render()}
function renderReview(){const objectiveTasks=DATA.tasks.filter(t=>!["write","open"].includes(t.type));const tried=objectiveTasks.filter(t=>a(t.id).first);const correct=tried.filter(t=>a(t.id).firstCorrect).length;
 $("#review").innerHTML=`<h2>我的阅读记录</h2>${bi("记录保存在这台设备，老师不会自动收到。","Records stay on this device and are not automatically sent to your teacher.")}<p class="score">客观任务首次正确率：${tried.length?Math.round(correct/tried.length*100)+"%":"尚未作答"} <small>${correct} / ${tried.length} 项</small></p>${bi("短答与开放讨论不计入自动正确率。","Written and open responses are excluded from automatic accuracy.")}<div class="review-list">${DATA.tasks.map(t=>{const x=a(t.id);return `<div class="review-row"><span>${t.id}. ${esc(t.title)}</span><span>${x.unlocked?"已比较 ✓":x.first?"待订正":"未完成"}</span><button data-go="${t.id}">返回 · Open</button></div>`}).join("")}</div>${[4,10].map(id=>{const x=a(id);return `<section class="record"><h3>任务${id}：${esc(DATA.tasks[id-1].title)}</h3><p class="muted">${x.first?.assisted?"首次提交前使用了提示 · Assisted":x.first?"首次提交前未使用提示 · Unassisted":"尚未提交 · Not submitted"}</p><h4>首次答案</h4><p class="kaiti">${esc(x.first?.text||"尚未作答")}</p><h4>订正答案</h4><p class="kaiti">${esc(x.revision||"尚未订正")}</p><p>自检 ${x.points?.length||0} / 3 点（老师确认）</p></section>`}).join("")}<button id="downloadRecord">下载学习记录 <small>Download record</small></button>`;
 document.querySelectorAll("[data-go]").forEach(b=>b.onclick=()=>go(+b.dataset.go));$("#downloadRecord").onclick=downloadRecord;
}
function downloadRecord(){let out=["《团圆饭》阅读记录","本记录由学生设备保存，非自动考试评分。"];DATA.tasks.forEach(t=>{const x=a(t.id);out.push(`\n任务${t.id} ${t.title}`,`完成：${x.unlocked?"是":"否"}`,`首次作答前提示：${x.first?.assisted?"有":"无或未提交"}`);if(t.type==="write")out.push("首次答案："+(x.first?.text||""),"订正："+x.revision,`自检：${x.points?.length||0}/3点（教师确认）`)});const u=URL.createObjectURL(new Blob([out.join("\n")],{type:"text/plain;charset=utf-8"}));const el=document.createElement("a");el.href=u;el.download="团圆饭_我的阅读记录.txt";el.click();setTimeout(()=>URL.revokeObjectURL(u),1000)}
function openDialog(html,cls=""){const d=$("#dialog");d.className=cls;$("#dialogContent").innerHTML=html;if(d.showModal)d.showModal();else d.setAttribute("open","")}
function word(w){const [z,e]=DATA.glossary[w];openDialog(`<h2 class="kaiti">${w}</h2>${bi(z,e)}<button id="speakWord">朗读词语与解释 <small>Listen</small></button><p id="speechNote" class="muted" aria-live="polite"></p>`);$("#speakWord").onclick=()=>speak(w+"。"+z,e)}
function speak(z,e){if(!("speechSynthesis" in window)){ $("#speechNote").textContent="这台设备暂不支持朗读，可阅读中英解释。 Audio unavailable; read the bilingual explanation.";return}speechSynthesis.cancel();const c=new SpeechSynthesisUtterance(z);c.lang="zh-CN";c.rate=.85;const en=new SpeechSynthesisUtterance(e);en.lang="en-SG";c.onerror=()=>{$("#speechNote").textContent="朗读未能播放，可阅读中英解释。 Read the bilingual text if audio is unavailable."};speechSynthesis.speak(c);speechSynthesis.speak(en)}
$("#dialogClose").onclick=()=>{$("#dialog").close?.();$("#dialog").removeAttribute("open");window.speechSynthesis?.cancel()};
document.addEventListener("click",e=>{const w=e.target.closest("[data-word]");if(w){e.stopPropagation();word(w.dataset.word);return}const s=e.target.closest(".sentence");if(s){selected={p:+s.dataset.p,text:s.dataset.text};document.querySelectorAll(".sentence.selected").forEach(n=>n.classList.remove("selected"));s.classList.add("selected")}});
document.addEventListener("keydown",e=>{if(["Enter"," "].includes(e.key)&&e.target.matches(".sentence,[data-word]")){e.preventDefault();e.target.click()}});
document.addEventListener("dragstart",e=>{const s=e.target.closest(".sentence");if(s){selected={p:+s.dataset.p,text:s.dataset.text};e.dataTransfer.setData("text/plain",JSON.stringify(selected));e.dataTransfer.effectAllowed="copy"}});
document.querySelectorAll("[data-stage]").forEach(b=>b.onclick=()=>stage(b.dataset.stage));
$("#chunkSelect").onchange=e=>{state.chunk=+e.target.value;save();source();if(state.stage==="read")renderRead()};$("#chunkPrev").onclick=()=>{state.chunk=Math.max(0,state.chunk-1);save();render()};$("#chunkNext").onclick=()=>{state.chunk=Math.min(5,state.chunk+1);save();render()};
$("#reset").onclick=()=>{openDialog(`<h2>重置本机记录？</h2>${bi("这会清除本练习的答案和进度，请先下载需要保留的记录。","This clears this exercise’s answers and progress. Download any records first.")}<button class="primary" id="confirmReset">确认重置 · Reset</button>`);$("#confirmReset").onclick=()=>{state=blank();selected=null;updateRoute();save();$("#dialogClose").click();render()}};
$("#wordList").onclick=()=>openDialog(`<h2>词语帮助 <small>Word help</small></h2>${Object.keys(DATA.glossary).map(w=>`<button class="kaiti word-button" data-word="${w}">${w}</button>`).join("")}`);
function updateRoute(){
 const hash=state.stage==="lesson1"||state.stage==="lesson2"?"task-"+state.current:state.stage==="read"?"read-"+(state.chunk+1):state.stage;
 try{window.history.replaceState(null,"","#"+hash)}catch{}
}
function applyRoute(){
 const hash=window.location.hash.slice(1);
 if(hash==="lesson1"){go(1);return}
 if(hash==="lesson2"){go(5);return}
 if(/^task-(?:[1-9]|10)$/.test(hash)){go(+hash.slice(5));return}
 if(hash==="read"){state.stage="read";state.chunk=0;state.comicPage=1}
 if(/^read-[1-6]$/.test(hash)){state.stage="read";state.chunk=+hash.slice(5)-1}
 if(hash==="review")state.stage="review";
 render();save();
}
window.addEventListener("hashchange",applyRoute);
document.addEventListener("click",e=>{
 const b=e.target.closest("[data-read-paragraph]");if(!b)return;
 const n=+b.dataset.readParagraph, note=$("#audioState");
 if(!window.speechSynthesis||!window.SpeechSynthesisUtterance){note.textContent="设备暂不支持朗读，请阅读原文。";return}
 window.speechSynthesis.cancel();const u=new window.SpeechSynthesisUtterance(DATA.paragraphs[n-1]);u.lang="zh-CN";u.rate=.85;
 note.textContent="正在朗读第"+n+"段";u.onend=()=>note.textContent="朗读结束";u.onerror=()=>note.textContent="朗读未能播放，请阅读原文。";window.speechSynthesis.speak(u);
});
$("#stopAudio").onclick=()=>{window.speechSynthesis?.cancel();$("#audioState").textContent="已停止朗读"};
applyRoute();
