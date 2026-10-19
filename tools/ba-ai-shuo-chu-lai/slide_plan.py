from pathlib import Path
import json,sys
L=json.loads(Path(sys.argv[1]).read_text()); slides=[]
def add(title,lines,lesson=1,kind='teach',panel=None,notes='',task=None):
    if task is not None:
        t=next(t for t in L['tasks'] if t['id']==task);notes='来源：'+t['source']+'。任务身份：'+t['role']+'。\n'+notes+'\n参考：'+t['answer']+'\n常见误区：'+t['reject']+'\n提示1：'+t['hints'][0]+'\n提示2：'+t['hints'][1]
    slides.append(dict(title=title,lines=lines,lesson=lesson,kind=kind,panel=panel,notes=notes))
add('把爱说出来',['中二高级华文　单元一','有爱在心，为什么难以开口？'],kind='cover',panel=27,notes='使用本次上传的原有漫画；不重画。建议3×50分钟，2×50分钟压缩用法见教师方案。')
add('一句话的温暖',['有人真诚地感谢你时，\n你有什么感受？','先想一想，不必公开私人经历。'],panel=12,notes='短导入3分钟。可用假设情境；不要求每人披露家庭经历，也不要求当堂给家长发消息。')
add('今天读懂什么',['比较人物表达爱的方式','用原文解释心理变化','说明结尾歌声与主题的关系'],notes='四个目标的完整表述见教师方案；开放回应贯穿第三课。')
add('女儿的崇拜',['从哪里可以看出女儿很崇拜“我”？'],kind='question',task='admiration-comparison')
add('证据怎样回答问题',['“再三赞叹”表现反复称赞。','“再看一遍”“爱不释手”表现珍爱文章。','这些具体表现支持“崇拜”。','直接信息（direct info）'],kind='answer',panel=3,task='admiration-comparison')
add('同样听文章，不同表现',['儿子的表现和女儿的有什么不一样？','同一件事，两个人都要答。'],kind='question',task='admiration-comparison')
add('比较的是具体表现',['女儿：赞叹，又拿文章重读。','儿子：拒绝听，马上逃走。','“截然相反”只是概括。'],kind='answer',task='admiration-comparison')
add('惯用语的比喻义',['碰钉子：遭到拒绝，目标未达到。','泼冷水：打击别人的热情。','口头禅：经常挂在口头的习惯语。'],task='idioms-context')
add('惯用语中的不同关系',['拍马屁：用好听的话讨好别人。','打退堂鼓：自己做事中途退缩。','谁对谁做什么？'],task='idioms-context')
add('用什么惯用语',['1. 他常常乱花钱，今天又向妈妈要钱，','　结果________。','2. 我们要对自己有信心，不要一遇到困难','　就________。','3. 我想去学街舞，但哥哥一直给我________，','　说我不适合跳舞。'],kind='question',task='idioms-context')
add('惯用语答案与依据',['1. 碰钉子：妈妈拒绝了要钱的要求。','2. 打退堂鼓：遇到困难，自己退缩。','3. 泼冷水：哥哥的话打击我的热情。'],kind='answer',task='idioms-context')
add('儿子爱“我”吗',['你觉得儿子爱“我”吗？为什么？','哪些是事实？哪些是推断？'],kind='question',task='son-love-v2')
add('判断不能超过证据',['事实：儿子拒听文章，否定妹妹的赞美。','可能：他不习惯赞美、说出感情。','不能单凭这些表现断定他不爱妈妈。'],kind='answer',task='son-love-v2')
add('“我”的感受',['结合上文女儿和儿子的表现，','说说“我”的感受。'],kind='question',task='family-feelings-v2')
add('女儿的话让“我”温暖',['第1段：有成就感。','第3段：无比愉快。','第8段：看到卡片，觉得再辛苦也值得。'],kind='answer',task='family-feelings-v2')
add('第10段写了什么',['第10段主要运用了哪一种人物描写？','表现了“我”怎样的特点？','是说出口的话，还是心里想的？'],kind='question',task='reflection-decision-v2')
add('从感激到决定',['“一边想”“扪心自问”：心理描写。','感谢母亲的付出：懂得感恩。','反省自己从未表达：善于反思。','体会女儿话语的温暖，决定学习她。'],kind='answer',task='reflection-decision-v2',notes='反思自己的原句包括连续两个问句。证据框支持加入多句，不以一句话限制学生。')
add('第二课　迟迟说不出口',['第十二至十五段','下定决心后，为什么还会退缩？'],lesson=2,kind='section',panel=21,notes='先一次一段阅读，再整合心理变化。')
add('“我”的心理变化',['下定决心（第11段）','害羞退缩，又鼓励自己（第12段）','寻找机会，仍不自在（第13段）','终于开口，紧张离开（第14–15段）'],lesson=2,notes='这些是教师概括，不冒充原文引句。让学生先根据段落口头排序，再揭示本页。')
add('为什么难以表达爱',['结合上文，说一说为什么“我”','难以向母亲表达爱。','证据 → 原因','不能只复述吃饭的经过。'],lesson=2,kind='question',task='difficulty-evidence')
add('原因要由证据推出',['“从未”“第一次”：不习惯直接表达。','“害羞”“心里有些疙瘩”：难为情。','所以面对母亲时，迟迟说不出口。','特定文化影响只是可能原因。'],lesson=2,kind='answer',task='difficulty-evidence')
add('女儿为什么“张大眼睛”',['可以删掉“张大眼睛”吗？','为什么？','细节的作用'],lesson=2,kind='question',panel=6,task='eyes-detail')
add('神态配合真诚的赞美',['不宜删掉。','“张大眼睛”表现惊喜与欣赏。','它和“真诚”“双眼含笑”等互相配合。','课本归为外貌描写，细分是神态。'],lesson=2,kind='answer',task='eyes-detail')
add('“破天荒”指什么',['“破天荒”是什么意思？','在文中有什么含义？'],lesson=2,kind='question',task='first-expression-v2')
add('第一次说出感谢和爱',['“破天荒”：以前从未有过。','文中指“我”第一次直接向母亲','说出感谢和爱。','她以前已有关爱，只是不曾这样表达。'],lesson=2,kind='answer',task='first-expression-v2')
add('能否删去这个比较',['可以去掉“比当年参加毕业考试”吗？','为什么？'],lesson=2,kind='question',task='details-effect-v2')
add('比较突出紧张程度',['不宜去掉。','把这次示爱与毕业考试的紧张作比较，','突出向母亲表达爱时格外紧张。','只说“紧张”，未说明紧张的程度。'],lesson=2,kind='answer',task='details-effect-v2')
add('通过比较把握人物特点',['从文中画出描写儿子、女儿和“我”的句子，','通过比较把握人物特点，理解文章主题。','特点 ＋ 行为依据 ＋ 解释','先自主概括，不从选项里挑特点。'],lesson=2,kind='question',task='character-comparison')
add('儿子与女儿',['儿子不愿赞美，说话直接。','依据：拒听文章，并否定妹妹的赞美。','女儿真诚欣赏，自然表达。','依据：赞叹、重读文章、称赞新衣。'],lesson=2,kind='answer',task='character-comparison',notes='接受证据支持的等义特点。不把“不愿赞美”扩大为“不孝、自私、不爱妈妈”。让学生比较自己的首次答案。')
add('女儿与“我”',['女儿自然地把爱说出来，也写卡片。','“我”心存感恩，懂得反思，','却不习惯开口：害羞、低头、说话断续。','证据必须解释具体特点。'],lesson=2,kind='answer',task='character-comparison')
add('第三课　熟悉的歌声',[L['paragraphs'][15]],lesson=3,kind='section',notes='完整第16段原文。先阅读，不急于公布主题。')
add('两次表达爱的回应',['女儿对“我”表达爱：','“我”的反应与感受是什么？','“我”对母亲表达爱：','母亲的反应与感受是什么？','行为写得明白，感受需要推断。'],lesson=3,kind='question',task='response-ending')
add('直接信息与必要推断',['“我”：有成就感、愉快，辛苦也值得。','母亲的行为：一边做饭，一边唱歌。','母亲的感受：受到爱与安慰，心情好转。','后一点须结合第9段的沉默来推断。'],lesson=3,kind='answer',task='response-ending')
add('最后一句的含义',['最后一句话有什么含义？','“自从父亲过世后，我还是第一次','听到这熟悉的歌声。”'],lesson=3,kind='question',task='response-ending')
add('歌声表现爱的力量',['第9段：抑郁、沉默寡言。','第16段：重新唱起歌。','母亲感受到爱与安慰，心情有所转变。','不能推断她从此完全摆脱悲痛。'],lesson=3,kind='answer',panel=30,task='response-ending')
add('文章主题',['“爱的语言让人觉得温暖，我们应该……”'],lesson=3,kind='question',task='character-comparison')
add('主题与两次表达',['我们应该把爱真诚地表达出来。','女儿的话，让“我”感到温暖。','“我”的表达，让母亲重新唱歌。'],lesson=3,kind='answer',task='response-ending')
add('第一次一定最难吗',['“我”认为第一次对母亲说出爱总是最难的。','你同意吗？为什么？'],lesson=3,kind='question',task='first-attempt-discussion')
add('不同立场怎样成立',['对不习惯表达的人，第一次要克服害羞。','对平时常表达的人，开口可能较自然。','因此可以同意、部分同意或不同意，','但理由必须说明适用的人或条件。'],lesson=3,kind='answer',task='first-attempt-discussion')
add('爱需不需要说出来',['你认为对家人的爱需不需要用语言表达出来？','说说你的理由。'],lesson=3,kind='question',task='express-love-open')
add('开放回应的四步',['立场：我怎么看？','理由：为什么？需要、影响或限制？','例子：什么具体事情能说明？','回扣：这个例子怎样支持我的立场？'],lesson=3,task='express-love-open')
add('一种合理的回答',['我认为需要，也要配合行动。','因为说出来能让家人明确感到被珍惜。','文中“我”表达爱后，母亲重新唱歌，','说明语言能把心里的爱传达给家人。'],lesson=3,kind='answer',task='express-love-open',notes='必须在学生独立提交后揭示。完整版参考答案见教师方案和网页；允许不同立场。')
add('另一种合理的方向',['也可以认为“不一定需要用语言”。','具体照顾也能让家人感受到爱。','例子须说明对方如何感受到关心，','并解释这怎样支持你的观点。'],lesson=3,kind='answer',task='express-love-open')
add('答案自检与订正',['我的理由是否回答了“为什么”？','例子是否具体、与立场一致？','我有没有解释例子怎样支持观点？','保留首次回答，在订正框补足。'],lesson=3,notes='不以关键词或字数自动评分。按四个意义单位分别反馈，教师复核。')
add('当堂整理',['把不熟的词加入个人词语本。','先回想，再翻卡核对。','保存或导出首次回答与订正。','当堂完成整理。'],lesson=3,notes='不加新短文、一周后小测或强制打卡。词语本与答案保存在同设备浏览器，可导出备份。')

add('第九段　母亲的情况',['为什么作者要写父亲过世后','母亲的情况？'],kind='question',task='mother-background')
add('理解母亲的心情与付出',['父亲过世后，母亲抑郁、沉默寡言。','她仍旧照顾家人、承担家务。','这些内容让我们理解“我”的感激。'],kind='answer',task='mother-background',notes='读到结尾后再回看歌声与此处的对照；此时不提前混入第16段。')
add('反思自己的两个问句',['“我不是常常因为女儿的甜言蜜语','而感到幸福吗？”','“我是不是应该学学女儿，勇敢地','向母亲表达感谢，表达爱呢？”'],kind='answer',task='reflection-decision-v2',notes='连续两个问句共同写出反思：先想到自己得到的温暖，再想到自己应该如何表达。原句完整写在第10段；证据框可连续加入。')
add('第十一段　下定决心',['第11段可不可以删掉？为什么？'],kind='question',task='determination')
add('承接反思，引出尝试',['不宜删掉。','这一段写“我”下定决心。','它承接上文的反思，','引出下文向母亲表达爱的尝试。'],kind='answer',task='determination')
# Indexes below refer to the original 45 slides plus the five existing-question additions.
order=[0,1,2,3,4,5,6,21,22,11,12,13,14,45,46,15,16,47,48,49,17,37,38,7,8,9,10,23,24,19,20,25,26,18,30,31,32,33,34,35,36,27,28,29,39,40,41,42,43,44]
slides=[slides[i] for i in order]
for i,slide in enumerate(slides):
    slide['lesson']=1 if i<20 else 2 if i<34 else 3
    if slide['title']=='同样听文章，不同表现':slide['notes']+=' 读完第2段再比较第1、2段。'
    if slide['title']=='今天读懂什么':slide['notes']+=' 问题严格按段落顺序进行，全文人物比较放在第16段之后。'

dest=Path(__file__).resolve().parents[2]/'du/textbook/2hcl/unit1/ba-ai-shuo-chu-lai/slides.json'
dest.write_text(json.dumps(slides,ensure_ascii=False,indent=2));print(len(slides),'slides')
