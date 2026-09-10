export const SHEET_HEADERS=['学习单ID','学习单','版本日期','班级','学号','姓名','提交ID','提交时间','作答次数','独立客观题得分','独立客观题总分','独立开放题教师分','独立开放题总分','待覆核题数','独立总分','独立满分','状态'];
export function gradeAttempt(a:any){
 const rs=a.records.filter((r:any)=>r.stage==='你做'),choice=rs.filter((r:any)=>r.type==='choice'),open=rs.filter((r:any)=>r.type==='open');
 const sum=(xs:any[],k:string)=>xs.reduce((n,r)=>n+(Number.isFinite(r[k])?r[k]:0),0);
 const objective=sum(choice,'score'),objectiveMax=sum(choice,'max'),openMax=sum(open,'max'),pending=open.filter((r:any)=>!Number.isInteger(r.teacherScore)).length,openScore=sum(open,'teacherScore');
 return {objective,objectiveMax,openScore:pending?null:openScore,openMax,pending,total:pending?null:objective+openScore,max:objectiveMax+openMax};
}
export function sheetRows(lesson:any,attempts:any[]){
 const counts=new Map();
 return [...attempts].sort((a,b)=>a.created_at.localeCompare(b.created_at)||a.id.localeCompare(b.id)).map(a=>{
  const key=a.class_name+'\0'+a.student_no,n=(counts.get(key)||0)+1;counts.set(key,n);const g=gradeAttempt(a);
  return [lesson.id,lesson.title,lesson.created_at,a.class_name,a.student_no,a.student_name,a.id,a.created_at,n,g.objective,g.objectiveMax,g.openScore??'',g.openMax,g.pending,g.total??'',g.max,g.pending?'待教师覆核':'已提交'];
 });
}
export function validSheetURL(value:unknown){return typeof value==='string'&&/^https:\/\/script\.google\.com\/macros\/s\/[A-Za-z0-9_-]+\/exec$/.test(value);}
export async function sendSheet(config:any,payload:any){
 if(!validSheetURL(config.url))throw Error('Invalid Sheets destination');
 const signal=AbortSignal.timeout(45000);
 let r=await fetch(config.url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...payload,secret:config.secret}),redirect:'manual',signal});
 // Google ContentService redirects to a one-time Google-hosted result URL; never forward the secret.
 if([301,302,303].includes(r.status)){
  const url=new URL(r.headers.get('location')||'',config.url);
  if(url.protocol!=='https:'||url.hostname!=='script.googleusercontent.com')throw Error('Unexpected Sheets redirect');
  r=await fetch(url,{redirect:'error',signal});
 }
 if(!r.ok)throw Error('Sheets HTTP error');
 const result=await r.json();if(result.ok!==true)throw Error('Sheets save not confirmed');
 return result;
}
