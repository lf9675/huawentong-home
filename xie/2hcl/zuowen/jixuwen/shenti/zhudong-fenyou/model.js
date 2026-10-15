'use strict';
(function(root){
 const copy=x=>JSON.parse(JSON.stringify(x));
 const now=()=>new Date().toISOString();
 const uid=()=>globalThis.crypto?.randomUUID?.()||('r'+Date.now().toString(36)+Math.random().toString(36).slice(2));
 const blank=()=>({keywords:[],outline:'',focus:''});
 const blankStudy=()=>({sampleViewed:false,showNotes:true,activeGroup:'sudden',activeCase:0,cases:{}});
 function study(s){if(!s.study)s.study=blankStudy();return s.study;}
 function caseState(s,id){const t=study(s);if(!t.cases[id])t.cases[id]={choice:null,evidence:[],rewrite:'',first:null,attempts:0,until:0,revealed:false,correct:false,reviewed:false,versions:[]};return t.cases[id];}
 function checkCase(s,q){if(!s.first)return '请先保留初次独立构思。';const c=caseState(s,q.id);if(c.revealed)return '';if(Date.now()<c.until)return '请先读提示，稍后再试。';if(c.choice===null)return '请先判断主要问题。';if(!c.evidence.length)return '请点选原文中最需要调整或补写的位置。';if(!c.rewrite.trim())return '请先试着改写关键部分，再看解析。';if(!c.first)c.first={choice:c.choice,evidence:copy(c.evidence),rewrite:c.rewrite,at:now()};c.attempts++;c.correct=c.choice===q.answer;c.revealed=c.correct||c.attempts>=2;c.until=c.revealed?0:Date.now()+5000;log(s,'扣题辨析 '+q.id+'：'+(c.correct?'判断方向符合解析':c.revealed?'展开解析':'查看提示'));return '';}
 function finishCase(s,q){const c=caseState(s,q.id);if(!c.revealed)return '请先完成判断并查看解析。';if(!c.rewrite.trim())return '请保留你的改写。';if(c.versions.length>=20)return '本例已保留二十次修改，请查看已有版本。';c.versions.push({choice:c.choice,evidence:copy(c.evidence),rewrite:c.rewrite,at:now()});c.reviewed=true;log(s,'扣题辨析 '+q.id+'：保留对照后的改写');return '';}
 function validStudy(t){
  const tx=(x,n)=>typeof x==='string'&&x.length<=n;
  const ev=x=>Array.isArray(x)&&x.length<=8&&x.every(i=>Number.isInteger(i)&&i>=0&&i<8);
  const choice=x=>x===null||(Number.isInteger(x)&&x>=0&&x<3);
  const snap=x=>x&&choice(x.choice)&&ev(x.evidence)&&tx(x.rewrite,10000)&&tx(x.at,100);
  if(!t||typeof t.sampleViewed!=='boolean'||typeof t.showNotes!=='boolean'||!['sudden','initiative','responsibility','relief','feelings'].includes(t.activeGroup)||!Number.isInteger(t.activeCase)||t.activeCase<0||t.activeCase>2||!t.cases||Array.isArray(t.cases)||Object.keys(t.cases).length>15)return false;
  return Object.entries(t.cases).every(([id,c])=>/^(sudden|initiative|responsibility|relief|feelings)-[123]$/.test(id)&&c&&choice(c.choice)&&ev(c.evidence)&&tx(c.rewrite,10000)&&(c.first===null||snap(c.first))&&Number.isInteger(c.attempts)&&c.attempts>=0&&c.attempts<=100&&Number.isFinite(c.until)&&['revealed','correct','reviewed'].every(k=>typeof c[k]==='boolean')&&Array.isArray(c.versions)&&c.versions.length<=20&&c.versions.every(snap));
 }
 function fresh(){return {version:4,study:blankStudy(),id:uid(),createdAt:now(),updatedAt:now(),stage:'initial',name:'',initial:blank(),first:null,compare:{selected:null,first:null,tries:0,correct:false,revealed:false,until:0},modelOpened:false,revised:{...blank(),body:'',reasons:[],evidence:''},revisions:[],transfer:{...blank(),essay:'',photos:[],mode:'type',reflection:''},transferPlan:null,submissions:[],feedback:[],events:[],independentStarted:null,returnVisits:0};}
 function log(s,type){s.events.push({at:now(),type});s.updatedAt=now();}
 function planError(d,prompt){if(!d.keywords.length)return '请先标出你认为重要的题目词语。';if(d.keywords.some(k=>!prompt.includes(k)))return '有一个关键词不在题目中，请重新标记。';if(!d.outline.trim())return '请先写下完整构思。';if(!d.focus.trim())return '请从自己的提纲中选出准备详写的内容。';if(!d.outline.includes(d.focus))return '提纲已修改，请重新选出准备详写的内容。';return '';}
 function lockFirst(s,prompt){const e=planError(s.initial,prompt);if(e)return e;if(s.first)return '初次构思已保留。';s.first={...copy(s.initial),at:now()};s.revised={...s.revised,...copy(s.initial)};s.stage='learn';log(s,'保存初次独立构思');return '';}
 function checkCompare(s){let c=s.compare;if(!c.selected)return '请先选择一段。';if(c.correct||c.revealed)return '';if(Date.now()<c.until)return '请先读提示，稍后再试。';if(c.first===null)c.first=c.selected;c.tries++;c.correct=c.selected==='b';c.revealed=c.correct||c.tries>=2;c.until=c.revealed?0:Date.now()+5000;log(s,'比较段落：'+(c.correct?'判断符合示范':'查看提示'));return '';}
 function lockRevision(s,prompt){if(!s.first)return '请先保存初次独立构思。';const e=planError(s.revised,prompt);if(e)return e;if(!s.revised.body.trim())return '请展开一个最能表现题意的重点段落。';if(!s.revised.evidence.trim()||!s.revised.body.includes(s.revised.evidence))return '请在重点段落中标出最能表现题意的一处。';s.revisions.push({...copy(s.revised),at:now()});log(s,'保存教学后的提纲与重点段落');return '';}
 function beginTransfer(s){if(!s.revisions.length)return '请先保存本题的修改稿与重点段落。';if(!s.independentStarted){s.independentStarted=now();log(s,'开始新题独立写作');}s.stage='transfer';return '';}
 function lockTransferPlan(s,prompt){if(!s.independentStarted)return '请先开始新题独立写作。';if(s.transferPlan)return '';const e=planError(s.transfer,prompt);if(e)return e;s.transferPlan={keywords:copy(s.transfer.keywords),outline:s.transfer.outline,focus:s.transfer.focus,at:now()};log(s,'保存新题独立提纲');return '';}
 function submitTransfer(s){if(!s.transferPlan)return '请先保留新题提纲，再开始作文。';if(s.transfer.mode==='type'&&!s.transfer.essay.trim())return '请先写好作文。';if(s.transfer.mode==='paper'&&!s.transfer.photos.length)return '请上传手写作文照片，才能把作品归入档案。';s.submissions.push({essay:s.transfer.essay,photos:copy(s.transfer.photos),mode:s.transfer.mode,at:now()});s.stage='record';log(s,'保存新题完整作文');return '';}
 function validateRecord(s){
  const text=(v,n=40000)=>typeof v==='string'&&v.length<=n;
  const arr=(v,n)=>Array.isArray(v)&&v.length<=n;
  const plan=p=>p&&arr(p.keywords,30)&&p.keywords.every(k=>text(k,200))&&text(p.outline)&&text(p.focus);
  if(!s||s.version!==4||!text(s.id,150)||!text(s.createdAt,100)||!text(s.updatedAt,100)||!['initial','learn','transfer','record'].includes(s.stage)||!text(s.name,100))return false;
  if(!plan(s.initial)||!plan(s.revised)||!plan(s.transfer)||!(s.first===null||plan(s.first))||!(s.transferPlan===null||plan(s.transferPlan)))return false;
  if(!text(s.revised.body)||!text(s.revised.evidence)||!arr(s.revised.reasons,10)||!s.revised.reasons.every(x=>text(x,100))||!text(s.transfer.essay)||!text(s.transfer.reflection,5000)||!['paper','type'].includes(s.transfer.mode))return false;
  const photo=p=>p&&text(p.name,200)&&text(p.data,1500000)&&/^data:image\/jpeg;base64,[A-Za-z0-9+/=]+$/.test(p.data);
  if(!arr(s.transfer.photos,6)||!s.transfer.photos.every(photo)||!arr(s.revisions,50)||!s.revisions.every(r=>plan(r)&&text(r.at,100)&&text(r.body)&&text(r.evidence)&&arr(r.reasons,10)&&r.reasons.every(x=>text(x,100))))return false;
  if(!arr(s.submissions,30)||!s.submissions.every(x=>text(x.at,100)&&text(x.essay)&&['paper','type'].includes(x.mode)&&arr(x.photos,6)&&x.photos.every(photo)))return false;
  if(!arr(s.feedback,30)||!s.feedback.every(validFeedback)||!arr(s.events,10000)||!s.events.every(e=>text(e.at,100)&&text(e.type,500)))return false;
  const c=s.compare;if(!c||![null,'a','b'].includes(c.selected)||![null,'a','b'].includes(c.first)||!Number.isInteger(c.tries)||c.tries<0||c.tries>100||typeof c.correct!=='boolean'||typeof c.revealed!=='boolean'||!Number.isFinite(c.until))return false;
  if(typeof s.modelOpened!=='boolean'||!(s.independentStarted===null||text(s.independentStarted,100))||!Number.isInteger(s.returnVisits)||s.returnVisits<0)return false;
  if((s.revisions.length&&!s.first)||(s.transferPlan&&!s.independentStarted)||(s.submissions.length&&!s.transferPlan))return false;
  if(s.study!==undefined&&!validStudy(s.study))return false;
  return true;
 }
 function validFeedback(f){return !!f&&typeof f.id==='string'&&f.id.length<150&&typeof f.at==='string'&&f.at.length<100&&['本题学习','新题独写'].includes(f.target)&&typeof f.evidence==='string'&&f.evidence.length<=5000&&typeof f.next==='string'&&f.next.length<=5000&&typeof f.dimension==='string'&&f.dimension.length<=100;}
 root.HWTModel={blankStudy,study,caseState,checkCase,finishCase,validStudy,copy,now,uid,fresh,log,planError,lockFirst,checkCompare,lockRevision,beginTransfer,lockTransferPlan,submitTransfer,validateRecord,validFeedback};
})(typeof window==='undefined'?globalThis:window);
