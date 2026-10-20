/* Hosted assets are kept below the per-file size limit; the user gets one ZIP. */
(()=>{const button=document.querySelector('#downloadPack'),status=document.querySelector('#packStatus');
const hash=async data=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',data))).map(x=>x.toString(16).padStart(2,'0')).join('');
async function download(manifest,button){button.disabled=true;let url;try{
 status.textContent='正在准备整套配套……';
 const response=await fetch('downloads/'+manifest);if(!response.ok)throw Error('清单暂时无法读取');const m=await response.json();
 const parts=[];let total=0;
 for(let i=0;i<m.parts.length;i++){const p=m.parts[i];status.textContent=`正在下载 ${i+1} / ${m.parts.length}，请稍候……`;const r=await fetch('downloads/'+p.file);if(!r.ok)throw Error('部分资源下载失败');const a=await r.arrayBuffer();if(a.byteLength!==p.bytes||await hash(a)!==p.sha256)throw Error('文件校验未通过，请重试');parts.push(a);total+=a.byteLength;}
 if(total!==m.bytes)throw Error('文件不完整');const blob=new Blob(parts,{type:m.mime||'application/zip'});if(await hash(await blob.arrayBuffer())!==m.sha256)throw Error('整套文件校验未通过');url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=m.name;document.body.appendChild(a);a.click();a.remove();status.textContent='文件已准备好，请在浏览器下载列表中保存。ZIP请先解压再使用。';setTimeout(()=>URL.revokeObjectURL(url),60000);
 }catch(e){status.textContent='下载未完成：'+e.message+'。可重试，或分别下载上方的PPT、教师方案和互动HTML。';if(url)URL.revokeObjectURL(url)}finally{button.disabled=false}}
button.onclick=()=>download('package-manifest.json',button);const offline=document.querySelector('#downloadOffline');offline.onclick=()=>download('offline-manifest.json',offline);
})();
