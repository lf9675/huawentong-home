import test from 'node:test';import assert from 'node:assert/strict';
import {validatePresentation,applyPresentation,presentationInput} from '../supabase/functions/hwt-essay/pedagogy.mjs';
import {evidenceRows,exampleParts,emphasisParts} from '../xie/zuowen-pigai/presentation.mjs';
import {summaryHtml,exampleHtml} from '../xie/zuowen-pigai/review.mjs';
const ps=[{id:1,text:'我决定试一试。'},{id:2,text:'我反复练习。我懂得了坚持。'}];
function fixture(){
 const common={judgement:'过程有写，但未写清尝试。',emphasis:['未写清尝试'],evidence:'不显示的旧依据',suggestion:'补出选择。'};
 const row=(id,keyword='勇敢尝试')=>({paragraph:id,quote:ps[id-1].text,keyword,status:'thin',problem:'只写决定，没有写出顾虑。',action:'补出为什么仍决定尝试。'});
 const note={quote:'我虽然害怕，还是举起了手。',keyword:'勇敢尝试',why:'仍然害怕，却主动选择接受机会。'};
 const k={...common,keywords:[{keyword:'勇敢尝试',meaning:'面对顾虑仍选择尝试',quote:ps[0].text,paragraphs:[1],verdict:'thin'}],expand_paragraphs:[1],compress_paragraphs:[2],evidence_rows:[row(1),row(2)],flow:[{label:'怕什么',status:'thin',paragraphs:[1]},{label:'怎样开始试',status:'thin',paragraphs:[1]}]};
 return {overall_review:{materials:common,detail_balance:common,keyword_detail:k,ending_reflection:{...common,status:'weak',paragraphs:[2],example:note.quote,example_notes:[note],evidence_rows:[row(2)],flow:k.flow}},paragraph_feedback:ps.map(p=>({original_text:p.text,status:'needs_revision',revised_top:note.quote+'我走上了台。',revision_notes:[note]}))};
}
test('new table covers both thin core and overlong supporting paragraphs',()=>{const f=fixture();validatePresentation(f,ps,{genre:'记叙文'});assert.equal(evidenceRows(f,'keyword').length,2);f.overall_review.keyword_detail.evidence_rows.pop();validatePresentation(f,ps,{genre:'记叙文'});const restored=f.overall_review.keyword_detail.evidence_rows.find(x=>x.paragraph===2);assert.equal(restored.quote,ps[1].text);assert.equal(restored.status,'off_focus');assert.equal(restored.from_paragraph_feedback,true);});
test('table quotes cannot refer to the wrong paragraph or invent evidence',()=>{const f=fixture();f.overall_review.keyword_detail.evidence_rows[0].quote=ps[1].text;assert.throws(()=>validatePresentation(f,ps,{genre:'记叙文'}),/引文/);assert.equal(evidenceRows(f,'keyword').length,1);});
test('keyword side notes must exactly match a unique non-overlapping example span',()=>{const f=fixture();f.paragraph_feedback[0].revision_notes[0]={quote:'我不再害怕。',keyword:'勇敢尝试',why:'错误引文'};assert.throws(()=>validatePresentation(f,ps,{genre:'记叙文'}),/示范原句/);assert(!exampleHtml(f.paragraph_feedback[0].revised_top,f.paragraph_feedback[0].revision_notes).includes('错误引文'));});
test('all original example characters remain with red keyword explanations in place',()=>{const t='我想了想。我虽然害怕，还是举起了手。我走上了台。',notes=fixture().paragraph_feedback[0].revision_notes;const parts=exampleParts(t,notes);assert.equal(parts.map(x=>x.text).join(''),t);assert.equal(parts.filter(x=>x.note).length,1);assert(exampleHtml(t,notes).includes('扣“勇敢尝试”'));});
test('summary emphasises the actual problem and escapes HTML instead of interpreting it',()=>{const f=fixture();f.overall_review.materials={...f.overall_review.materials,judgement:'选材真实，但未能充分支撑勇敢尝试。<img src=x>',emphasis:['未能充分支撑勇敢尝试']};const html=summaryHtml(f);assert(html.includes('<strong>未能充分支撑勇敢尝试</strong>'));assert(!html.includes('不显示的旧依据'));assert(html.includes('&lt;img src=x&gt;'));assert(html.includes('<strong>我反复练习。我懂得了坚持。</strong>'));assert(html.includes('focusFlow'));});
test('old records keep compression evidence, ending comments and source text available',()=>{const f=fixture();delete f.overall_review.keyword_detail.evidence_rows;delete f.overall_review.ending_reflection.evidence_rows;const rows=evidenceRows(f,'keyword');assert(rows.some(x=>x.paragraph===2&&x.quote.includes('反复练习')));assert(evidenceRows(f,'ending').some(x=>x.quote.includes('坚持')));});
test('emphasis preserves repeated and overlapping phrases without dropping characters',()=>{const t='没有扣题，没有扣题。';const parts=emphasisParts(t,['没有扣题','扣题']);assert.equal(parts.map(x=>x.text).join(''),t);assert.equal(parts.filter(x=>x.bold).length,2);});

test('missing display rows reuse the existing keyword finding and never invent source text',()=>{const f=fixture();f.overall_review.keyword_detail.evidence_rows=[];validatePresentation(f,ps,{genre:'记叙文'});const rows=f.overall_review.keyword_detail.evidence_rows;assert(rows.some(x=>x.keyword==='勇敢尝试'));assert(rows.every(x=>ps[x.paragraph-1].text.includes(x.quote)));});

test('formatting stage input excludes scores and language findings',()=>{const f=fixture();f.scores={total:40};f.paragraph_feedback[0].red_issues=[{original:'私密标记'}];const request=presentationInput(f,{prompt:'勇敢尝试',genre:'记叙文'},ps);assert(!JSON.stringify(request).includes('私密标记'));assert(!('scores' in request));assert.equal(request.paragraphs.length,2);});
test('formatting failure leaves the saved grade intact for a retry',()=>{const f=fixture(),before=JSON.stringify(f);assert.throws(()=>applyPresentation(f,{cards:{materials:{judgement:'短评'}}},ps,{genre:'记叙文'}));assert.equal(JSON.stringify(f),before);});
function stageFixture(){
 const f=fixture();f.scores={total:40};f.overall_review.keyword_detail.status='off_focus';f.overall_review.keyword_detail.actual_focus='反复练习';
 f.paragraph_feedback.forEach((p,i)=>Object.assign(p,{para_num:i+1,red_issues:[],structure_content_issues:[{problem:'关键选择写得太少',suggestion:'补出为什么决定试'}],why_and_how:'补出为什么决定试'}));
 const data={cards:structuredClone(f.overall_review),examples:f.paragraph_feedback.map(p=>({paragraph:p.para_num,revised_top:p.revised_top,revision_notes:p.revision_notes}))};return {f,data};
}
test('display merge cannot alter scores, focus verdict, original text, or language findings',()=>{const {f,data}=stageFixture();data.scores={total:0};data.cards.keyword_detail.status='aligned';data.examples[0].original_text='篡改原文';const out=applyPresentation(f,data,ps,{genre:'记叙文'});assert.equal(out.scores.total,40);assert.equal(out.overall_review.keyword_detail.status,'off_focus');assert.equal(out.paragraph_feedback[0].original_text,ps[0].text);assert.equal(f.presentation_version,undefined);assert.equal(out.presentation_version,1);});
test('presentation action saves a separate checkpoint, rejects bad quotes, and retries without regrading',async()=>{
 globalThis.Deno={env:{get:k=>({SUPABASE_URL:'https://db.invalid',SUPABASE_SERVICE_ROLE_KEY:'test-only',GEMINI_API_KEY:'test-only'})[k]},serve:()=>{}};
 const {handle}=await import('../supabase/functions/hwt-essay/index.ts');const {f,data}=stageFixture();
 const job={id:crypto.randomUUID(),status:'draft',input:{genre:'记叙文',mode:'grade',pageCount:1,prompt:'勇敢尝试'},result:{grade:f,pages:[ps.map(x=>x.text).join('\n\n')],presentation_required:true}};
 const saved=globalThis.fetch;let bad=true,ai=0,patches=0,complete=0;
 globalThis.fetch=async(url,opts={})=>{const b=opts.body?JSON.parse(opts.body):{};
  if(url.includes('hwt_take_rate'))return Response.json(true);
  if(url.includes('access_codes?'))return Response.json([{id:1,is_active:1,expiry:'2100-01-01',exam_level:'HCL'}]);
  if(url.includes('hwt_essay_job')){if(b.p_action==='patch'){patches++;Object.assign(job.result,b.p_data.patch);}if(b.p_action==='complete')complete++;return Response.json(job);}
  if(url.startsWith('https://generativelanguage.googleapis.com/')){ai++;assert(b.systemInstruction.parts[0].text.includes('已保存的教学判断'));const response=structuredClone(data);if(bad)response.cards.keyword_detail.evidence_rows[0].quote='虚构句子';return Response.json({candidates:[{finishReason:'STOP',content:{parts:[{text:JSON.stringify(response)}]}}]});}
  throw Error('unexpected request');
 };
 const call=action=>handle(new Request('https://site.invalid',{method:'POST',body:JSON.stringify({action,id:job.id,code:'HW-TEST-TEST'})}));
 try{let r=await call('finish');assert.equal(r.status,400);assert.equal(complete,0);r=await call('presentation');assert.equal(r.status,502);assert.equal(patches,0);assert.equal(job.result.grade.presentation_version,undefined);bad=false;r=await call('presentation');assert.equal(r.status,200);assert.equal(job.result.grade.presentation_version,1);assert.equal(job.result.presentation_required,false);assert.equal(job.result.grade.scores.total,40);await call('presentation');assert.equal(ai,2);assert.equal(complete,0);}finally{globalThis.fetch=saved;}
});
