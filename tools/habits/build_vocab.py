from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];D=R/'du/ciyu/1hcl/unit4/peiyang-hao-xiguan';M=R/'du/textbook/1hcl/unit4/peiyang-hao-xiguan';D.mkdir(parents=True,exist_ok=True)
# Each context tests use. Meanings are support, not a second compulsory quiz.
rows=[
('一寸光阴一寸金','小乐总把复习拖到最后，朋友想提醒他珍惜时间。','哪一句提醒最贴切？',['一寸光阴一寸金，要把时间用好。','一诺千金，答应朋友的事要做到。','开卷有益，多读书能增加见识。','滴水穿石，坚持练习会有收获。'],'语境重点是珍惜时间。其他句子分别谈守信、阅读和坚持。'),
('一诺千金','阿明答应帮朋友整理资料，虽然很累，仍按约完成。','哪一个词最能概括他在这件事中的表现？',['一诺千金','一帆风顺','开卷有益','新颖独特'],'他履行了承诺。承诺可以是日常生活中的事，不限于重大或金钱承诺。'),
('言出必行','班长承诺每天检查班级门窗，之后每天都认真检查。','哪一句最准确？',['班长言出必行，答应的事都认真做到。','班长言出必行，说话的声音特别响亮。','班长言出必行，想到什么就马上说出。','班长言出必行，每次发言都说得很快。'],'言出必行强调说到做到，不是音量、语速或想到就说。组织也可在合适语境下说到做到。'),
('起码','老师规定，小组报告不能少于三分钟。','哪一句保留了老师的要求？',['小组报告起码要讲三分钟。','小组报告最多只能讲三分钟。','小组报告大约可以讲三分钟。','小组报告必须正好讲三分钟。'],'起码在这里表示下限。至少三分钟，可以超过三分钟。'),
('开卷有益','小华从一本故事书里学到待人的道理，想表达读书的益处。','哪一句最贴合这个意思？',['开卷有益，这次阅读让我有所收获。','一诺千金，这次阅读让我有所收获。','以礼待人，这次阅读让我有所收获。','言出必行，这次阅读让我有所收获。'],'开卷有益表示读书有好处。读了几遍才理解，不会因此使这个成语用错。'),
('新颖','展览采用了一种有创意、与常见展览不同的呈现方法。','哪个词最适合形容这种设计？',['新颖','熟练','稳妥','整齐'],'这里同时有新鲜和独特的意思，不能仅凭“刚买的”或“很流行”判断。'),
('尴尬','我把朋友认成了别人，还当众叫错名字，一时不知怎样解释。','哪个词最贴切地形容当时的处境？',['尴尬','欣慰','惋惜','向往'],'情境让人难为情，不知怎样应对。尴尬可能与紧张、害羞同时出现，不能机械排除。'),
('维护','朋友之间出现误会，我们决定坦诚沟通，努力让关系不受损害。','哪个词最适合填空：我们这样做是为了____友情。',['维护','制定','掌握','欣赏'],'维护友情表示维持和保护朋友关系。这里根据具体搭配判断，不把维护的对象绝对限制为抽象事物。'),
('一帆风顺','我们希望朋友今后的学习和生活都十分顺利。','哪一句祝福最贴切？',['祝你一帆风顺，事事顺利。','祝你一诺千金，事事顺利。','祝你开卷有益，事事顺利。','祝你言出必行，事事顺利。'],'一帆风顺在这里是祝愿顺利，不是证明一个人一生从没遇到困难。'),
('有效','我们换了沟通方式，误会逐渐减少，达到了改善关系的目的。','哪一个判断有语境依据？',['这种沟通方法很有效。','这种沟通方法很新颖。','这种沟通方法很复杂。','这种沟通方法很费时。'],'有效强调能够起作用、达到目的；语境没有交代新颖程度、复杂程度或耗时。'),
('策略','为了更好地维护友情，小组讨论遇到分歧时如何沟通。','这里的“策略”指什么？',['根据情况采用的处理方法','参加活动必须填写的资料','活动结束以后获得的奖品','记录朋友姓名的固定格式'],'策略是为达到目标、根据情况采取的方法。人际交往、学习和比赛都可以需要策略。'),
('戏剧','学校让学生通过扮演角色，把故事搬上舞台。','哪个词最适合填空：学校举办了一场____演出。',['戏剧','计划','策略','友谊'],'戏剧演出是通过角色表演故事。本题检测这一个明确搭配。'),
('工作坊','活动让参加者一边讨论，一边练习怎样与朋友沟通。','海报中的“工作坊”最接近哪一种活动？',['共同学习并动手练习的活动','观众从头到尾观看的演出','参加者领取奖品的颁奖活动','只登记姓名与电话的报名活动'],'本海报的工作坊是互动学习活动。这个语境义不排除该词在其他语境中的用法。'),
('友谊','小安和朋友虽然分到不同班，仍经常关心、支持彼此。','哪个词最适合填空：他们之间保持着深厚的____。',['友谊','策略','计划','形式'],'友谊指朋友之间的感情。不能只凭年龄、职业或身份不同就断言两人不可能有友谊。'),
('嘉宾','俱乐部邀请一位辅导员来到工作坊，与参加者交流。','海报把这位受邀请的人称作什么？',['嘉宾','观众','演员','读者'],'嘉宾是受邀请参加活动的客人，不一定必须身份很高。这里以海报中的角色为依据。'),
('辅导员','工作坊邀请专门指导、帮助他人处理问题的人员分享方法。','哪一个称呼符合海报介绍？',['辅导员','售票员','裁判员','播音员'],'本课的辅导员负责指导和帮助他人，不能把这个职务只限定在营队或宿舍。')]
positions=[2,0,3,1,1,3,0,2,3,2,1,0,2,1,0,3];tasks=[]
for i,(word,context,q,options,why) in enumerate(rows):
 right=options[0];others=options[1:];j=positions[i];ops=others[:j]+[right]+others[j:]
 tasks.append(dict(id='usage-'+str(i+1),title=str(i+1)+' · '+word,lesson=1,order=i+1,range=[i+1],focus=[i+1],questions=[q],mode='objective',guide='按需要选词复习。先判断语境，再看解释。',keywords=[],checks=[dict(id='choice',question=q,options=ops,correct=j,why=[why if x==right else '这项没有准确回应当前语境。'+why for x in ops])],answer=right,explain=why,hints=['回看左边，找出人物的需要或做法。','比较选项分别强调什么，再选最符合本句的一项。'],points=['根据语境判断','能说明其他项为什么不合适'],source='教师补充语境 · 旧词语练习优化',role='按需独立复习',reject='不要只凭一个词或答案位置猜测。',scoreGuide='客观点选1项，记录首次与订正。'))
L=dict(id='s1u4l1-vocab',title='培养好习惯 词语复习',label='中一高级华文 · 单元四 · 词语复习',grade=1,unit=4,version='20261023-habits-vocab-1',sequenceVersion=1,unitNoun='部分',wordEnglishVisible=True,paragraphs=[r[1] for r in rows],paragraphLabels=[r[0]+' · 练习语境' for r in rows],paragraphIdeas=[r[4] for r in rows],panels=[[] for _ in rows],panelRects=[],panelImages=[],tasks=tasks)
(D/'content.js').write_text('window.LESSON='+json.dumps(L,ensure_ascii=False)+';')
lex=json.loads((M/'lexicon.js').read_text().removeprefix('window.LESSON_WORDS=').strip().removesuffix(';'))
for key,v in lex.items():v['paragraph']=next((i+1 for i,r in enumerate(rows) if r[0]==key),1)
(D/'lexicon.js').write_text('window.LESSON_WORDS='+json.dumps(lex,ensure_ascii=False)+';')
s=(M/'reading.html').read_text().replace('../../../shared/lesson-v1/','../../../../textbook/shared/lesson-v1/').replace('href="lesson.css','href="../../../../textbook/1hcl/unit4/peiyang-hao-xiguan/lesson.css').replace('src="lesson-support.js','src="../../../../textbook/1hcl/unit4/peiyang-hao-xiguan/lesson-support.js')
s=s.replace('src="word-context.js','src="../../../../textbook/1hcl/unit4/peiyang-hao-xiguan/word-context.js')
s=s.replace('<a class="btn" href="../../../../ciyu/1hcl/unit4/peiyang-hao-xiguan/#lesson1">词语闯关</a>','')
s=s.replace('培养好习惯 · 互动学习','培养好习惯 · 词语闯关').replace('<button data-view="read">读文</button>','').replace('>本课问题</button>','>词语闯关</button>').replace('href="index.html">主页','href="../../../../textbook/1hcl/unit4/peiyang-hao-xiguan/index.html">课文主页')
s=s.replace('<main>','<main><p class="reading-return">按需选择词语练习。<a href="../../../../textbook/1hcl/unit4/peiyang-hao-xiguan/reading.html">返回课文学习</a></p>')
s=s.replace('<script src="content.js','<script>if(!location.hash)history.replaceState(null,"","#lesson1");</script><script src="content.js')
s=s.replace('<script src="../../../../textbook/shared/lesson-v1/cloud-bootstrap.js?v=20261023-habits-1"></script>','').replace('<script src="../../../../textbook/shared/lesson-v1/cloud.js?v=20261023-habits-1"></script>','')
(D/'index.html').write_text(s)
(D/'README.md').write_text('# 中一单元四 生活空间 培养好习惯词语复习\n\n原网址保留。2026-10-23：原16词38题改为每词一道明确语境用法题，支持按需选题、首次答案、提示后订正和本地保存。没有从旧页迁移作答，因旧页未保存答案。\n\n旧版由Git历史保留，不再提供重复课堂入口。四个课本词义题在课文主学习页口头完成。\n\n共用lesson-v1引擎，内容与代码分离。词语本归入s1u4l1。\n')
p=R/'du/textbook/shared/lesson-v1/catalog.js';c=json.loads(p.read_text().removeprefix('window.LESSON_CATALOG=').strip().removesuffix(';'))
for x in c:
 if x['id']=='s1u4l1' and 's1u4l1-vocab' not in x['aliases']:x['aliases'].append('s1u4l1-vocab')
p.write_text('window.LESSON_CATALOG='+json.dumps(c,ensure_ascii=False,separators=(',',':'))+';\n')
print('Built 16 contextual vocabulary questions; each answer position used 4 times')
