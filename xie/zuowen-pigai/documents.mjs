// Files stay on this device until the student explicitly starts OCR.
export const MAX_PAGES=6, MAX_EDGE=2400;
const MB=1024*1024;
export function fileKind(file){
 const pdf=file.type==='application/pdf'||(!file.type&&/\.pdf$/i.test(file.name));
 const image=/^image\/(jpeg|png|webp)$/.test(file.type)||(!file.type&&/\.(jpe?g|png|webp)$/i.test(file.name));
 if(!pdf&&!image)throw Error('请选择 JPG、PNG、WebP 图片或 PDF 文件。');
 if(!file.size||file.size>(pdf?50:25)*MB)throw Error(pdf?'PDF 必须小于 50 MB。':'图片必须小于 25 MB。');
 return pdf?'pdf':'image';
}
export function pageLimit(current,added){if(!Number.isInteger(added)||added<1||current+added>MAX_PAGES)throw Error(`每篇作文最多 ${MAX_PAGES} 页（PDF 按实际页数计算）。请先拆分 PDF 或移除已有页面。`);}
export function fittedSize(width,height){
 if(!Number.isFinite(width)||!Number.isFinite(height)||width<=0||height<=0)throw Error('无法读取页面尺寸。');
 const scale=Math.min(1,MAX_EDGE/Math.max(width,height));return {width:Math.max(1,Math.round(width*scale)),height:Math.max(1,Math.round(height*scale)),scale};
}
export function releasePages(pages){for(const p of pages)p.bitmap?.close();}
export async function renderData(p){
 const {width:w,height:h}=fittedSize(p.bitmap.width,p.bitmap.height),swap=p.rotation%180!==0;
 const canvas=document.createElement('canvas');canvas.width=swap?h:w;canvas.height=swap?w:h;
 try{const ctx=canvas.getContext('2d');if(!ctx)throw Error('设备无法生成预览，请关闭其他页面后重试。');
 ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.translate(canvas.width/2,canvas.height/2);ctx.rotate(p.rotation*Math.PI/180);ctx.drawImage(p.bitmap,-w/2,-h/2,w,h);
 p.data=canvas.toDataURL('image/jpeg',.94);if(p.data.length>12500000)p.data=canvas.toDataURL('image/jpeg',.8);
 if(!p.data.startsWith('data:image/jpeg;base64,')||p.data.length>12500000)throw Error('页面无法转换，请缩小图片或重新扫描。');
 p.width=canvas.width;p.height=canvas.height;
 }finally{canvas.width=canvas.height=1;}
}
async function imagePage(file){
 let bitmap;try{bitmap=await createImageBitmap(file,{imageOrientation:'from-image'});}catch{throw Error('图片无法打开，请重新保存为 JPG 或 PNG。');}
 try{
 if(bitmap.width*bitmap.height>50000000)throw Error('照片像素过大，请先缩小。');
 // Release the large original after downsampling; keep rotation lossless on the working bitmap.
 const size=fittedSize(bitmap.width,bitmap.height);
 if(size.scale<1){const small=await createImageBitmap(bitmap,{resizeWidth:size.width,resizeHeight:size.height,resizeQuality:'high'});bitmap.close();bitmap=small;}
 const page={name:file.name,kind:'image',bitmap,rotation:0};await renderData(page);return page;
 }catch(e){bitmap.close();throw e;}
}
let pdfLibrary;
async function pdfjs(){
 if(!pdfLibrary)pdfLibrary=import('./vendor/pdfjs/pdf.min.mjs').then(lib=>{lib.GlobalWorkerOptions.workerSrc=new URL('./vendor/pdfjs/pdf.worker.min.mjs',import.meta.url).href;return lib;}).catch(()=>{pdfLibrary=null;throw Error('PDF 组件未能加载，请刷新页面再试。');});
 return pdfLibrary;
}
async function pdfPages(file,current,onProgress){
 const lib=await pdfjs(),base=new URL('./vendor/pdfjs/',import.meta.url).href;
 const task=lib.getDocument({data:new Uint8Array(await file.arrayBuffer()),isEvalSupported:false,enableXfa:false,cMapUrl:base+'cmaps/',cMapPacked:true,standardFontDataUrl:base+'standard_fonts/',wasmUrl:base+'wasm/'});
 const pages=[];
 try{const pdf=await task.promise;pageLimit(current,pdf.numPages);
 for(let i=1;i<=pdf.numPages;i++){
  onProgress(`正在展开 ${file.name}：第 ${i} / ${pdf.numPages} 页……`);
  const source=await pdf.getPage(i),unit=source.getViewport({scale:1});
  const viewport=source.getViewport({scale:MAX_EDGE/Math.max(unit.width,unit.height)}),canvas=document.createElement('canvas');
  canvas.width=Math.max(1,Math.round(viewport.width));canvas.height=Math.max(1,Math.round(viewport.height));
  let bitmap;
  try{await source.render({canvasContext:canvas.getContext('2d'),viewport,background:'rgb(255,255,255)'}).promise;
   bitmap=await createImageBitmap(canvas);const p={name:`${file.name} · 第 ${i} 页`,kind:'pdf',sourcePage:i,bitmap,rotation:0};await renderData(p);pages.push(p);bitmap=null;
  }finally{bitmap?.close();canvas.width=canvas.height=1;source.cleanup();}
 }
 return pages;
 }catch(e){releasePages(pages);if(e.name==='PasswordException')throw Error('PDF 有密码保护，请先解除密码后再上传。');if(e.name==='InvalidPDFException'||e.name==='MissingPDFException')throw Error('PDF 已损坏或格式不完整，请重新导出后上传。');throw e;
 }finally{await task.destroy();}
}
export async function importDocuments(files,{existingCount=0,onProgress=()=>{}}={}){
 const list=[...files],loaded=[];if(!list.length)return loaded;
 pageLimit(existingCount,list.length);list.forEach(fileKind);
 try{for(const file of list){onProgress(`正在准备 ${file.name}……`);
  if(fileKind(file)==='pdf')loaded.push(...await pdfPages(file,existingCount+loaded.length,onProgress));
  else{pageLimit(existingCount+loaded.length,1);loaded.push(await imagePage(file));}
 }return loaded;}catch(e){releasePages(loaded);throw e;}
}
