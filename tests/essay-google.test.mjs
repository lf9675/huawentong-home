import test from 'node:test';import assert from 'node:assert/strict';
const env={SUPABASE_URL:'https://db.invalid',SUPABASE_SERVICE_ROLE_KEY:'test-only',GOOGLE_CLOUD_VISION_API_KEY:'vision-test-only',GEMINI_API_KEY:'gemini-test-only'};
globalThis.Deno={env:{get:key=>env[key]},serve:()=>{}};
const {handle}=await import('../supabase/functions/hwt-essay/index.ts');
const job={id:crypto.randomUUID(),status:'draft',input:{pageCount:1},result:{}};
const requests=[];let mode='ok';
globalThis.fetch=async(url,options={})=>{
 const body=options.body?JSON.parse(options.body):null;requests.push({url,options,body});
 if(url.includes('hwt_take_rate'))return Response.json(true);
 if(url.includes('access_codes?code_hash='))return Response.json([{id:1,is_active:1,expiry:'2100-01-01',exam_level:'HCL'}]);
 if(url.includes('hwt_essay_job'))return Response.json(body.p_action==='patch'?{...job,result:body.p_data.patch}:job);
 if(url==='https://vision.googleapis.com/v1/images:annotate'){
  if(mode==='error')return Response.json({error:{message:'PRIVATE_DATA',code:403}},{status:403});
  return Response.json({responses:[{fullTextAnnotation:{text:'原字',pages:[{width:100,height:200,blocks:[]}]}}]});
 }
 if(url.startsWith('https://generativelanguage.googleapis.com/'))return Response.json({candidates:[{finishReason:'STOP',content:{parts:[{text:'{"ok":true}'}]}}]});
 throw Error('Unexpected network destination');
};
const call=(action,extra={})=>handle(new Request('https://site.invalid',{method:'POST',body:JSON.stringify({action,code:'HW-TEST-TEST',id:job.id,...extra})}));
test('authenticated OCR sends only the JPEG to Vision, keeps image identity and hides upstream credentials',async()=>{
 const r=await call('ocr',{page:0,image:'data:image/jpeg;base64,YWJj'});assert.equal(r.status,200);const data=await r.json();assert.equal(data.result.ocr_0.provider,'Google Cloud Vision');assert.equal(data.result.ocr_0.imageHash.length,64);
 const upstream=requests.find(r=>r.url.startsWith('https://vision.'));assert.equal(upstream.body.requests[0].image.content,'YWJj');assert.equal(upstream.body.requests[0].features[0].type,'DOCUMENT_TEXT_DETECTION');assert.equal(upstream.options.headers['x-goog-api-key'],'vision-test-only');assert(!JSON.stringify(data).includes('test-only'));
});
test('Gemini connection probe parses actual response shape; failed Vision calls never fall back or leak upstream data',async()=>{
 let r=await call('check_grading');assert.equal(r.status,200);assert.equal((await r.json()).ready,true);
 mode='error';r=await call('ocr',{page:0,image:'data:image/jpeg;base64,YWJj'});assert.equal(r.status,502);const d=await r.json();assert(d.error.includes('Google Cloud Vision'));assert(!d.error.includes('PRIVATE_DATA'));assert(!requests.some(r=>/bigmodel|deepseek/.test(r.url)));
});
