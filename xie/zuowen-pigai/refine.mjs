// Bounds come from the authenticated server; canvas crops the actual submitted image.
export async function cropTargets(source,targets){
 if(!targets.length)return [];
 const img=new Image();img.crossOrigin='anonymous';img.src=source;await img.decode();
 return targets.map(t=>{
  const [x,y,w,h]=t.rect,sx=x/100*img.naturalWidth,sy=y/100*img.naturalHeight,sw=w/100*img.naturalWidth,sh=h/100*img.naturalHeight;
  const canvas=document.createElement('canvas'),scale=Math.min(2,1200/Math.max(sw,sh));canvas.width=Math.max(1,Math.round(sw*scale));canvas.height=Math.max(1,Math.round(sh*scale));
  const context=canvas.getContext('2d');context.fillStyle='#fff';context.fillRect(0,0,canvas.width,canvas.height);context.drawImage(img,sx,sy,sw,sh,0,0,canvas.width,canvas.height);
  return {id:t.id,rect:t.rect,image:canvas.toDataURL('image/jpeg',.9)};
 });
}
