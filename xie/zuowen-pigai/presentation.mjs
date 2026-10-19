// Shared by the screen and PDF: show source evidence next to a brief diagnosis.
const normal=s=>String(s||'').replace(/\s/g,'');
export const plainExample=s=>String(s||'').replace(/【(?:动作|行动|心理|细节|对话|环境|分析|铺垫|抒情|点题|语言|神态)】/g,'');
export const verdictLabel=s=>({met:'已写清',thin:'还没写清',missing:'缺少',off_focus:'偏离重点',adequate:'已写清',weak:'还没写清',off_topic:'感悟偏题'})[s]||'对照原文';
export function emphasisParts(text,phrases=[]){
 text=String(text||'');const ranges=[];
 for(const p of phrases||[]){if(typeof p!=='string'||!p)continue;let start=0;while((start=text.indexOf(p,start))!==-1){ranges.push([start,start+p.length]);start+=p.length;}}
 ranges.sort((a,b)=>a[0]-b[0]);const merged=[];for(const r of ranges){const last=merged.at(-1);if(last&&r[0]<=last[1])last[1]=Math.max(last[1],r[1]);else merged.push(r);}
 const out=[];let cursor=0;for(const [a,b]of merged){if(a>cursor)out.push({text:text.slice(cursor,a),bold:false});out.push({text:text.slice(a,b),bold:true});cursor=b;}if(cursor<text.length)out.push({text:text.slice(cursor),bold:false});return out;
}
export function problemPhrases(card={}){
 const t=String(card.judgement||''),phrases=(card.emphasis||[]).filter(x=>typeof x==='string'&&x&&t.includes(x));
 if(phrases.length&&phrases.every(x=>x.length<=Math.max(12,t.length*.65)&&!/[，。；]/.test(x)))return phrases;
 const clauses=t.split(/[，。；]/).map(x=>x.replace(/^(但|然而|不过)/,'')).filter(Boolean),strongest=clauses.find(x=>/未能|没有|偏离|削弱|脱离/.test(x));
 return strongest?[strongest.replace(/的主题$|的题目要求$/,'')]:clauses.filter(x=>/不够|不足|偏向|偏重|略写|一笔带过|太多|偏移/.test(x)).slice(-2);
}
const excerpt=t=>(String(t||'').match(/[^。！？]+[。！？]?/g)||[String(t||'')]).slice(0,2).join('');
export function citedParagraphs(text,count){
 const ids=new Set(),add=n=>{if(Number.isInteger(n)&&n>=1&&n<=count)ids.add(n);};
 for(const m of String(text||'').matchAll(/第?(\d+)段?\s*(?:到|至|[-—～~])\s*第?(\d+)段/g)){const a=Number(m[1]),b=Number(m[2]);if(b>=a&&b-a<count)for(let n=a;n<=b;n++)add(n);}
 for(const m of String(text||'').matchAll(/第(\d+(?:[、，,和及与]\d+)*)段/g))for(const n of m[1].split(/[、，,和及与]/))add(Number(n));
 return [...ids].sort((a,b)=>a-b);
}
export function evidenceRows(f,kind){
 const r=f.overall_review||{},card=kind==='ending'?r.ending_reflection:r.keyword_detail,ps=f.paragraph_feedback||[];
 if(!card)return [];
 const complete=rows=>{
  if(kind!=='ending')for(const id of citedParagraphs(card.evidence,ps.length)){if(rows.some(x=>x.paragraph===id))continue;const p=ps[id-1];rows.push({paragraph:id,quote:excerpt(p.original_text),keyword:'详写重点',status:card.status==='off_focus'?'off_focus':card.status==='aligned'?'met':'thin',problem:card.judgement,action:card.suggestion,full_text:p.original_text,legacy:true});}
  return rows.sort((a,b)=>(a.paragraph||Infinity)-(b.paragraph||Infinity));
 };
 if(Array.isArray(card.evidence_rows)&&card.evidence_rows.length){
  return complete(card.evidence_rows.filter(x=>{const p=ps[x.paragraph-1];return p&&(x.quote?normal(p.original_text).includes(normal(x.quote)):x.status==='missing');}));
 }
 if(kind==='ending')return (card.paragraphs||[]).flatMap(id=>{const p=ps[id-1];return p?[{paragraph:id,quote:excerpt(p.original_text),keyword:'结尾抒情议论',status:card.status,problem:p.status==='needs_revision'?p.why_and_how||card.judgement:card.judgement,action:p.status==='needs_revision'?p.why_and_how||card.suggestion:card.suggestion,legacy:true,full_text:p.original_text}]:[];});
 const rows=(card.keywords||[]).map(k=>{const id=(k.paragraphs||[]).find(id=>normal(ps[id-1]?.original_text).includes(normal(k.quote)))||(k.paragraphs||[])[0];return {paragraph:id||null,quote:k.quote||'',keyword:k.keyword,status:k.verdict,problem:k.verdict==='met'?'已经体现：'+k.meaning:'要写清：'+k.meaning,action:k.verdict==='met'?'保留这部分。':ps[id-1]?.why_and_how||card.suggestion,legacy:true};});
 for(const id of card.compress_paragraphs||[]){const p=ps[id-1];if(!p)continue;rows.push({paragraph:id,quote:excerpt(p.original_text),keyword:'详写重点',status:'off_focus',problem:p.why_and_how||card.judgement,action:'压缩这部分。'+(card.suggestion||''),legacy:true,full_text:p.original_text});}
 return complete(rows);
}
export function focusFlow(f,kind){
 const r=f.overall_review||{},card=kind==='ending'?r.ending_reflection:r.keyword_detail;
 if(card?.flow?.length)return card.flow;
 if(kind==='ending')return ['回扣经历','写出感受','说明扣题的道理'].map(label=>({label,status:'guide',paragraphs:[]}));
 return (card?.keywords||[]).map(x=>({label:x.keyword,status:x.verdict,paragraphs:x.paragraphs||[]}));
}
export function exampleParts(text,notes=[]){
 text=plainExample(text);const ranges=[];
 for(const note of notes||[]){if(!note?.quote||!note.keyword||!note.why)continue;const quote=plainExample(note.quote),a=text.indexOf(quote);if(a<0||text.indexOf(quote,a+quote.length)>=0)continue;ranges.push({a,b:a+quote.length,note});}
 ranges.sort((a,b)=>a.a-b.a);const out=[];let cursor=0;
 for(const r of ranges){if(r.a<cursor)continue;if(r.a>cursor)out.push({text:text.slice(cursor,r.a)});out.push({text:text.slice(r.a,r.b),note:r.note});cursor=r.b;}if(cursor<text.length)out.push({text:text.slice(cursor)});return out;
}
