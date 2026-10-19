import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const workspaceDir=path.resolve(process.argv[2]);
const lessonDir=path.join(workspaceDir,'huawentong-home/du/textbook/2hcl/unit1/fang-feng-zheng');
const slides=JSON.parse(await fs.readFile(path.join(lessonDir,'slides.json'),'utf8'));
const L=JSON.parse(await fs.readFile(path.join(workspaceDir,'huawentong-home/tools/fang-feng-zheng/lesson.json'),'utf8'));
const pres=Presentation.create({slideSize:{width:1280,height:720}});
const kai='LXGW WenKai TC', song='Noto Serif CJK SC';
function wrap(s,width,size){const max=width/size;let line='',len=0,lines=[];for(const c of s){if(c==='\n'){lines.push(line);line='';len=0;continue}const v=/[\u0000-\u00ff]/.test(c)?.55:1;if(len+v>max){lines.push(line);line='';len=0}line+=c;len+=v}if(line)lines.push(line);return lines.join('\n')}
function text(slide,name,txt,x,y,w,h,{size=40,color='#243d37',font=kai,bold=false}={}){const shape=slide.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});shape.text=txt;shape.text.style={fontSize:size,typeface:font,color,bold,wrap:'word',insets:0,verticalAlignment:'top'};for(const key of ['为什么','有什么不同','哪些','作用','用意','分别','特点','看法','理由']){if(txt.includes(key)){const range=shape.text.get(key);range.bold=true;range.fill='#a33e35';}}return shape}
for(let idx=0;idx<slides.length;idx++){
 const d=slides[idx],s=pres.slides.add();s.background.fill='#fffcf6';
 text(s,'title',d.title,64,48,1152,88,{size:d.kind==='cover'?68:48,font:kai,color:d.kind==='question'?'#a33e35':'#245e51',bold:true});
 const hasImage=!!d.panel,w=hasImage?620:1152,fontSize=40;
 let y=d.kind==='cover'?210:174;
 for(let j=0;j<d.lines.length;j++){
  const line=wrap(d.lines[j],w,fontSize), count=line.split('\n').length,h=count*56+5;
  if(y+h>664)throw Error(`Slide ${idx+1} text overflow at line ${j+1}: ${y+h}`);
  text(s,'body-'+j,line,64,y,w,h,{size:fontSize,font:(d.kind==='answer'||d.kind==='concept')?song:kai,color:d.kind==='answer'&&j===0?'#a33e35':'#243d37'});y+=h+12;
 }
 if(d.diagram){
  let yy=196;
  for(let i=0;i<d.diagram.length;i++){
   const [left,right]=d.diagram[i];
   text(s,'mapping-left-'+i,left,64,yy,460,100,{size:40});
   text(s,'mapping-link-'+i,'对应',560,yy,120,100,{size:40,color:'#a33e35',font:song});
   text(s,'mapping-right-'+i,right,730,yy,480,112,{size:40});yy+=145;
  }
 }
 if(hasImage){const n=d.panel,[x0,y0,cw,ch]=L.panelRects[n-1],pic=await fs.readFile(path.join(lessonDir,'assets','comic'+Math.ceil(n/10)+'.png'));const width=500,height=width*ch/cw;const im=s.images.add({blob:pic,contentType:'image/png',alt:'用户原有漫画第'+n+'格',fit:'contain',position:{left:716,top:230,width,height},crop:{left:x0/1024,top:y0/1536,right:1-(x0+cw)/1024,bottom:1-(y0+ch)/1536}});}
 s.speakerNotes.text=`第${d.lesson}课。${d.kind==='question'?'先让学生回答，下一页再揭示。':''}\n${d.notes}\n来源：用户上传课文及教参截图（2026-10-19）。`;
}
const renderSlides=[...pres.slides.items];
if(renderSlides.length!==slides.length)throw Error('Slide count mismatch');
const SKILL_DIR='/root/.codex/skills/builtins/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL_DIR,'container_tools/artifact_tool_utils.mjs')));
const stamp=Date.now(),stage=path.join(workspaceDir,'build/pptx-'+stamp);await fs.mkdir(stage,{recursive:true});
const candidate=path.join(stage,'candidate.pptx'),finalPath=path.join(workspaceDir,'output/fang-feng-zheng-'+stamp+'.pptx');
await (await PresentationFile.exportPptx(pres)).save(candidate);
execFileSync(process.env.CODEX_PRIMARY_RUNTIME_PYTHON,[path.join(workspaceDir,'huawentong-home/tools/ba-ai-shuo-chu-lai/deduplicate_pptx.py'),candidate]);
const result=await finalizePresentation({workspaceDir,candidatePath:candidate,finalPath,pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:[kai,song]},verifyArtifactToolImport:true,requiredNativeTableOwnerSlides:[],explicitTotalSlideCount:slides.length,receiptPath:path.join(stage,'validation.json')});
console.log('Finalized',result);
await fs.mkdir(path.join(lessonDir,'slides'),{recursive:true});
for(const [i,slide] of renderSlides.entries()){
 const png=await pres.export({slide,format:'png',scale:1});await fs.writeFile(path.join(lessonDir,'slides',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 console.log('rendered',i+1);
}
await fs.copyFile(finalPath,path.join(lessonDir,'downloads/fang-feng-zheng.pptx'));
