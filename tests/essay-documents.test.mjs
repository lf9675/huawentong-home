import test from 'node:test';import assert from 'node:assert/strict';
import {fileKind,pageLimit,fittedSize,importDocuments,renderData,releasePages} from '../xie/zuowen-pigai/documents.mjs';
import {visionResult,geminiRequest,geminiResult} from '../supabase/functions/hwt-essay/google.mjs';
import {locate} from '../xie/zuowen-pigai/core.mjs';
test('PDF and image limits count actual pages, including mixed uploads',()=>{
 assert.equal(fileKind({type:'application/pdf',name:'a',size:100}),'pdf');assert.equal(fileKind({type:'',name:'A.PDF',size:100}),'pdf');assert.equal(fileKind({type:'',name:'a.JPG',size:100}),'image');
 assert.throws(()=>fileKind({type:'text/html',name:'a.pdf',size:100}));assert.throws(()=>fileKind({type:'application/pdf',size:51*1024*1024}));assert.throws(()=>fileKind({type:'image/png',size:26*1024*1024}));
 pageLimit(3,3);assert.throws(()=>pageLimit(3,4));assert.throws(()=>pageLimit(0,7));assert.throws(()=>pageLimit(6,1));
 assert.deepEqual(fittedSize(4000,6000),{width:1600,height:2400,scale:.4});assert.throws(()=>fittedSize(Infinity,10));
});
const poly=(x,y,w,h)=>({vertices:[{...(x?{x}:{}),...(y?{y}:{})},{x:x+w,y},{x:x+w,y:y+h},{x,y:y+h}]});
function sample(){return {fullTextAnnotation:{text:'不可思意\n',pages:[{width:1000,height:2000,blocks:[{paragraphs:[{words:[{boundingBox:poly(0,0,400,100),symbols:[...'不可思意'].map((text,i)=>({text,boundingBox:poly(i*100,0,75,90),confidence:i===3?.7:.99}))}]}]}]}]}};}
test('Google preserves student spelling and uses true symbol boxes, including zero vertices',()=>{const result=visionResult(sample());assert.equal(result.text,'不可思意');assert.equal(result.lowConfidence,1);assert.deepEqual(locate(result.text,[3,4],result.layout),{precision:'character',rects:[[30,0,7.5,4.5]]});});
test('missing or invalid symbol geometry falls back to a real word region',()=>{const s=sample();delete s.fullTextAnnotation.pages[0].blocks[0].paragraphs[0].words[0].symbols[3].boundingBox;const r=visionResult(s);assert.equal(locate(r.text,[3,4],r.layout).precision,'region');s.fullTextAnnotation.pages[0].width=0;assert.throws(()=>visionResult(s));assert.throws(()=>visionResult({}));});
test('Gemini request keeps instructions separate and rejects truncation and thought text',()=>{const b=geminiRequest('rules',{essay:'student'},6000);assert.equal(b.systemInstruction.parts[0].text,'rules');assert.equal(b.generationConfig.responseFormat.text.mimeType,'application/json');assert.deepEqual(geminiResult({candidates:[{finishReason:'STOP',content:{parts:[{thought:true,text:'private thought'},{text:'{"complete":true}'}]}}]}),{complete:true});assert.throws(()=>geminiResult({candidates:[{finishReason:'MAX_TOKENS'}]}));});
