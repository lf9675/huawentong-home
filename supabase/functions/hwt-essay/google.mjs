// Only OCR-supplied polygons are used for geometry; never infer character width.
function rectangle(poly,width,height){
 const v=poly?.vertices;if(!Array.isArray(v)||v.length!==4)return null;
 const points=v.map(p=>[p.x===undefined?0:p.x,p.y===undefined?0:p.y]);
 if(!points.every(p=>p.every(Number.isFinite)))return null;
 const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);const b=[Math.min(...xs),Math.min(...ys),Math.max(...xs),Math.max(...ys)];
 return b[0]>=0&&b[1]>=0&&b[2]<=width&&b[3]<=height&&b[2]>b[0]&&b[3]>b[1]?b:null;
}
export function visionResult(response){
 const annotation=response?.fullTextAnnotation,pages=annotation?.pages;
 if(!annotation?.text?.trim())throw Error('没有识别到文字，请检查页面方向和清晰度。');
 if(!Array.isArray(pages)||pages.length!==1)throw Error('识别服务没有返回完整页面，请重试。');
 const {width,height}=pages[0];if(!(width>0&&height>0&&Number.isFinite(width)&&Number.isFinite(height)))throw Error('识别服务没有返回有效尺寸，请重试。');
 const elements=[];let lowConfidence=0;
 for(const block of pages[0].blocks||[])for(const paragraph of block.paragraphs||[])for(const word of paragraph.words||[]){
  const chars=(word.symbols||[]).map(s=>{if(Number.isFinite(s.confidence)&&s.confidence<.8)lowConfidence++;return {text:s.text||'',bbox_2d:rectangle(s.boundingBox,width,height)};});
  elements.push({index:elements.length,label:'text',content:chars.map(c=>c.text).join(''),bbox_2d:rectangle(word.boundingBox,width,height),char_boxes:chars});
 }
 return {text:annotation.text.trim(),layout:{width,height,coordinate_space:'pixel',elements},provider:'Google Cloud Vision',lowConfidence};
}
export function geminiRequest(system,user,maxTokens){
 return {systemInstruction:{parts:[{text:system}]},contents:[{role:'user',parts:[{text:typeof user==='string'?user:JSON.stringify(user)}]}],generationConfig:{maxOutputTokens:Math.max(2048,maxTokens),responseFormat:{text:{mimeType:'application/json'}}}};
}
export function geminiResult(response){
 const candidate=response?.candidates?.[0];
 if(candidate?.finishReason!=='STOP')throw Error('Gemini 输出未完整完成，请重试此步骤。');
 const text=(candidate.content?.parts||[]).filter(p=>!p.thought).map(p=>p.text||'').join('');
 try{const data=JSON.parse(text);if(!data||typeof data!=='object'||Array.isArray(data))throw Error();return data;}catch{throw Error('Gemini 返回格式不完整，请重试此步骤。');}
}
