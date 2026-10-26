function showStorageWarning(){const n=$('#storageNotice');if(n)n.hidden=false;}
let lastExport=null,lastURL='';
function download(filename,content,type){
 const blob=new Blob([content],{type});if(lastURL)URL.revokeObjectURL(lastURL);
 lastURL=URL.createObjectURL(blob);lastExport={filename,blob,type};
 const box=$('#exportFallback');box.hidden=false;$('#exportText').value=content;
 const open=$('#openExport');open.href=lastURL;open.download=filename;
 const share=$('#shareExport');share.hidden=!(navigator.canShare&&navigator.canShare({files:[new File([blob],filename,{type})]}));
 share.onclick=async()=>{try{await navigator.share({files:[new File([lastExport.blob],lastExport.filename,{type:lastExport.type})]});}catch(err){if(err.name!=='AbortError')$('#importStatus').textContent='Share unavailable. 请使用打开或复制内容。';}};
 const a=document.createElement('a');a.href=lastURL;a.download=filename;document.body.appendChild(a);a.click();a.remove();
}
function validateRecord(s){
 const fail=()=>{throw Error('Not a compatible Chidao record（不是兼容的迟到备份）');};
 if(!s||Array.isArray(s)||s.version!==D.version||!s.identity||!s.answers||Array.isArray(s.answers))fail();
 if(!Number.isInteger(s.readP)||s.readP<1||s.readP>D.paragraphs.length||![1,2].includes(s.lesson))fail();
 for(const k of ['name','class','number'])if(typeof s.identity[k]!=='string'||s.identity[k].length>200)fail();
 for(const l of [1,2])if(!Number.isInteger(s.taskAt?.[l])||s.taskAt[l]<0||s.taskAt[l]>=tlist(l).length)fail();
 for(const [id,a] of Object.entries(s.answers)){
  const t=ts.find(t=>t.id===id);if(!t||!a||!Array.isArray(a.selection)||!Array.isArray(a.order)||!Array.isArray(a.attempts)||typeof a.response!=='string'||a.response.length>10000||typeof a.revealed!=='boolean'||typeof a.completedAt!=='string')fail();
  for(const list of [a.selection,a.order]){if(list.length>4||new Set(list).size!==list.length||list.some(n=>!Number.isInteger(n)||n<0||n>=(t.options?.length||0)))fail();}
  if(a.attempts.length>2000||a.attempts.some(v=>!v||typeof v.at!=='string'||typeof v.answer!=='string'||v.answer.length>10000||![true,false,null].includes(v.correct)))fail();
 }
}
