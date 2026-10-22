/* Pure validation/grading. Browser-supplied scores and identities are never trusted. */
export const fail=(message,status=400)=>{throw Object.assign(new Error(message),{status})};
export const text=(v,max,required=false)=>{if(typeof v!=='string'||v.length>max||(required&&!v.trim()))fail('资料缺失或过长。');return v.trim()};
export const fields=t=>[...(t.fields||[]),...(t.answerTable?.fields||[])];
export function snapshot(t,input){
 if(!input||typeof input!=='object')fail('作答格式不完整。');
 const out={fields:{},choices:{},evidence:{},timestamp:text(input.timestamp,40,true),assisted:input.assisted===true};
 if(!Number.isFinite(Date.parse(out.timestamp)))fail('作答时间无效。');
 for(const f of fields(t)){const v=text(input.fields?.[f.id]??'',5000,!f.optional);if(f.type==='select'&&v&&!f.options.includes(v))fail('选项与课文版本不符。');out.fields[f.id]=v;}
 for(const c of t.checks||[]){const v=input.choices?.[c.id];if(!Number.isInteger(v)||v<0||v>=c.options.length)fail('请选择有效选项。');out.choices[c.id]=v;}
 for(const b of t.blanks||[]){const v=text(input.choices?.[b.id],100,true);if(!(t.bank||[]).includes(v))fail('搭配选项无效。');out.choices[b.id]=v;}
 for(const [i] of (t.evidence||[]).entries())out.evidence[i]={text:text(input.evidence?.[i]?.text,12000,true)};
 return out;
}
export function grade(t,s){
 if(t.mode!=='objective')return {correct:null,items:[],status:'pending_teacher'};
 const items=[...fields(t).filter(f=>f.type==='select'&&f.correct!==undefined).map(f=>({id:f.id,label:f.label,answer:s.fields[f.id],correct:s.fields[f.id]===f.correct})),
 ...(t.checks||[]).map(c=>({id:c.id,label:c.question,answer:c.options[s.choices[c.id]],correct:s.choices[c.id]===c.correct})),
 ...(t.blanks||[]).map(b=>({id:b.id,label:b.before+' ___ '+b.after,answer:s.choices[b.id],correct:s.choices[b.id]===b.answer}))];
 if((t.evidence||[]).length||!items.length)fail('此题型尚未接入服务端核对。',422);
 return {correct:items.every(i=>i.correct),items,status:'objective',right:items.filter(i=>i.correct).length,total:items.length};
}
export function normalize(lesson,body){
 if(body.lessonId!==lesson.id||body.contentVersion!==lesson.version)fail('课文版本不符，请联系教师；本机答案仍保留。',409);
 if(!Array.isArray(body.records)||body.records.length>lesson.tasks.length)fail('题目数量不符。');
 const seen=new Set();const records=body.records.map(r=>{
 const t=lesson.tasks.find(t=>t.id===r.taskId);if(!t||seen.has(t.id))fail('题号重复或不属于本课。');seen.add(t.id);
 const first=snapshot(t,r.first),latest=snapshot(t,r.latest||r.first);
 return {taskId:t.id,first,firstResult:grade(t,first),latest,latestResult:grade(t,latest),revision:text(r.revision??'',10000),hintCount:Math.min(10000,Math.max(0,Number.isInteger(r.hintCount)?r.hintCount:0))};
 });
 if(!Array.isArray(body.readParagraphs)||body.readParagraphs.some(p=>!Number.isInteger(p)||p<1||p>lesson.paragraphs.length))fail('阅读位置无效。');
 return {records,readParagraphs:[...new Set(body.readParagraphs)],final:body.final===true};
}
export function summarize(assignment,students,responses,reviews){
 const tasks=assignment.lesson.tasks;const rows=students.map(s=>{
 const rs=responses.filter(r=>r.student_id===s.id),rv=reviews.filter(r=>r.student_id===s.id);
 const pending=rs.filter(r=>tasks.find(t=>t.id===r.task_id)?.mode==='written'&&!rv.some(v=>v.task_id===r.task_id)).length;
 const wrong=rs.filter(r=>r.latest_result.correct===false).length;
 return {...s,answered:rs.length,total:tasks.length,pending,wrong,needsHelp:wrong>0||rv.some(v=>v.verdict==='需帮助'),status:s.submitted_at?'已交齐':rs.length?'进行中':s.last_seen_at?'已进入':'未收到'};
 });
 const questions=tasks.map(t=>{
 const rs=responses.filter(r=>r.task_id===t.id),ind=rs.filter(r=>!r.first_answer.assisted),rv=reviews.filter(r=>r.task_id===t.id);
 const items=t.mode==='objective'?grade(t,rs[0]?.first_answer||{fields:{},choices:{}}).items.map(i=>({id:i.id,label:i.label,answered:rs.length,wrong:rs.filter(r=>r.first_result.items.find(x=>x.id===i.id)?.correct===false).length})):[];
 return {id:t.id,title:t.title,mode:t.mode,role:t.role,received:rs.length,correct:rs.filter(r=>r.first_result.correct===true).length,wrong:rs.filter(r=>r.first_result.correct===false).length,independent:ind.length,independentWrong:ind.filter(r=>r.first_result.correct===false).length,assisted:rs.length-ind.length,latestWrong:rs.filter(r=>r.latest_result.correct===false).length,pending:t.mode==='written'?rs.length-rv.length:0,items};
 });
 return {expected:students.length,complete:rows.filter(s=>s.status==='已交齐').length,incomplete:rows.filter(s=>s.status!=='已交齐').length,notReceived:rows.filter(s=>s.status==='未收到').length,partial:rows.filter(s=>s.status==='进行中'||s.status==='已进入').length,pending:rows.reduce((n,s)=>n+s.pending,0),needsHelp:rows.filter(s=>s.needsHelp).length,students:rows,questions};
}
