"""Verified textbook content, question map and lossless panel display copies."""
from pathlib import Path
import json, shutil
from PIL import Image
R=Path(__file__).resolve().parents[2]
D=R/'du/textbook/1hcl/unit4/peiyang-hao-xiguan'
U=R.parent/'upload'
for f in ['assets','downloads','slides']:(D/f).mkdir(parents=True,exist_ok=True)
rects=[]
for page,ys in enumerate([[(143,438),(447,783),(791,1135),(1142,1526)],[(143,438),(447,783),(791,1125),(1132,1524)],[(143,471),(479,793),(799,1102),(1108,1524)],[(143,463),(469,776),(782,1089),(1094,1520)]],1):
 src=U/f'培养好习惯-{page}.png';shutil.copy2(src,D/f'assets/comic{page}.png');im=Image.open(src)
 for y0,y1 in ys:
  for x0,x1 in [(5,509),(518,1020)]:
   n=len(rects)+1;im.crop((x0,y0,x1,y1)).save(D/f'assets/panel-{n:02d}.png');rects.append([x0,y0,x1-x0,y1-y0])
for n,src in enumerate(['image(20261023-074245).png','image(20261023-074258).png','image(20261023-074314).png'],1):shutil.copy2(U/src,D/f'assets/textbook-{n}.png')
labels=['守时惜时','勤于阅读','坚持不懈','信守诺言','健康生活','制定计划','为人诚实','以礼待人','互动剧场','工作坊','活动与报名资料']
paras=[
'守时惜时\n一寸光阴一寸金，寸金难买寸光阴。',
'勤于阅读\n开卷有益，走遍天下书为伴。',
'坚持不懈\n滴水穿石，只要坚持，就一定会有收获。',
'信守诺言\n一诺千金，言出必行。',
'健康生活\n健康不是一切，但没有健康就没有一切。',
'制定计划\n成功始于计划，没有计划，你就会走向失败。',
'为人诚实\n多一分诚实，多一分信任。',
'以礼待人\n以礼待人是人际交往最起码的要求。',
'互动剧场：《差不多先生》\n互动剧场是一种新颖的戏剧形式。在互动剧场中，你不只是观众，也是演员。\n差不多先生有个坏习惯，凡事差不多就好。让我们一起来帮助他改掉这个坏习惯。',
'工作坊：好习惯助你成为人气王\n如何避免言语不当造成的尴尬？如何维护友情？\n好习惯能帮助你去除这些烦恼，让友谊的小船一帆风顺！\n快来参加我们的工作坊，学习如何培养良好的习惯，掌握人际交往的有效策略！',
'欢乐民众俱乐部\n青年节特备活动\n互动剧场：《差不多先生》\n日期：7月21日\n时间：晚上7点至9点\n地点：欢乐民众俱乐部礼堂\n工作坊：好习惯助你成为人气王\n日期：7月20日\n时间：下午3点至5点\n地点：欢乐民众俱乐部礼堂\n嘉宾：高级辅导员王世平博士\n报名网站：www.huanlecommunity.com.sg'
]
ideas=['珍惜自己和他人的时间。','读书对人有益。','持之以恒，才能逐渐有收获。','答应别人的事，要认真做到。','健康是学习和生活的重要基础。','先安排，再有步骤地行动。','诚实有助于建立信任。','以礼待人是交往的基本要求。','观众也能参与表演，帮助人物改变坏习惯。','培养好习惯，学习维护友情的有效方法。','按活动名称核对日期、时间、地点与报名方式。']
panels=[[1,2],[3,4],[5,6],[7,8],[9,10],[11,12],[13,14],[15,16],[17,18,19,20,21,22,23],[25,26,27,28,29,30],[24,31]]
tasks=[]
def task(id,title,p,questions,mode,answer,explain,hints,points,**kw):
 t=dict(id=id,title=title,lesson=1,order=len(tasks)+1,range=[p],focus=[p],questions=questions,mode=mode,answer=answer,explain=explain,hints=hints,points=points,source='课本《阅读放大镜》',role='学生独立',guide='先回答，再对照。',reject='',scoreGuide='按意思核对，接受合理的等义表达。',keywords=[])
 t.update(kw);tasks.append(t)
for id,title,p,answer,explain,hint,number in [
 ('word-reading','1 · 开卷有益',2,'读书有好处。','“卷”在这里指书。“有益”是有好处，不是必须读完某一整本书才算有益。','注意“勤于阅读”与“书为伴”。',2),
 ('word-persist','2 · 坚持不懈',3,'坚持下去，不松懈、不轻易放弃。','“滴水穿石”说明积累与坚持；不能只答“做得很快”。','注意“只要坚持”和“收获”。',1),
 ('word-promise','3 · 一诺千金',4,'说话算数，信守承诺。','“千金”形容承诺很有分量，不是说承诺一定涉及大笔金钱。','把“信守诺言”和“言出必行”连起来想。',3)]:
 task(id,title,p,['用自己的话解释下列词语。',title.split(' · ')[1]],'oral',answer,explain,[hint,'不要用原词解释原词，说清它表示的意思。'],['说出了核心意思','没有照搬原词'],source=f'课本第一题第{number}小题',role='师生口头共构',guide='先对同桌说一句解释，再展开核对。无需打字。',keywords=[title.split(' · ')[1]],scoreGuide='课堂口头核对，不自动评分。教师补充核心意思，不要求抄写。')
task('theatre','4 · 互动剧场',9,['互动剧场有什么特别之处？'],'objective','观众不只是观看表演，也可以成为演员，参与帮助差不多先生改掉坏习惯。','关键是观众角色的变化。课文写“你不只是观众，也是演员”；教参进一步指出观众能够影响剧情的发展。',['回看“你不只是……也是……”这句话。','比较“看别人演”与“自己参与演”的区别。'],['说出了观众也能成为演员','依据来自原文'],source='课本第二题第1小题',guide='点选最完整的一项，再口头指出原文依据。',keywords=['特别之处'],checks=[dict(id='participate',question='哪一项说明它的特别之处？',options=['观众观看表演后离场回家','观众主要听嘉宾讲解方法','观众坐在台下欣赏整场戏','观众也能成为演员参与表演'],correct=3,why=['没有说明观众也能参与。','这是把工作坊的形式混入剧场。','仍然只是观看，漏了角色变化。','符合“你不只是观众，也是演员”。'])],scoreGuide='客观点选1项。教学参考点：观众也能当演员；参与改变人物行为或剧情。',reject='只说新颖、有趣，未说明新颖在哪里。')
task('word-smooth','5 · 一帆风顺',10,['用自己的话解释下列词语。','一帆风顺'],'oral','非常顺利，没有阻碍或挫折。这里希望朋友相处顺利。','海报把友谊比作小船，借航行顺利表达朋友相处顺利的愿望。不能理解成真的一起坐船。',['先想小船顺风前进的情景。','这里的小船指“友谊”，把意思放回句子。'],['解释了顺利的意思','能放回友情的语境'],source='课本第一题第4小题',role='师生口头共构',guide='先对同桌解释，再展开核对。无需打字。',keywords=['一帆风顺'],scoreGuide='课堂口头核对，不自动评分。')
task('purpose','6 · 工作坊的目的',10,['举办工作坊的目的是什么？'],'written','让参与者学习如何培养良好的习惯，掌握人际交往的有效策略。','题目问举办活动希望达到什么目标，要包括“培养良好习惯”和“掌握交往策略”两方面。日期、地点和嘉宾不回答目的。',['先找海报邀请大家参加工作坊的那一句。','注意两个并列动作：“学习……”和“掌握……”。'],['培养良好习惯','掌握人际交往的有效策略'],guide='加入原句，圈出两个要点，再写一句完整答案。',keywords=['目的'],fields=[dict(id='response',label='我的完整回答',placeholder='举办工作坊是为了让参与者……，并……。')],evidence=[dict(label='原文依据（可以加入多句）',p=[10],terms=['学习如何培养','掌握人际交往'])],scoreGuide='教师参考2点：培养良好习惯1点；掌握人际交往的有效策略1点。各点独立，不自动批改。',reject='只答“成为人气王”过于笼统；抄日期、地点属于答非所问。')
task('audience','7 · 适合谁参加',10,['工作坊适合哪些人参加？'],'objective','适合想了解如何维护友情、怎样更好地处理朋友之间关系的青年参加。','用海报的“如何避免言语不当造成的尴尬”“如何维护友情”定位需要；结合青年节活动判断对象。不是所有活动都适合完全相同的需要。',['回看工作坊开头的两个问题。','题目问参加者有什么需要，不是问谁担任嘉宾。'],['对象是青年','需要与维护友情、处理朋友关系有关'],keywords=['哪些人'],checks=[dict(id='audience',question='哪类青年的需要最符合这个工作坊？',options=['希望学习维护友情方法的青年','希望参与互动戏剧表演的青年','希望了解俱乐部建筑的青年','希望学习制定运动计划的青年'],correct=0,why=['符合开头两个问题和人际交往的目标。','更符合另一项互动剧场活动。','海报没有介绍建筑的学习内容。','健康生活虽是好习惯，但不是本工作坊的重点。'])],scoreGuide='客观点选1项；教师口头追问为何适合。',reject='只答“青年”不完整；把高级辅导员误当作参加对象。')
task('register','8 · 报名方式',11,['如何报名参加青年节特备活动？'],'objective','到海报列出的报名网站 www.huanlecommunity.com.sg 报名。','先找“报名网站”标签，再读它后面的信息。两项活动的日期和时段不同，地点相同。网址只作教材阅读资料。',['找到海报底部“报名网站”四个字。','场地、日期、嘉宾都不能代替报名方式。'],['找到了报名网站','没有把活动地点当作报名地点'],keywords=['如何报名'],guide='只需读海报作答，不用访问教材里的报名网址。',checks=[dict(id='channel',question='根据海报，应该怎样报名？',options=['到活动礼堂当面购买门票','到海报所列的网站进行报名','向到场的辅导员发送短信','在演出结束后登记个人资料'],correct=1,why=['海报未写现场售票。','海报明确标出“报名网站”。','海报没有短信报名说明。','海报没有演出后登记的说明。'])],scoreGuide='客观点选1项；完整答法应写到海报报名网站。',reject='臆造电话、收费、截止日期或报名柜台。',oral=[['两个活动分别在什么时候举行？','互动剧场：7月21日，晚上7点至9点。工作坊：7月20日，下午3点至5点。此追问只作核对，不另加作业。']])
task('friendship','9 · 我怎样维护友情',10,['你是怎么维护友情的？和同学分享你的经验。'],'written','示例：我会先听朋友解释，再表达自己的想法。一次我们做小组作业时意见不同，我先问清他的理由，再一起调整分工。这样能减少误会，也让朋友感到被尊重，所以有助于维护友情。','写自己的真实经历。把“我做了什么”与“为什么有帮助”连起来；不能只写友谊很重要，也不要求采用示例的做法。',['先选一个你真的做过的维护友情的方法。','回想一件具体事情：当时有什么问题？你怎样做？为什么有帮助？'],['写了具体做法','举了自己的真实经历','解释为什么有助于维护友情'],source='课本第三题；“为什么”是答题支架',guide='先独立写一小段，再和同桌分享。说清做法、经历和为什么。',keywords=['怎么维护友情','你的经验'],required=True,requiredMessage='请先写下自己的做法、经历和为什么，再完成本课。',scope='full',fields=[dict(id='response',label='我的真实经历',placeholder='我会……。有一次……，我……。这样……，所以有助于维护友情。')],scoreGuide='教师参考3项：具体做法；真实且相关的个人经历；解释做法如何帮助友情。每项可评“完整／待补充”，不自动打分。',reject='只写“要友善”；只讲故事没有解释；照抄示例当作自己的经历。')
L=dict(id='s1u4l1',title='培养好习惯',label='中一高级华文 · 单元四 · 生活空间',grade=1,unit=4,version='20261023-habits-1',sequenceVersion=1,unitNoun='部分',wordEnglishVisible=True,paragraphs=paras,paragraphLabels=labels,paragraphIdeas=ideas,paragraphTasks=['','word-reading','word-persist','word-promise','','','','','theatre','word-smooth','register'],panels=panels,panelRects=rects,panelImages=[f'assets/panel-{i:02d}.png' for i in range(1,33)],tasks=tasks)
words={}
def w(term,p,meaning,en):words[term]=dict(meaning=meaning,en=en,paragraph=p)
for row in [
('守时惜时',1,'遵守约定时间，珍惜时间。','be punctual and value time'),('一寸光阴一寸金',1,'时间像黄金一样宝贵。','time is as precious as gold'),('寸金难买寸光阴',1,'金钱也买不回已经过去的时间。','money cannot buy back time that has passed'),('勤于阅读',2,'经常主动读书。','read regularly and diligently'),('开卷有益',2,'读书有好处。','reading is beneficial'),('坚持不懈',3,'坚持下去，不松懈、不轻易放弃。','persevere without giving up'),('滴水穿石',3,'水不断滴下能穿透石头，比喻坚持能有成果。','constant effort can achieve results'),('收获',3,'通过付出得到的成果。','gain or achievement from effort'),('信守诺言',4,'认真履行答应别人的事。','keep a promise'),('一诺千金',4,'说话算数，很重视自己的承诺。','honour one’s word and keep promises'),('言出必行',4,'说了就一定付诸行动。','do what one has promised'),('制定',6,'经过考虑，把内容定下来。','draw up or formulate'),('计划',6,'事先安排要做的事情和步骤。','a plan of what to do and how'),('诚实',7,'说真话，不欺骗。','honest; truthful'),('信任',7,'相信对方可靠。','trust someone to be reliable'),('以礼待人',8,'用有礼貌的言语和行动对待别人。','treat others politely and respectfully'),('人际交往',8,'人与人之间的沟通和相处。','interaction and relationships with other people'),('起码',8,'最低限度；最基本的。','at least; the most basic'),('互动剧场',9,'观众能参与表演的戏剧形式。','interactive theatre involving the audience'),('新颖',9,'新鲜而有独特之处。','novel and original'),('戏剧',9,'由演员表演故事的艺术。','drama; a performed story'),('形式',9,'事物表现出来的方式。','form or format'),('观众',9,'观看演出的人。','audience members'),('演员',9,'扮演角色、进行表演的人。','actors or performers'),('凡事',9,'所有的事情。','in everything; in all matters'),('工作坊',10,'让参加者共同学习、交流或练习的活动。','a workshop for learning and practice'),('言语不当',10,'说话不合适，可能让人不舒服。','inappropriate words or remarks'),('尴尬',10,'让人难为情或不知如何应对的处境。','an awkward or embarrassing situation'),('维护',10,'维持和保护，使其不受损害。','maintain and protect'),('友情',10,'朋友之间的感情。','friendship'),('友谊',10,'朋友之间的感情。','friendship'),('烦恼',10,'使人忧虑、不愉快的事情或心情。','worries or troubles'),('一帆风顺',10,'事情进行得非常顺利。','go smoothly without setbacks'),('掌握',10,'学会并能够运用。','learn and be able to use'),('有效',10,'能起作用，达到预期目的。','effective; producing the intended result'),('策略',10,'为达到目标，根据情况采用的方法。','a strategy chosen to achieve a goal'),('特备',11,'特别安排或准备的。','specially organised'),('嘉宾',11,'受邀请参加活动的客人。','an invited guest'),('辅导员',11,'负责指导和帮助他人的人员。','a counsellor or adviser')]:w(*row)
(D/'lesson.json').write_text(json.dumps(L,ensure_ascii=False,indent=2))
(D/'content.js').write_text('window.LESSON='+json.dumps(L,ensure_ascii=False)+';\n')
(D/'lexicon.js').write_text('window.LESSON_WORDS='+json.dumps(words,ensure_ascii=False,indent=2)+';\n')
brief={'minutes':50,'flow':[['导入与海报类型',3],['八种好习惯图文自读及前三个词义',10],['互动剧场及课本第二题第1问',8],['工作坊、一帆风顺、目的与对象',13],['活动资料与报名方式',4],['友情开放题独立写答及分享',9],['订正与词语整理',3]],'targets':['结合语境，用自己的话解释四个词语','按题目对象筛选海报信息，区分特点、目的、对象与报名方式','结合真实经历解释维护友情的方法'],'sourceConflict':'课本海报写www.huanlecommunity.com.sg，教参及漫画第32格写另一网址。答案遵照课本，原漫画不改动。','mapping':list(zip(labels,panels))}
(D/'teaching-brief.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2))
print('Built',len(paras),'sections',len(tasks),'tasks',len(words),'words; minutes',sum(x[1] for x in brief['flow']))
