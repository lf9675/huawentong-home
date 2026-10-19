import test from 'node:test';import assert from 'node:assert/strict';
const env={SUPABASE_URL:'https://db.invalid',SUPABASE_SERVICE_ROLE_KEY:'test-only',GEMINI_API_KEY:'gemini-test-only',ZHIPU_API_KEY:'legacy-unused',DEEPSEEK_API_KEY:'legacy-unused',GOOGLE_CLOUD_VISION_API_KEY:'legacy-unused'};
globalThis.Deno={env:{get:key=>env[key]},serve:()=>{}};
const {handle,providerFailure}=await import('../supabase/functions/hwt-essay/index.ts');
const {geminiFailureInfo}=await import('../supabase/functions/hwt-essay/google.mjs');
const job={id:crypto.randomUUID(),status:'draft',input:{pageCount:1},result:{}};
const requests=[];let mode='ok';
globalThis.fetch=async(url,options={})=>{
 const body=options.body?JSON.parse(options.body):null;requests.push({url,options,body});
 if(url.includes('hwt_take_rate'))return Response.json(true);
 if(url.includes('access_codes?'))return Response.json([{id:1,is_active:1,expiry:'2100-01-01',exam_level:'HCL'}]);
 if(url.includes('hwt_essay_job'))return Response.json(body.p_action==='patch'?{...job,result:body.p_data.patch}:job);
 if(url.startsWith('https://generativelanguage.googleapis.com/')){
  // Google generateContent uses an enum here, unlike the inline image MIME string.
  if(body.generationConfig?.responseFormat?.text?.mimeType!=='APPLICATION_JSON')return Response.json({error:{code:400,message:"Invalid value at generation_config.response_format.text.mime_type: application/json"}},{status:400});
  for(const p of body.contents[0].parts)if(p.inlineData)assert.equal(p.inlineData.mimeType,'image/jpeg');
  if(mode==='error')return Response.json({error:{message:'PRIVATE_DATA',code:403}},{status:403});
  const data=body.contents[0].parts.some(p=>p.inlineData)?{complete:true,lines:[{text:'原字',paragraph_end:true,uncertain:false,box_2d:[0,0,100,100]}]}:{ok:true};
  return Response.json({candidates:[{finishReason:'STOP',content:{parts:[{text:JSON.stringify(data)}]}}]});
 }
 throw Error('Unexpected network destination: '+url);
};
const call=(action,extra={})=>handle(new Request('https://site.invalid',{method:'POST',body:JSON.stringify({action,code:'HW-TEST-TEST',id:job.id,...extra})}));
test('authenticated OCR sends JPEG to Gemini, preserves image identity and hides credentials',async()=>{
 const r=await call('ocr',{page:0,image:'data:image/jpeg;base64,YWJj'});assert.equal(r.status,200);const data=await r.json();assert.equal(data.result.ocr_0.provider,'Gemini');assert.equal(data.result.ocr_0.imageHash.length,64);assert.equal(data.result.ocr_0.layout.geometry_source,'model_estimate');
 const upstream=requests.find(r=>r.url.startsWith('https://generativelanguage.'));assert.equal(upstream.body.contents[0].parts[0].inlineData.data,'YWJj');assert.equal(upstream.options.headers['x-goog-api-key'],'gemini-test-only');assert(!JSON.stringify(data).includes('test-only'));
});
test('invalid JSON output enum is diagnosed without returning private provider content',async()=>{
 const error={error:{code:400,message:"Invalid value at 'generation_config.response_format.text.mime_type' (type.googleapis.com/google.ai.generativelanguage.v1beta.TextResponseFormat.MimeType), application/json PRIVATE_DATA"}};
 assert.deepEqual(geminiFailureInfo(error),{code:'400',category:'output_format_invalid',field:''});
 await assert.rejects(()=>providerFailure('ocr',Response.json(error,{status:400})),e=>e.status===502&&e.message.includes('output_format_invalid')&&!e.message.includes('PRIVATE_DATA'));
});
test('Gemini grading probe succeeds; provider errors never fall back or leak upstream content',async()=>{
 let r=await call('check_grading');assert.equal(r.status,200);assert.equal((await r.json()).ready,true);
 mode='error';r=await call('ocr',{page:0,image:'data:image/jpeg;base64,YWJj'});assert.equal(r.status,502);const d=await r.json();assert(d.error.includes('Gemini'));assert(!d.error.includes('PRIVATE_DATA'));assert(!requests.some(r=>/bigmodel|deepseek|vision.googleapis/.test(r.url)));mode='ok';
});
test('legacy keys alone cannot report ready or start paid work',async()=>{
 delete env.GEMINI_API_KEY;const start=requests.length;
 const health=await handle(new Request('https://site.invalid'));const data=await health.json();assert.deepEqual(data.services,{database:true,ocr:false,grading:false});assert.deepEqual(data.providers,{ocr:'Gemini',grading:'Gemini'});assert.equal(data.ready,false);
 for(const [action,extra] of [['create',{genre:'记叙文',pageCount:1}],['ocr',{page:0,image:'data:image/jpeg;base64,YWJj'}],['check_grading',{}]]){const r=await call(action,extra);assert.equal(r.status,503);assert((await r.json()).error.includes('GEMINI_API_KEY'));}
 assert(requests.slice(start).every(r=>r.url.startsWith('https://db.invalid/')));env.GEMINI_API_KEY='gemini-test-only';
});
