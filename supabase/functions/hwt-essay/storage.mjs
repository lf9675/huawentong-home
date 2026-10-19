const BUCKET='hwt-essay-pages';
const fail=()=>{throw Object.assign(Error('原图保存或读取暂时失败，请重试此步骤。'),{status:503});};
async function storage(path,options={}){
 const key=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'),url=Deno.env.get('SUPABASE_URL');
 const r=await fetch(url+'/storage/v1/'+path,{...options,headers:{apikey:key,Authorization:'Bearer '+key,...options.headers},signal:AbortSignal.timeout(20000)});
 if(!r.ok)fail();return r;
}
export async function savePage(id,page,data){
 const raw=atob(data.slice(data.indexOf(',')+1)),bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));
 const path=`${id}/${page}.jpg`;
 await storage('object/'+BUCKET+'/'+path,{method:'POST',headers:{'Content-Type':'image/jpeg','x-upsert':'true'},body:bytes});
 return path;
}
export async function pageData(id,page){
 const r=await storage(`object/authenticated/${BUCKET}/${id}/${page}.jpg`),bytes=new Uint8Array(await r.arrayBuffer());let str='';
 for(let i=0;i<bytes.length;i+=8192)str+=String.fromCharCode(...bytes.subarray(i,i+8192));
 return 'data:image/jpeg;base64,'+btoa(str);
}
export async function pageUrls(job){
 return Promise.all(Array.from({length:job.input.pageCount},async(_,i)=>{
  if(!job.result['ocr_'+i]?.imagePath)return null;
  const r=await storage(`object/sign/${BUCKET}/${job.id}/${i}.jpg`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({expiresIn:3600})});
  const d=await r.json();return Deno.env.get('SUPABASE_URL')+'/storage/v1'+d.signedURL;
 }));
}
