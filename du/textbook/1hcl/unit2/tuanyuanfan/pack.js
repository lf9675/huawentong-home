(()=>{
 const link=document.querySelector('#downloadPack'),status=document.querySelector('#packStatus');let busy=false,url='';
 link.addEventListener('click',async e=>{
  if(url)return;e.preventDefault();if(busy)return;busy=true;link.setAttribute('aria-disabled','true');
  try{
   status.textContent='正在准备整套资料，请稍候……';
   const response=await fetch('downloads/resource-pack.json',{cache:'no-store'});if(!response.ok)throw Error('manifest');
   const manifest=await response.json(),parts=[];
   for(let i=0;i<manifest.parts.length;i++){
    status.textContent='正在准备资料 '+(i+1)+' / '+manifest.parts.length+'……';
    const part=manifest.parts[i],r=await fetch(part.url,{cache:'no-store'});if(!r.ok)throw Error('download');
    const buffer=await r.arrayBuffer();if(buffer.byteLength!==part.bytes)throw Error('size');parts.push(buffer);
   }
   const blob=new Blob(parts,{type:'application/zip'});if(blob.size!==manifest.bytes)throw Error('size');
   if(globalThis.crypto?.subtle){const hash=await crypto.subtle.digest('SHA-256',await blob.arrayBuffer());const hex=Array.from(new Uint8Array(hash),b=>b.toString(16).padStart(2,'0')).join('');if(hex!==manifest.sha256)throw Error('checksum')}
   url=URL.createObjectURL(blob);link.href=url;link.textContent='保存完整资源包 ZIP';status.textContent='资料已准备好。若下载没有开始，请点“保存完整资源包”。';link.click();
  }catch{status.textContent='下载中断，请再试一次；也可分别下载上方资料。';link.textContent='重试整套下载'}
  finally{busy=false;link.removeAttribute('aria-disabled')}
 });
 window.addEventListener('pagehide',()=>{if(url){URL.revokeObjectURL(url);url='';link.href='#';link.textContent='下载整套 ZIP';status.textContent=''}});
})();
