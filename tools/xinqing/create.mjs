import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const W=process.env.XQ_BUILD_DIR||'/tmp/huawentong-xinqing-build',R=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),O=R+'/du/textbook/2hcl/unit4/xin-qing-shou-zhang';
await fs.mkdir(W+'/ppt-build',{recursive:true});await fs.mkdir(O+'/slides',{recursive:true});
const L=JSON.parse(await fs.readFile(O+'/lesson.json','utf8')),T=L.tasks,deck=[],pres=Presentation.create({slideSize:{width:1280,height:720}});
const K='LXGW WenKai TC',S='Noto Serif CJK SC',ink='#243D37',green='#245E51',red='#AE3F37',paper='#FFFCF6';pres.theme.defaultFont=K;
const images=await Promise.all([1,2,3,4].map(i=>fs.readFile(O+'/assets/comic'+i+'.png')));
function text(sl,s,x,y,w,h,size=44,color=ink,font=K,bold=false){const a=sl.shapes.add({name:'text-'+sl.shapes.items.length,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});a.text=s;a.text.style={typeface:font,fontSize:size,color,bold,wrap:'square',autoFit:'none',insets:0};return a;}
function start(title,notes='',kind='concept'){const sl=pres.slides.add();sl.background.fill=paper;text(sl,title,64,42,1152,110,50,kind==='question'?red:green,K,true);deck.push({title,notes,kind,lesson:1});sl.speakerNotes.text='中二高级华文 单元四 生活空间《心情手账》。来源：教师提供的课文、阅读放大镜、教参及四张漫画。\n'+notes;text(sl,String(deck.length).padStart(2,'0'),1154,661,64,44,38,green);return sl;}
function standard(title,rows,notes='',kind='concept',size=44){const sl=start(title,notes,kind);rows.forEach((s,i)=>text(sl,s,72,178+i*145,1130,132,size,ink,kind==='answer'?S:K));deck.at(-1).lines=rows;return sl;}
function picture(sl,n,x,y,w){const r=L.panelRects[n-1];sl.images.add({blob:images[L.panelSheets[n-1]-1],contentType:'image/png',alt:'用户原漫画第'+n+'格',fit:'contain',position:{left:x,top:y,width:w,height:w*r[3]/r[2]},crop:{left:r[0]/1024,top:r[1]/1536,right:1-(r[0]+r[2])/1024,bottom:1-(r[1]+r[3])/1536}});}
const note=id=>{const t=T.find(t=>t.id===id);return t.source+'\n'+t.role+'。'+t.answer+'\n'+t.explain+'\n'+t.scoreGuide+'\n常见误读：'+t.reject;};
function reading(p){const s=start('第'+'一二三四'[p-1]+'则 · 7月'+p+'日','阅读本则，再进入相应任务。漫画与全文均可在互动页并列查看。');text(s,L.paragraphs[p-1],72,181,1136,420,43);}
function tableAnswer(p,rows){const s=start('7月'+p+'日 · 表格参考',note('table-july'+p),'answer');const tb=s.tables.add({rows:3,columns:2,left:72,top:182,width:1136,height:398,columnWidths:[212,924],values:[['项目','内容'],['烦恼',rows[0]],['打算',rows[1]]]});tb.borders.assign({style:'solid',fill:'#D5DDD8',width:1});tb.cells.block({row:0,column:0,rowCount:3,columnCount:2}).assign({textStyle:{typeface:K,fontSize:42,color:ink},margins:{left:20,right:20,top:16,bottom:16},anchor:'center'});for(let c=0;c<2;c++){tb.getCell(0,c).fill='#E6EEE8';tb.getCell(0,c).text.style={typeface:K,fontSize:42,color:green,bold:true};}deck.at(-1).nativeTable=true;}
let s=start('心情手账','一课时按50分钟规划。四则手账分别处理不同烦恼。不要当作同一事件的四个阶段。','cover');text(s,'中二高级华文 · 单元四\n生活空间',72,185,680,150,42);text(s,'读懂心情，\n说清看法与理由。',72,380,640,170,46,red);picture(s,4,795,180,400);
standard('这一周，我的心情',['用几个词语概括一下你这一周的心情。','先想一想，再口头分享。','只说你愿意分享的内容。'],'课本正文页提示。导入3分钟，口头处理，不新增文字作答。');
reading(1);
standard('课文词语一（1）（2）',['从课文中找出代表下列意思的词语。','1. 轻视自己，认为自己不如别人。','2. 坚强持久的意志。'],note('words-july1'),'question');
standard('词语参考 · 自卑与毅力',['1. 自卑：轻视自己，认为自己不如别人。','2. 毅力：坚强持久的意志。','“我要做……”是在提出目标。'],note('words-july1')+'\n不以身材评价同学，也不要求讨论个人体重。','answer',42);
s=start('7月1日 · 烦恼与打算',note('table-july1'),'question');text(s,'根据课文内容，完成表格。\n\n“我”遇到什么烦恼？\n\n“我”打算怎么做？',72,180,660,420,44);picture(s,6,790,180,400);
tableAnswer(1,['不满意身材，又难抗拒零食的诱惑。','坚持运动，戒掉爱吃零食的坏习惯。']);
reading(2);
s=start('7月2日 · 烦恼与打算',note('table-july2'),'question');text(s,'根据课文内容，完成表格。\n\n“我”遇到什么烦恼？\n\n“我”打算怎么做？',72,180,660,420,44);picture(s,11,790,180,400);
tableAnswer(2,['觉得友情渐疏，又不清楚美星近况。','明天主动找美星好好谈一谈。']);
standard('看见的表现，与未确定的原因',['表现：茫然、魂不守舍或打瞌睡。','推测：“好像是睡眠不足”。','原因：课文还没有交代。'],note('table-july2')+'\n先口头问能否确定原因，再揭示。不是额外书写题。','answer',42);
reading(3);
standard('课文词语一（3）',['从课文中找出代表下列意思的词语。','3. 厌恶；不满意。','回到哥哥对使用电脑时间的反应。'],note('words-july3'),'question');
standard('“嫌”与“怄气”',['“嫌”：哥哥不满意我用电脑太久。','“怄气”：“我”生闷气，闹别扭。','两个词说的对象与意思不同。'],note('words-july3'),'answer',42);
s=start('7月3日 · 烦恼与打算',note('table-july3'),'question');text(s,'根据课文内容，完成表格。\n\n“我”遇到什么烦恼？\n\n“我”打算怎么做？',72,180,660,420,44);picture(s,16,790,180,400);
tableAnswer(3,['争着用电脑，和哥哥吵了起来。','哥哥主动示好，“我”决定不再怄气。']);
reading(4);
standard('课文词语一（4）',['从课文中找出代表下列意思的词语。','4. 做饭做菜。','这个词说的是活动，还是职业？'],note('words-july4'),'question');
standard('烹饪、厨师与会计师',['烹饪：做饭做菜。','“我”想选修营养与食品科学，将来当厨师。','爸爸希望“我”向会计方面发展。'],note('words-july4'),'answer',42);
s=start('7月4日 · 烦恼与打算',note('table-july4'),'question');text(s,'根据课文内容，完成表格。\n\n“我”遇到什么烦恼？\n\n“我”打算怎么做？',72,180,660,420,44);picture(s,23,790,180,400);
tableAnswer(4,['自己的兴趣和梦想，与爸爸的期望不同。','仍想按照自己的兴趣作选择。']);
standard('手账主人是怎样的人',['从手账的内容推测，手账的主人','是个什么样的人？（年龄、身份、性格等）','回看全文，自己概括一个特点。'],note('character'),'question',44);
standard('特点＋依据＋解释',['特点：主人是一个怎样的人？','依据：哪一个具体行为可以证明？','解释：这个行为为什么能体现特点？'],'先独立作答6分钟。身份从选科句判断，准确年龄未交代。证据可跨则连续加入多句。');
standard('人物分析参考',['主人是即将进入中三的中学生。','主人关心朋友：留意美星的异常，多次询问。','这说明主人愿意了解朋友的处境。'],note('character')+'\n也可分析有主见、愿意接受和解等有依据的特点。','answer',42);
standard('课本第三题 · 必做开放回应',['假设这本心情手账是你朋友跟你分享的，','针对其中一则心情日记说出你的看法，','并说明理由。'],note('open-response'),'question');
standard('看法为什么有道理',['看法＋理由：我怎么看？为什么？','例子：结合本则细节，说出具体做法。','回扣：这怎样支持我的看法？'],'独立书写9分钟内完成并对照。观点不同可以，关键是理由与证据。');
standard('开放回应示例 · 7月2日',['我赞成主动找美星谈一谈，','因为只凭她的表现，还不知道发生了什么。','可以找安静的时候，先关心她，再听她说。'],note('open-response')+'\n这是参考示范，不是唯一答案。','answer',42);
standard('例子怎样支持看法',['她闪烁其词，不代表她不想交朋友。','平静询问，能表达关心并给她解释的空间。','这样做有助于了解情况，减少误会。'],note('open-response')+'\n不保证一次谈话就解决问题。其他三则的可接受方向见教师资料。','answer',42);
standard('当堂检查与订正',['我有没有把“打算”写成“已经做到”？','我的特点有没有原文依据？','我的看法有没有说明“为什么”？'],'最后3分钟，用已有回答检查，不加新短文或课后任务。检查页导出记录，个人词语本按年级单元课文汇总。');
await fs.writeFile(O+'/slides.json',JSON.stringify(deck,null,2));
await fs.writeFile(W+'/ppt-build/proto.json',JSON.stringify(pres.toProto()));
await(await PresentationFile.exportPptx(pres)).save(W+'/ppt-build/candidate.pptx');
for(const [i,sl]of pres.slides.items.entries()){let png=await pres.export({slide:sl,format:'png',scale:1});await fs.writeFile(O+'/slides/slide-'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await png.arrayBuffer()));console.log('rendered',i+1)}
console.log('slides',deck.length,'native tables',deck.map((d,i)=>d.nativeTable?i+1:0).filter(Boolean));
