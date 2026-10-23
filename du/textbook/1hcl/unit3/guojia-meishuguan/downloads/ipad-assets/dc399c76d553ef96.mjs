import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const R=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),D=R+'/du/textbook/1hcl/unit3/guojia-meishuguan',W=R+'/../build';
const L=JSON.parse(await fs.readFile(D+'/lesson.json','utf8')),meta=[],nativeTables=[];
const K='LXGW WenKai TC',S='Noto Serif CJK SC',p=Presentation.create({slideSize:{width:1280,height:720}});p.theme.defaultFont=K;
const ink='#18344F',blue='#185E94',red='#AF2438';
function tx(sl,text,x,y,w,h,size=44,font=K,color=ink,bold=false){const a=sl.shapes.add({name:'text-'+sl.shapes.items.length,geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});a.text=text;a.text.style={typeface:font,fontSize:size,color,bold,wrap:'square',autoFit:'none',insets:0};return a;}
const notes=id=>{const t=L.tasks.find(t=>t.id===id);return t.source+'。'+t.role+'。\n'+t.questions.join('\n')+'\n参考：'+t.answer+'\n解释：'+t.explain+'\n'+t.scoreGuide+'\n常见误区：'+t.reject;};
function start(title,nt='',kind='concept'){const sl=p.slides.add();sl.background.fill='#F7FAFD';tx(sl,title,66,42,1148,116,50,K,blue,true);tx(sl,String(meta.length+1).padStart(2,'0'),1150,660,70,46,38,K,blue);sl.speakerNotes.text='中一高级华文 单元三《国家美术馆探秘》\n课文、教参及四页漫画均来自教师附件。\n'+nt;meta.push({title,notes:nt,kind});return sl;}
function lines(title,rows,nt='',kind='concept',size=44){const sl=start(title,nt,kind);rows.forEach((s,i)=>tx(sl,s,76,180+i*143,1120,132,size,kind==='answer'?S:K));meta.at(-1).lines=rows;return sl;}
async function pic(title,n,rows=[],nt=''){const sl=start(title,nt,'comic');const r=L.panelRects[n-1],bytes=await fs.readFile(D+'/'+L.panelImages[n-1]);sl.images.add({blob:bytes,contentType:'image/png',alt:'原漫画第'+n+'格',fit:'contain',position:{left:65,top:170,width:700,height:454}});rows.forEach((s,i)=>tx(sl,s,805,184+i*145,400,137,40));meta.at(-1).panel=n;return sl;}
function table(title,values,nt){const sl=start(title,nt,'answer');const tb=sl.tables.add({rows:values.length,columns:2,left:75,top:183,width:1130,height:405,columnWidths:[320,810],values});tb.borders.assign({style:'solid',fill:'#B9CBD9',width:1});for(let r=0;r<values.length;r++){tb.rows[r].height=405/values.length;for(let c=0;c<2;c++){const ce=tb.getCell(r,c);ce.fill=c===0?'#DCEAF4':'#FFFFFF';ce.text.style={typeface:K,fontSize:40,color:ink,bold:c===0,wrap:'square',autoFit:'none',insets:18,verticalAlignment:'middle'};}}nativeTables.push(meta.length);meta.at(-1).table=values;}

await pic('国家美术馆探秘',1,['中一高级华文','第三单元 巩固','1—2课时'],'第一课任务1—7，第二课任务8—10。数字与馆藏数量均按课文教学。');
lines('这篇课文怎样读',['每到一段，先弄懂一个“秘密”。','看到数字或例子，问：说明什么特点？','最后用具体内容，解释自己的选择。'],'核心目标：信息筛选、说明方法作用、语境解释、开放回应。');
lines('第一段 · 数字说明什么',['第1段的数字说明了','国家美术馆的什么特点？','先找数字和单位，再说特点。'],notes('size'),'question');
table('数字与单位，要一起读',[['课文数字','6万4000平方米'],['熟悉的比较','大约9个足球场那么大'],['说明的特点','面积很大，读者更容易想象']],notes('size'));
lines('第二段 · “秘密”的引号',['“秘密”为什么加引号？','普通的“秘密”，通常指什么？','这里的“秘密”，可以公开介绍吗？'],notes('secrets'),'question');
lines('借用“秘密”，邀请读者探索',['这里借指鲜为人知的有趣事情。','人们尚不了解，值得探索和发现。','它们可以公开，并非必须保密。'],notes('secrets'),'answer');
lines('第三段 · 两座建筑的来历',['美术馆由哪两座历史建筑改建而成？','它见证了哪些历史事件？','分别找建筑名称和对应的作用。'],notes('history'),'question',42);
table('建筑与历史作用',[['前最高法院','60多年作为司法制度的最高殿堂'],['政府大厦','见证日本投降和新加坡宣布自治'],['共同来历','两座历史建筑合二为一，改建成馆']],notes('history'));
lines('第四段 · 例子说明什么',['法官的座位、被告栏、棕色天花板','这里举的例子是为了说明什么？','先看“例如”前面的概括句。'],notes('court'),'question',42);
lines('举例子，让“部分原貌”更具体',['特点：美术馆保留部分原貌。','例子：法官座位、被告栏、天花板。','作用：让读者知道具体保留了什么。'],notes('court'),'answer',42);
await pic('地下通道有什么用途',14,['当时犯人经过这里，','直接进入被告栏。','这是文中明写的信息。'],notes('court')+'\n原漫画路线示意。通道所属建筑可推测，具体建造年份文中未写。');
lines('第五段 · 门的“秘密”',['悬空桥两端的大门有什么“秘密”？','为什么用“古色古香”形容这些大门？','“原本……变成……”写了什么变化？'],notes('doors'),'question',42);
table('窗户变成大门',[['原本','窗户'],['现在','悬空桥两端的大门'],['古色古香','风格古朴，有旧时韵味']],notes('doors'));
lines('第六段 · 圆顶为什么变色',['圆顶的颜色有了什么变化？','为什么会出现这样的变化？','课文写明了原本的具体颜色吗？'],notes('dome'),'question');
lines('圆顶变色的因果',['现在是铜绿色。','原因是长年的氧化（oxidation）。','原色未写明，答题不能根据示意图补写。'],notes('dome'),'answer',42);
lines('第七段 · 钱包里的名作',['为什么把这幅画称为','“钱包里的名作”？','写一两句，解释画、钞票与钱包的联系。'],notes('painting')+'\n先独立回答，再揭示下一页。第一课文字作答1。','question',42);
lines('画、钞票与钱包的联系',['《晒咸鱼》印在50新元钞票背面。','钞票常放在钱包里。','所以称这幅画为“钱包里的名作”。'],notes('painting'),'answer',42);
lines('第七段 · 熟悉，又陌生',['为什么说对许多人来说，','这幅画“既熟悉又陌生”？','分别找两个“是因为”。'],notes('painting'),'question');
table('看过，不等于了解',[['熟悉','见过50新元钞票背面的图案'],['陌生','对画作本身并不了解'],['画面内容','马来同胞晒咸鱼，宁静而平和']],notes('painting'));
lines('第一课 · 检查已有回答',['数字：有没有连上面积或数量？','例子：有没有说出具体说明的特点？','“钱包”：有没有解释钞票与画的联系？'],'第一课最后5分钟订正，收藏需要的词语。无需新出口题。','concept',42);
lines('第八段 · 你想亲自去探秘吗',['作者在结尾呼吁读者做什么？','你也想亲自去美术馆探秘吗？为什么？','先读完第8段，再独立写自己的选择。'],notes('ending')+'\n第二课从此开始。第二课文字作答1。','question',42);
lines('开放回应 · 说清为什么',['立场与理由：想不想去？为什么？','具体内容：哪一个“秘密”影响你？','回扣：亲自观察能帮助你了解什么？'],notes('ending')+'\n允许不同立场，教师按意义覆核。');
lines('一个有依据的回答',['我想亲自参观，了解旧建筑如何改建。','课文说悬空桥的大门原本是窗户，\n我想近看设计师怎样保留古朴风格。','这样能把课文读到的内容看得更具体。'],notes('ending')+'\n学生先答后显示。这不是唯一立场。','answer',40);
lines('全文回顾 · 五个“秘密”',['国家美术馆藏了哪些秘密？','先按第3—7段的顺序口头说。','每个秘密，只保留最关键的信息。'],notes('summary'),'question');
{const sl=start('五个“秘密”参考',notes('summary'),'answer');['两座历史建筑合建的来历','地下通道曾供犯人直接进入被告栏','悬空桥的大门原本是窗户','圆顶经过长年氧化而变色','《晒咸鱼》印在50新元钞票上'].forEach((s,i)=>tx(sl,(i+1)+'  '+s,80,174+i*88,1100,78,40,S));}
lines('课本统整表',['通过数字和例子理解事物的特点。','每行连接：特点、具体说明、说明方法。','先自己填，再逐行对照。'],notes('summary'),'question');
table('建筑 · 面积很大',[['事物的特点','面积很大'],['对特点的说明','6万4000平方米，约9个足球场'],['说明方法','列数字，结合熟悉事物作比较']],notes('summary'));
table('建筑 · 历史意义重要',[['事物的特点','具有重要的历史意义'],['对特点的说明','政府大厦见证日本投降和宣布自治'],['说明方法','举例子']],notes('summary'));
table('建筑 · 保留部分原貌',[['事物的特点','保留两座建筑的部分原貌'],['对特点的说明','法官座位、被告栏、棕色天花板'],['说明方法','举例子']],notes('summary'));
table('画作 · 馆藏丰富',[['事物的特点','馆藏丰富'],['对特点的说明','9000余件收藏品'],['说明方法','列数字']],notes('summary'));
lines('课本仿句 · 既熟悉又陌生',['对我来说，______既熟悉又陌生。','熟悉，是因为______；','陌生，是因为______。'],notes('language-research')+'\n第二课文字作答2。先写自己的句子，不直接照抄示范。','question');
lines('仿句参考 · 同一个对象',['学校附近的老建筑，既熟悉又陌生。','熟悉：我每天上学都会经过。','陌生：我不知道它过去有什么用途。'],notes('language-research')+'\n检查两面原因都指向同一个对象。','answer');
lines('课本查找 · 还有谁的画作',['除了钟泗滨的画作，','50新元钞票背面还有谁的画作？','查资料时，把画家与画面内容对应起来。'],notes('language-research')+'\n网页提供MAS及国家美术馆资料链接。可小组查阅，不新增打字要求。','question',42);
lines('查找结果 · 陈文希',['陈文希（Chen Wen Hsi）','Two Gibbons Amidst Vines','画面内容：藤蔓间的两只长臂猿。'],'国家美术馆FY2016 Annual Report印刷页16、PDF第19页明确列出画作和画家，并说明用于50元钞票背面。\nhttps://www.nationalgallery.sg/content/dam/about/annual-reports/reports/FY2016%20Annual%20Report.pdf\nMAS简称Gibbon：https://www.mas.gov.sg/currency/circulation-currency/circulation-currency-notes\n核对日期2026-10-23。','answer',40);
lines('检查与订正',['统整：每一个例子，是否支持那项特点？','仿句：同一个对象，两面原因是否合理？','开放回应：具体内容，怎样支持我的选择？'],'第二课最后5分钟。查看首次回答，补足缺点，再导出记录。开放题、解释题与仿句由教师覆核。','concept',42);

await fs.mkdir(W+'/ppt',{recursive:true});
await fs.writeFile(D+'/slides.json',JSON.stringify(meta,null,2));await fs.writeFile(D+'/slides-data.js','window.SLIDES='+JSON.stringify(meta)+';');
for(const [i,sl]of p.slides.items.entries()){const png=await p.export({slide:sl,format:'png',scale:1});await fs.writeFile(D+'/slides/slide-'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await png.arrayBuffer()));console.log('Rendered',i+1,'/',meta.length);}
await(await PresentationFile.exportPptx(p)).save(W+'/ppt/candidate.pptx');
await fs.writeFile(W+'/ppt/requirements.json',JSON.stringify({count:meta.length,tables:nativeTables}));
console.log('PPT candidate ready',meta.length,nativeTables);
