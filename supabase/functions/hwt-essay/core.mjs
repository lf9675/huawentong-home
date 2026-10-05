// Geometry comes only from OCR boxes. Never divide a region uniformly into characters.
export const norm = x => String(x ?? '').replace(/\s/g, '');
export function span(text, quote, left='', right='', lo=0, hi=text.length) {
  quote=norm(quote);left=norm(left);right=norm(right);if(!quote)return null;
  const hits=[];let p=text.indexOf(quote,lo);
  while(p>=0 && p+quote.length<=hi){
    if((!left||text.slice(Math.max(0,p-left.length),p)===left)&&(!right||text.slice(p+quote.length,p+quote.length+right.length)===right))hits.push([p,p+quote.length]);
    p=text.indexOf(quote,p+1);
  }
  return hits.length===1?hits[0]:null;
}
export function chunks(pages) {
  const text=pages.map(norm).join(''),out=[];
  for(let start=0;start<text.length;start+=500){const end=Math.min(start+600,text.length);out.push({start,end,text:text.slice(start,end)});if(end===text.length)break;}
  return out;
}
function box(item, layout){
 const b=item?.bbox_2d;if(!Array.isArray(b)||b.length!==4||!b.every(Number.isFinite))return null;
 let [x,y,r,bottom]=b;const space=item.coordinate_space||layout.coordinate_space;
 if(space==='pixel'){if(!(layout.width>0&&layout.height>0))return null;x/=layout.width;r/=layout.width;y/=layout.height;bottom/=layout.height;}
 else if(space==='normalized_1000'){x/=1000;y/=1000;r/=1000;bottom/=1000;}
 else if(space!=='normalized')return null;
 if(!(x>=0&&y>=0&&r<=1&&bottom<=1&&r>x&&bottom>y))return null;
 return [x*100,y*100,(r-x)*100,(bottom-y)*100].map(v=>Math.round(v*10000)/10000);
}
export function locate(source, range, layout){
 if(!layout)return null;
 const items=(layout.elements||[]).flat().filter(x=>['text','formula','doc_title','paragraph_title'].includes(x.label)).sort((a,b)=>(a.index||0)-(b.index||0));
 const text=items.map(x=>norm(x.content)).join('');source=norm(source);
 const s=text===source?range:span(text,source.slice(...range),source.slice(Math.max(0,range[0]-6),range[0]),source.slice(range[1],range[1]+6));
 if(!s)return null;let offset=0,precise=true,covered=0;const rects=[];
 for(const item of items){
  const t=norm(item.content),lo=Math.max(s[0],offset),hi=Math.min(s[1],offset+t.length);
  if(lo<hi){
   const chars=item.char_boxes||[];const bs=chars.map(c=>box(c,layout));
   if(chars.map(c=>norm(c.text)).join('')===t&&chars.length===t.length&&chars.every(c=>norm(c.text).length===1)&&bs.every(Boolean))rects.push(...bs.slice(lo-offset,hi-offset));
   else{const b=box(item,layout);if(!b)return null;rects.push(b);precise=false;}
   covered+=hi-lo;
  }offset+=t.length;
 }
 return covered===s[1]-s[0]?{rects,precision:precise?'character':'region'}:null;
}
export function ledger(pages, findings, layouts=[]){
 const full=pages.map(norm).join(''),seen=new Set(),out=[];
 for(const finding of findings){
  const s=span(full,finding.quote,finding.anchor_left,finding.anchor_right,finding.start??0,finding.end??full.length);
  const key=JSON.stringify([s||['unlocated',out.length],norm(finding.quote),finding.fix]);if(seen.has(key))continue;seen.add(key);
  const marks=[];let offset=0;
  if(s)pages.forEach((p,i)=>{const n=norm(p).length,lo=Math.max(offset,s[0]),hi=Math.min(offset+n,s[1]);if(lo<hi){const pos=locate(p,[lo-offset,hi-offset],layouts[i]);marks.push({page:i,...(pos||{rects:[],precision:'pending'})});}offset+=n;});
  out.push({...finding,id:'issue-'+(out.length+1),span:s,marks,uncertain:!!finding.uncertain||!s,location:!s||marks.some(m=>m.precision==='pending')?'pending':marks.some(m=>m.precision==='region')?'region':'character'});
 }
 return out;
}
export function validRect(r){return Array.isArray(r)&&r.length===4&&r.every(Number.isFinite)&&r[0]>=0&&r[1]>=0&&r[2]>0&&r[3]>0&&r[0]+r[2]<=100&&r[1]+r[3]<=100;}
