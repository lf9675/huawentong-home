(()=>{
const status=document.querySelector('#packageStatus'),decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function hash(b){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',b)),x=>x.toString(16).padStart(2,'0')).join('')}
async function get(p){const r=await fetch(p.file);if(!r.ok)throw Error();const b=await r.arrayBuffer();if(b.byteLength!==p.bytes||await hash(b)!==p.sha256)throw Error('资料校验失败');return b}
for(const[id,key]of [['downloadPackage','package'],['downloadPpt','pptx'],['downloadOffline','offline']])document.querySelector('#'+id).onclick=async function(){
 this.disabled=true;try{
  const m=await fetch('downloads/'+key+'-manifest.json').then(r=>{if(!r.ok)throw Error();return r.json()}),parts=[];
  for(let i=0;i<m.parts.length;i++){
   status.textContent='下载中 '+(i+1)+' / '+m.parts.length;const p=m.parts[i];
   if(p.header)parts.push(decode(p.header));
   if(p.segments){for(const seg of p.segments)parts.push(await get(seg))}else parts.push(await get(p));
  }
  if(m.tail)parts.push(decode(m.tail));
  const blob=new Blob(parts,{type:key==='pptx'?'application/vnd.openxmlformats-officedocument.presentationml.presentation':'application/zip'});
  if(blob.size!==m.bytes||await hash(await blob.arrayBuffer())!==m.sha256)throw Error('资料校验失败');
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=m.filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);status.textContent='完整文件已准备好，请保存。';
 }catch(e){status.textContent='下载未完成，请重试。'+(e.message==='资料校验失败'?e.message:'')}finally{this.disabled=false}
};
})();
