/* Collection adapter for the two earlier worksheets; their exercises remain unchanged. */
(async()=>{'use strict';const L=window.LESSON,c=window.HWTTextbookConnection;
const loadCloud=()=>{const script=document.createElement('script');script.src='/du/textbook/shared/lesson-v1/cloud.js?v=tb2';document.body.append(script)};
if(!c){loadCloud();return}await window.HWTWorksheetReady;const legacy=window.HWTWorksheet;document.querySelector("#submitAll").textContent="交齐本课，提交给教师";const oldNote=document.querySelector(".submitzone > p");oldNote.textContent="每题提交后自动同步。全部完成后交齐本课；开放题由教师覆核，不按字数生成最终成绩。";
const records=()=>{const raw=legacy.state();return raw._hwtAnswers||(raw._hwtAnswers={})};
function snapshot(t,raw){const s={fields:{},choices:{},evidence:{},timestamp:new Date().toISOString(),assisted:false};
 if(t.legacyKind==='index'){if(raw[t.legacyKey]===undefined)return null;s.choices.choice=raw[t.legacyKey];}
 if(t.legacyKind==='value'){const i=t.legacyValues.indexOf(raw[t.legacyKey]);if(i<0)return null;s.fields.value=t.fields[0].options[i];}
 if(t.legacyKind==='verbs'){if(!raw.verbDone)return null;const picks=raw.verbSel||[];s.fields.picked=picks.join('、');t.verbCore.forEach((v,i)=>s.fields['verb'+i]=picks.includes(v)?'已圈选':'未圈选');s.fields.extra=picks.some(v=>!t.verbCore.includes(v)&&!t.verbAllowed.includes(v))?'有':'没有';}
 if(t.legacyKind==='written'){for(const f of t.fields){if(!raw[f.id]?.trim())return null;s.fields[f.id]=raw[f.id].trim();}}
 return s;
}
function capture(written=false){const raw=legacy.state(),answers=records();for(const t of L.tasks){if((t.mode==='written')!==written)continue;const s=snapshot(t,raw);if(!s)continue;const old=answers[t.id],signature=x=>JSON.stringify([x.fields,x.choices]);if(!old)answers[t.id]={first:s,attempts:[s],revision:'',hintCount:0};else if(signature(old.attempts.at(-1))!==signature(s))old.attempts=[s];}try{localStorage.setItem(window.LESSON_STORAGE_KEY,JSON.stringify(raw))}catch{}window.dispatchEvent(new CustomEvent('hwt:lesson-saved'));}
const status=document.createElement('p');status.setAttribute('role','status');const button=document.createElement('button');button.textContent='提交开放题';button.className='btn';document.querySelector('#s5').append(button,status);
function prepareFinal(){const t=L.tasks.find(t=>t.mode==='written');if(!snapshot(t,legacy.state())){status.textContent='请选立场，并写完理由及最后一栏。开放题由教师覆核。';return false}capture(true);status.textContent='开放题已提交，等待教师覆核；修改后可再次提交。';return true}
button.onclick=prepareFinal;window.HWTWorksheetSubmit=()=>{if(prepareFinal())window.dispatchEvent(new CustomEvent('hwt:lesson-final'))};
window.HWTWorksheetSaved=()=>capture();
window.LessonEngine={state:()=>({answers:records(),position:{view:'task',p:1},cloudReadParagraphs:[]}),backup:()=>legacy.state(),prepareFinal,restore(s){const raw={_hwtAnswers:s.answers};for(const t of L.tasks){const x=s.answers[t.id];if(!x)continue;const v=x.attempts.at(-1)||x.first;if(t.legacyKind==='index')raw[t.legacyKey]=v.choices.choice;if(t.legacyKind==='value')raw[t.legacyKey]=t.legacyValues[t.fields[0].options.indexOf(v.fields.value)];if(t.legacyKind==='verbs'){raw.verbDone=true;raw.verbSel=v.fields.picked?v.fields.picked.split('、'):t.verbCore.filter((w,i)=>v.fields['verb'+i]==='已圈选');if(!v.fields.picked&&v.fields.extra==='有')raw.verbSel.push(t.verbTokens.find(w=>!t.verbCore.includes(w)&&!t.verbAllowed.includes(w)));}if(t.legacyKind==='written')Object.assign(raw,v.fields);}legacy.restore(raw);setTimeout(()=>location.reload(),100);}};
loadCloud();
})();
