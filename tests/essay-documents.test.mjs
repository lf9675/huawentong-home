import test from 'node:test';import assert from 'node:assert/strict';
import {fileKind,pageLimit,fittedSize} from '../xie/zuowen-pigai/documents.mjs';
import {geminiOcrRequest,geminiOcrResult,geminiRequest,geminiResult} from '../supabase/functions/hwt-essay/google.mjs';
import {locate,ledger} from '../xie/zuowen-pigai/core.mjs';
test('PDF and image limits count actual pages, including mixed uploads',()=>{
 assert.equal(fileKind({type:'application/pdf',name:'a',size:100}),'pdf');assert.equal(fileKind({type:'',name:'A.PDF',size:100}),'pdf');assert.equal(fileKind({type:'',name:'a.JPG',size:100}),'image');
 assert.throws(()=>fileKind({type:'text/html',name:'a.pdf',size:100}));assert.throws(()=>fileKind({type:'application/pdf',size:51*1024*1024}));assert.throws(()=>fileKind({type:'image/png',size:26*1024*1024}));
 pageLimit(3,3);assert.throws(()=>pageLimit(3,4));assert.throws(()=>pageLimit(0,7));assert.throws(()=>pageLimit(6,1));
 assert.deepEqual(fittedSize(4000,6000),{width:1600,height:2400,scale:.4});assert.throws(()=>fittedSize(Infinity,10));
});
const sample=()=>({complete:true,lines:[{text:'不可思意',paragraph_end:false,uncertain:false,box_2d:[100,200,150,800]},{text:'他□着我。',paragraph_end:true,uncertain:true,box_2d:[200,200,250,800]}]});
test('Gemini transcription preserves misspellings and reads documented y/x coordinate ordering',()=>{
 const r=geminiOcrResult(sample());assert.equal(r.text,'不可思意\n他□着我。');assert.deepEqual(r.uncertainLines,[2]);assert.equal(r.layout.geometry_source,'model_estimate');
 assert.deepEqual(locate(r.text,[3,4],r.layout),{precision:'region',rects:[[20,10,60,5]]});
 const a=ledger([r.text],[{quote:'□',fix:'核对原字'}],[r.layout])[0];assert.equal(a.uncertain,true);assert.equal(a.location,'region');
});
test('Gemini estimates never become measured character boxes and invalid boxes preserve text',()=>{
 const s=sample(),r=geminiOcrResult(s);r.layout.elements[0].char_boxes=[...'不可思意'].map((text,i)=>({text,bbox_2d:[200+i*100,100,250+i*100,150]}));assert.equal(locate(r.text,[3,4],r.layout).precision,'region');
 s.lines[0].box_2d=[100,200,50,800];const bad=geminiOcrResult(s);assert.equal(bad.text,r.text);assert.equal(locate(bad.text,[3,4],bad.layout),null);assert.equal(ledger([bad.text],[{quote:'意',fix:'议'}],[bad.layout]).length,1);
 for(const value of [null,[],[0,0,NaN,400],[-1,0,50,400],[0,0,1001,400]]){s.lines[0].box_2d=value;assert.equal(geminiOcrResult(s).layout.elements[0].bbox_2d,null);}
});
test('partial or malformed OCR output is rejected rather than silently omitting pages or lines',()=>{const s=sample();s.complete=false;assert.throws(()=>geminiOcrResult(s));s.complete=true;delete s.lines[0].text;assert.throws(()=>geminiOcrResult(s));assert.throws(()=>geminiOcrResult({complete:true,lines:[]}));});
test('compact generation schema still enforces page and coordinate limits at the boundary',()=>{
 const line=sample().lines[0];assert.throws(()=>geminiOcrResult({complete:true,lines:Array(251).fill(line)}));
 assert.throws(()=>geminiOcrResult({complete:true,lines:[{...line,text:'字'.repeat(5001)}]}));
 const r=geminiOcrResult({complete:true,lines:[{...line,box_2d:[0,0,100,100,200]}]});assert.equal(r.layout.elements[0].bbox_2d,null);assert.equal(r.text,line.text);
});
test('Gemini requests separate instructions from input and reject truncation/thought text',()=>{
 const b=geminiRequest('rules',{essay:'student'},6000);assert.equal(b.systemInstruction.parts[0].text,'rules');assert.equal(b.generationConfig.responseFormat.text.mimeType,'APPLICATION_JSON');
 const ocr=geminiOcrRequest('data:image/jpeg;base64,YWJj');assert.equal(ocr.contents[0].parts[0].inlineData.data,'YWJj');assert(ocr.generationConfig.responseFormat.text.schema.required.includes('lines'));
 assert.deepEqual(geminiResult({candidates:[{finishReason:'STOP',content:{parts:[{thought:true,text:'private thought'},{text:'{"complete":true}'}]}}]}),{complete:true});assert.throws(()=>geminiResult({candidates:[{finishReason:'MAX_TOKENS'}]}));
});
