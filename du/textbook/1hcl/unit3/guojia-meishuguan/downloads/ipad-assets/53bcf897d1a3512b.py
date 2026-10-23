"""One content source for the National Gallery textbook package."""
import io,json, random, shutil
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'du/textbook/1hcl/unit3/guojia-meishuguan'
UPLOAD=ROOT.parent/'upload'
P=[
'新加坡国家美术馆位于市政区，占地6万4000平方米，大约有9个足球场那么大。它是东南亚地区面积最大的艺术博物馆之一，收藏了许多举世无双的东南亚艺术珍品。',
'你知道吗？新加坡国家美术馆藏着许多有趣的“秘密”，让我们一起去探索一下吧。',
'要探索国家美术馆的“秘密”，首先要从它的建筑开始。实际上，国家美术馆是由前最高法院和政府大厦合二为一，改建而成的。这两座标志性的历史建筑建于殖民地时代，在新加坡历史上扮演过举足轻重的角色。前最高法院在60多年里一直是新加坡司法制度的最高殿堂，政府大厦则见证了多个历史事件，例如，日本投降和新加坡宣布自治等。',
'今天，国家美术馆还保留着这两座建筑的部分原貌，例如，法庭内法官的座位、被告栏、棕色天花板等。这里有个鲜为人知的“秘密”——地下通道。那时，犯人不是从大门进来，而是从这个特别通道直接进入法庭被告栏的。',
'国家美术馆里的门也藏着“秘密”。馆内悬空桥两端古色古香的大门原本是窗户，经过设计师的巧思妙想，变成了我们现在看到的门，多有意思！',
'来到五楼，你甚至可以近距离观赏前最高法院的圆顶，这里也有个小“秘密”，这圆顶原本不是铜绿色的，是经过长年的氧化才变成现在这样的。',
'我们要探索的“秘密”还藏在国家美术馆的画作中。国家美术馆里馆藏丰富，共有9000余件收藏品，其中一幅画被称作“钱包里的名作”。对大多数人来说，它既熟悉又陌生。熟悉，是因为它就印在50新元钞票的背面，每个人都见过；陌生，是因为大多数人对这幅画并不了解。这幅名为《晒咸鱼》的画，展现了马来同胞晒咸鱼的场景，画面宁静而平和。在画家钟泗滨的笔下，过去东南亚沿海村落中常见的生活画面被生动地表现了出来。',
'国家美术馆的建立是我国推动艺术发展的重要的里程碑，它为我国长期以来收藏的大量东南亚艺术品，尤其是本地艺术家的优秀作品提供了一个永久的展示空间。在这个历史与艺术交融的美术馆里，还有很多“秘密”等待着你去探索、发掘。亲自去走一走，看一看，感受那浓浓的历史和艺术气息，说不定你也会有新发现，找到属于自己的秘密。'
]
labels=['美术馆有多大','一起探索“秘密”','两座历史建筑','保留原貌与地下通道','窗户变成大门','变色的圆顶','钱包里的名作','亲自探索与发现']
ideas=['用面积和足球场的数量，具体说明美术馆面积很大。','借用“秘密”引起读者的兴趣，邀请读者探索。','两座历史建筑改建成美术馆，曾在新加坡历史上发挥重要作用。','保留法庭部分原貌，地下通道曾让犯人直接进入被告栏。','悬空桥两端的大门原来是窗户，经过设计变成门。','圆顶经过长年氧化才变成现在的铜绿色。','馆藏丰富；《晒咸鱼》印在钞票上，却未必为人们所了解。','美术馆提供永久展示空间，作者鼓励读者亲自探索历史与艺术。']
panels=[[1,2,3],[4],[5,6,7,8],[9,10,11,12,13,14],[15,16],[17,18,19,20],list(range(21,29)),[29,30,31,32]]
roles=['教师示范','师生共构','学生独立','师生共构','学生独立','学生独立','学生独立','学生独立','师生共构','学生独立']
ids=['size','secrets','history','court','doors','dome','painting','ending','summary','language-research']
L=dict(id='s1u3l3',title='国家美术馆探秘',label='中一高级华文 · 单元三 · 巩固课文',grade=1,unit=3,version='20261023-gallery-1',sequenceVersion=1,paragraphs=P,paragraphLabels=labels,paragraphIdeas=ideas,paragraphTasks=ids[:8],simpleTaskGuide=True,wordEnglishVisible=True,accuracyLabel='客观任务首次全部答对率',objectiveSuccess='点选和证据已核对。请看解释，再订正。',panels=panels,tasks=[])
def select(id,label,correct,others):
    ops=[correct]+others; random.Random(id).shuffle(ops)
    return dict(id=id,label=label,type='select',options=ops,correct=correct)
def check(id,q,opts,correct,why):
    return dict(id=id,question=q,options=opts,correct=correct,why=why)
def task(n,title,questions,mode='objective',**kw):
    t=dict(id=ids[n-1],order=n,title=str(n)+' · '+title,lesson=1 if n<=7 else 2,range=[n] if n<=8 else [1,8],focus=[n] if n<=8 else [1],mode=mode,questions=questions,keywords=[],guide='先读原文，再作答。',checks=[],fields=[],evidence=[],points=[],hints=[],role=roles[n-1],source='教参问题改编互动',answer='',explain='',reject='')
    if n>=9:t['scope']='full'
    t.update(kw);L['tasks'].append(t);return t

task(1,'数字说明什么',['第1段的数字说明了国家美术馆的什么特点？'],
 keywords=['数字','什么特点'],guide='我做：先找数字和单位，再判断它说明什么。',source='课本第1段旁注原题；教参第1—2段',
 conceptNotes=[['列数字（use numbers）','用准确的数量说明特点。先看单位：平方米说面积，件说数量。'],['比较（comparison）','把不熟悉的大小，跟熟悉的事物比较，帮助想象。']],
 checks=[check('feature','这些数字主要说明什么？',['馆内收藏的艺术作品很丰富','美术馆所占的地方十分宽广','美术馆作为法院的历史悠久','馆内历史建筑的数量特别多'],1,['收藏丰富要看收藏品的数量，这里单位是平方米。','6万4000平方米与约9个足球场都指向面积大。','历史悠久要看时间，这里不是年份。','足球场是用来帮助想象面积，并非建筑数量。'])],
 evidence=[dict(label='加入说明面积的原句',p=[1],terms=['6万4000'],requiredTerms=['6万4000','9个足球场'])],
 answer='这些数字具体说明国家美术馆面积很大。6万4000平方米说明实际面积，约9个足球场帮助读者想象它有多大。',
 explain='数字要和单位一起读，再连接特点。不能只回答“用了列数字”。“大约”表示近似，“之一”也不能删去。',reject='只说“非常美”“收藏丰富”；漏掉数字与面积之间的关系；把“之一”说成唯一最大。',
 hints=['先看这些数字后面的单位。','“平方米”和“足球场那么大”都在说明同一个特点。'],points=['说出面积大','数字和单位没有写错','说明数字怎样帮助理解'],scoreGuide='课堂参考3点：面积大1；准确引用面积或比较1；说明具体、易想象1。各点独立，不作线上逐字评分。')
task(2,'“秘密”为什么加引号',['“秘密”为什么加引号？'],keywords=['“秘密”','引号'],source='课本第2段旁注原题；教参第1—2段',
 conceptNotes=[['借用（borrowed meaning）','把词借到新的语境。这里的“秘密”，需要结合美术馆的内容理解。']],
 checks=[check('quotes','这里加引号，主要因为“秘密”是——',['参观者向工作人员提出的问题','美术馆为这项活动规定的名称','馆方保留并要求参观者保密的事','借来称呼人们尚不熟知的趣事'],3,['这不是直接记录参观者的问话。','文章没有说“秘密”是正式活动名称。','这里的趣事可以公开介绍，并非要求保密。','借用“秘密”指鲜为人知、等待探索的趣事。'])],
 answer='作者借用“秘密”来说明美术馆里鲜为人知、等待人们探索的有趣事情。它们可以公开，并非通常所说不能让人知道的秘密，所以加上引号。',explain='把普通词义和本篇语境比较：不熟知，不等于不能公开。',reject='只答“强调”或“引用”；说这些事不能让公众知道。',hints=['普通的“秘密”通常能不能随意公开？','比较“鲜为人知”和“不能公开”。'],points=['说出借用','解释鲜为人知的趣事','没有误解为必须保密'],scoreGuide='课堂参考2点：借用1；说明与普通“秘密”的不同1。')
task(3,'两座建筑的历史',['美术馆由哪两座历史建筑改建而成？它见证了哪些历史事件？'],keywords=['哪两座','哪些历史事件'],
 checks=[check('importance','日本投降和宣布自治的例子说明什么？',['政府大厦承载了重要的历史','前最高法院收藏品数量丰富','美术馆的展览面积十分宽广','政府大厦今天仍然负责审案'],0,['这两个例子说明政府大厦见证重要历史事件。','原文把事件与政府大厦相连，和馆藏数量无关。','事件不能说明面积，需看第1段数字。','文中说的是历史作用，不是说今天仍负责审案。'])],
 fields=[select('buildings','由哪两座建筑改建？','前最高法院和政府大厦',['政府大厦和艺术博物馆','前最高法院和艺术学校']),select('events','政府大厦见证的历史事件','日本投降和新加坡宣布自治',['日本投降和美术馆首次展览','美术馆成立和新加坡宣布独立'])],
 answer='国家美术馆由前最高法院和政府大厦合二为一、改建而成。政府大厦见证了日本投降、新加坡宣布自治等历史事件。',
 explain='先分清说明对象，再连例子。前最高法院与司法制度有关；政府大厦与文中列举的历史事件有关。',reject='把“自治”改成“独立”；混淆两座建筑的历史作用。',hints=['第3段先介绍来源，再分别介绍两座建筑。','留意“前最高法院……政府大厦则……”的对应关系。'],points=['建筑名称齐全','事件符合原文','没有把自治改成独立'],scoreGuide='课堂参考4点：两座建筑各1；两个事件各1。',oral=[['“举足轻重”在这里是什么意思？','这两座建筑在新加坡历史上有重要影响。']])
task(4,'原貌和地下通道',['这里举的例子是为了说明什么？','国家美术馆的地下通道有什么用途？'],keywords=['例子','说明什么','用途'],source='课本第4段旁注原题；教参第3—7段',
 conceptNotes=[['举例子（give examples）','先有一个特点，再列出具体事物，让这个特点更清楚。']],
 checks=[check('original','法官座位、被告栏、天花板的例子说明——',['整座建筑仍保持当年全部模样','地下通道是今日游客必经之路','改建后仍可看见旧建筑的样貌','法庭家具都是艺术家的收藏品'],2,['原文限定“部分原貌”，不能扩大为全部。','这些例子说明原貌，不说明今天游客的路线。','这些具体保留下来的部分，让读者理解“部分原貌”。','家具是建筑原貌的例子，原文没说都是艺术藏品。'])],
 fields=[select('passage','地下通道当时让犯人怎样进入法庭？','从特别通道直接进入被告栏',['从美术馆大门进入展览厅','从悬空桥进入法官的座位'])],
 answer='这些例子说明美术馆还保留着两座建筑的部分原貌。地下通道当时让犯人不从大门进入，而从特别通道直接进入法庭被告栏。',
 explain='概括句后面列举座位、被告栏、天花板，让“部分原貌”变得具体。用途是文中明写的事实；通道是哪年建的，课文没有说明。',reject='把部分说成全部；把通道用途说成方便游客；断定具体建造年份。',hints=['先找“例如”前面的概括句。','“保留……部分原貌”和“直接进入……被告栏”分别回答两个问题。'],points=['举例对应部分原貌','用途准确','不把推测当成事实'],scoreGuide='课堂参考3点：部分原貌1；犯人使用1；直接到被告栏1。',oral=[['你认为这个通道来自哪个建筑？根据什么？','可合理推测来自前最高法院，因为通道通向法庭被告栏；这是结合第3、4段的推测，不是文中直接命名。']])
task(5,'门的“秘密”',['悬空桥两端的大门有什么“秘密”？','为什么用“古色古香”来形容这些大门？'],keywords=['什么“秘密”','为什么','古色古香'],
 fields=[select('before','这些门原本是什么？','窗户',['被告栏','法官座位'])],
 checks=[check('old-style','“古色古香”在这里突出大门的什么特点？',['颜色发黄并且散发古旧香气','保留古朴的样式与旧时韵味','刻着名画并陈列大量艺术品','采用时尚材料与新颖的装饰'],1,['不能把“色”“香”逐字解释成颜色和气味。','这个词形容古朴的色彩、格调与韵味。','原文没有说门上刻着名画。','“时尚新颖”不符合“古色古香”的语境。'])],
 answer='这些大门原本是窗户，经过设计师的巧思妙想才变成门。“古色古香”突出它们古朴、有旧时韵味的样式。',explain='“原本……变成……”说明改建的巧思。“古色古香”描述风格，不能按字面解释为香味。',reject='说门变成窗；说门发出香气；把漫画中的材质细节当作课文事实。',hints=['找“原本”和“变成”之间的变化。','看“古色古香”是在形容门的风格，还是气味。'],points=['变化方向正确','解释古朴韵味'],scoreGuide='课堂参考2点：窗变门1；古朴旧时韵味1。')
task(6,'圆顶为什么变色',['前最高法院的圆顶有什么“秘密”？','美术馆圆顶的颜色有了什么变化？为什么会出现这样的变化？'],keywords=['什么变化','为什么'],
 conceptNotes=[['氧化（oxidation）','材料长期与空气中的氧等发生化学变化。读本段时，只需抓住它与颜色变化的因果。']],
 checks=[check('cause','圆顶变成铜绿色的原因是什么？',['长期发生氧化使表面改变颜色','设计师为了改建重新涂上绿色','室内灯光让圆顶看起来像绿色','窗户的颜色映照在圆顶的表面'],0,['原文明确用“是经过长年的氧化才……”解释原因。','文中没有重新涂漆的说明。','文中没有把变色归因于灯光。','这是把门窗内容错误地移到圆顶上。'])],
 fields=[select('known','课文有没有说明圆顶原本的具体颜色？','只说原本不是铜绿色',['明确说原本是深棕色','明确说原本是鲜红色'])],
 answer='圆顶原本不是铜绿色，经过长年的氧化才变成现在的铜绿色。课文没有说明它原本的具体颜色。',explain='变化和原因都在同一句里。原漫画的颜色变化属于示意，答题不能据此补写课文没交代的原色。',reject='看图猜原本颜色；把改建或涂漆当作变色原因。',hints=['找“是经过……才……”这个因果句式。','课文写了现在的颜色，是否写了原本颜色的名称？'],points=['说出铜绿色','原因是长年氧化','没有编造原本颜色'],scoreGuide='课堂参考2点：变化1；原因1。原色边界不另计分。')
task(7,'钱包里的名作',['为什么把这幅画称为“钱包里的名作”？','为什么说对许多人来说，这幅画“既熟悉又陌生”？'],mode='written',keywords=['为什么','既熟悉又陌生'],source='课本第7段旁注原题；教参第3—7段',guide='先点选分清“熟悉”和“陌生”，再写一两句回答第一问。',
 checks=[check('familiar','哪项准确解释“既熟悉又陌生”？',['熟悉画家的名字，却不熟悉钞票','熟悉画中的人物，却不了解建筑','熟悉馆中的原画，却不熟悉作者','熟悉钞票上的图案，却不了解画作'],3,['原文没有说大多数人熟悉画家姓名。','原文说的是钞票图案，不是认识画中人物。','“见过”指钞票背面的图案，不保证见过原画。','看过图案与了解画作是不同层次，所以可以同时成立。'])],
 fields=[dict(id='why-wallet',label='为什么称为“钱包里的名作”？',placeholder='因为这幅名画……，所以……。')],
 answer='这幅名画《晒咸鱼》的图案印在50新元钞票背面，而钞票常放在钱包里，所以被称为“钱包里的名作”。人们熟悉钞票上的图案，却往往不了解画作本身，因此既熟悉又陌生。',
 explain='Direct Info：画印在50新元钞票背面。必要联系：钞票常放在钱包里。第二问要分别解释看过图案和了解画作，不能只答其中一面。',reject='说原画放进了钱包；把钞票正面写成背面；只解释熟悉或只解释陌生。',hints=['“钱包”里放的是什么？它与画有什么联系？','分别看“熟悉，是因为……”和“陌生，是因为……”。'],points=['画名与钞票背面正确','解释钞票与钱包的联系','熟悉与陌生两面齐全'],scoreGuide='第一问课堂参考2点：50新元钞票背面有该画1；连接钱包中的钞票1。第二问两面各1。书面答案教师按意义覆核。',oral=[['这幅画描绘了什么样的场景？','马来同胞晒咸鱼的场景，表现过去东南亚沿海村落的生活，画面宁静平和。'],['是哪一位画家的哪一幅画？','课文写作钟泗滨的《晒咸鱼》。作者英文名为Cheong Soo Pieng，部分官方资料写作钟泗宾。']])
task(8,'你想亲自探秘吗',['作者在结尾呼吁读者做什么？','你也想亲自去美术馆探秘吗？为什么？'],mode='written',required=True,keywords=['呼吁','为什么'],source='课本第8段旁注原题；教参开放题',guide='先判断作者的呼吁，再写完整回答。立场可以不同，理由须具体。',concept='open',
 checks=[check('appeal','作者在结尾主要呼吁读者——',['搜集更多关于馆藏数量的资料','背熟所有历史事件的时间地点','亲自参观并发现历史艺术趣事','购买钞票并收藏喜欢的名画'],2,['搜集资料可以帮助学习，但不是结尾主要呼吁。','文中鼓励亲身探索，不是背诵时间地点。','“亲自去走一走，看一看”直接表达了呼吁。','原文没有购买钞票或名画的建议。'])],
 fields=[dict(id='open-response',label='我的看法、理由、具体内容与回扣',placeholder='我想／暂时不想……，因为……。课文介绍……，这让我……，所以……。')],
 answer='示例：我想亲自去探秘，因为我想知道旧建筑怎样与艺术展示结合。课文说悬空桥两端的大门原本是窗户，我想近距离观察这种改建，看看设计师怎样保留古朴风格。因此，亲自参观能帮助我把课文读到的内容看得更具体。',
 alternatives=['暂时不想也可：提出真实的个人兴趣或限制，引用相关内容，并解释为什么它影响自己的选择。不能只说“没有兴趣”。'],
 explain='开放题看立场、理由、具体例子和它们之间的联系。示例不是唯一答案，系统只保存与显示自检，不自动判定观点正确。',reject='只写“想，因为很好玩”；只抄景点信息，没有解释为何影响自己的选择。',hints=['从五个“秘密”中挑一个最影响你决定的内容。','解释：亲自看到这个内容，能够帮助你了解什么？或为什么暂时不适合你？'],points=['明确回答想或暂时不想','解释具体理由','有准确的课文内容或真实生活例子','说明例子怎样支持选择'],scoreGuide='课堂参考4点：立场1；理由1；例子1；回扣关系1。四点独立给分，不规定唯一立场；由教师覆核。',oral=[['国家美术馆为什么是艺术发展的里程碑？','它为大量东南亚艺术品，尤其本地艺术家的优秀作品，提供永久展示空间。']])

rows=[
('建筑','面积很大','6万4000平方米，约9个足球场','列数字（结合比较）',1),
('建筑','具有重要的历史意义','政府大厦见证日本投降和宣布自治','举例子',3),
('建筑','保留部分原貌','法官座位、被告栏、棕色天花板','举例子',4),
('画作','馆藏丰富','共有9000余件收藏品','列数字',7)
]
table_fields=[];table_rows=[]
for i,(obj,feature,ev,method,p) in enumerate(rows):
    names=[f'r{i}-feature',f'r{i}-evidence',f'r{i}-method']
    table_fields += [select(names[0],'事物的特点',feature,[r[1] for j,r in enumerate(rows) if j!=i]),select(names[1],'对特点的说明',ev,[r[2] for j,r in enumerate(rows) if j!=i]),select(names[2],'说明方法',method,[s for s in ['列数字','举例子','列数字（结合比较）'] if s!=method])]
    table_rows.append(dict(name=obj+' · 第'+str(p)+'段',fields=names))
task(9,'课本统整表',['阅读课文，了解课文内容，通过数字和例子理解事物的特点。'],keywords=['数字','例子','特点'],source='课本巩固练习二原题；保留建筑三行、画作一行',guide='看左边原文，逐行配对。每一行都要把特点、说明和方法连起来。',fields=table_fields,tableRows=table_rows,
 conceptNotes=[['特点—说明—作用','先找特点，再选能够证明它的数字或例子。说明方法帮助我们读懂特点。']],
 answer='建筑：面积很大——6万4000平方米、约9个足球场——列数字（结合比较）；历史意义重要——日本投降和宣布自治——举例子；保留部分原貌——座位、被告栏、棕色天花板——举例子。画作：馆藏丰富——9000余件收藏品——列数字。',
 explain='同样是数字，单位不同，说明的特点也不同。“平方米”说明面积，“件”说明馆藏数量；历史事件的例子与保留原貌的例子也不能混放。',reject='只写方法名称；把9000余件放在建筑面积；把地下通道用途当作保留原貌三个例子的总特点。',hints=['先按每一行的段号回看，暂时不急着选说明方法。','第1段看单位；第3、4段看“例如”前后；第7段看“馆藏丰富”。'],points=['每行特点与证据相符','数字与单位准确','例子说明了对应特点'],scoreGuide='课堂参考12格，各1点；“列数字（结合比较）”也接受“列数字并以足球场作比较”。各格独立，不因同一行错一格全行清零。')
task(10,'仿写与查找',['仿写句子：对我来说，________既熟悉又陌生。熟悉，是因为________；陌生，是因为________。','上网找一找，除了钟泗滨的画作，50新元钞票背面还有谁的画作？'],mode='written',keywords=['既熟悉又陌生','还有谁'],source='课本巩固练习一、三原题',guide='先写自己的句子，再打开资料查找画家。仿句与查找分开完成。',focus=[7],
 fields=[dict(id='imitation',label='我的仿句',placeholder='对我来说，……既熟悉又陌生。熟悉，是因为……；陌生，是因为……。'),select('artist','查找：另一位画家是谁？','陈文希（Chen Wen Hsi）',['钟泗滨（Cheong Soo Pieng）','蔡名智（Chua Mia Tee）']),select('artwork','查找：另一幅画的内容是什么？','藤蔓间的两只长臂猿',['沿海村落晒咸鱼的人们','站在教室里的学生与老师'])],
 resources=[dict(label='查阅新加坡金融管理局',url='https://www.mas.gov.sg/currency/circulation-currency/circulation-currency-notes'),dict(label='查阅国家美术馆资料',url='https://www.nationalgallery.sg/content/dam/about/annual-reports/reports/FY2016%20Annual%20Report.pdf#page=19')],
 answer='仿句示例：对我来说，学校附近的老建筑既熟悉又陌生。熟悉，是因为我每天上学都会经过；陌生，是因为我不知道它过去有什么用途。查找参考：陈文希（Chen Wen Hsi）的 Two Gibbons Amidst Vines，画中是藤蔓间的两只长臂猿。',
 explain='仿句的“熟悉”和“陌生”必须说同一个对象的不同层面，分别解释原因。查找题按画家与画作核对；这里用英文原题名，中文只说明画面内容。',reject='前后换了对象；只重复“因为很熟悉／很陌生”；只交立场而没有两面原因；把钞票设计者当成画作作者。',hints=['仿写：选一个你常见到、却还不真正了解的对象。','查找：MAS资料的Portrait Series $50部分说明两幅画；国家美术馆资料PDF第19页列出另一位画家。'],points=['同一个对象','熟悉和陌生都有具体原因','画家与画面相符','仿句通顺'],scoreGuide='仿句课堂参考3点：同一对象1；熟悉原因1；陌生原因1。查找2点：陈文希1；长臂猿画1。系统不自动评价仿句。')

L['tasks'][8]['questions'].insert(0,'国家美术馆藏了哪些秘密？')
L['tasks'][8]['source']='课本第8段旁注原题、巩固练习二原题；保留建筑三行、画作一行'
L['tasks'][8]['guide']='先口头说出五个“秘密”，再看原文逐行配对表格。'
L['tasks'][8]['answer']='五个“秘密”：两座历史建筑合建的来历；地下通道的用途；窗户变成门；圆顶因氧化而变色；钞票上的《晒咸鱼》。\n'+L['tasks'][8]['answer']

VOC=[
(1,'市政区','城市中行政机构及重要公共建筑集中的地区。','the civic district, where major public and government buildings are located'),
(1,'占地','建筑或场所所使用的土地面积。','occupy an area of land'),
(1,'平方米','测量面积的单位。','square metre, a unit of area'),
(1,'收藏','收集并保存有价值的物品。','collect and preserve valuable objects'),
(1,'举世无双','全世界没有第二个能相比，形容极为独特。','unique in the world; without equal'),
(1,'珍品','珍贵的物品。','a rare and valuable object'),
(2,'秘密','这里借指鲜为人知、值得探索的趣事。','here, a little-known fact waiting to be discovered'),
(2,'探索','通过观察、寻找，了解未知的事。','explore and learn about something not yet known'),
(3,'最高法院','司法体系中具有最高地位的法院。','the Supreme Court'),
(3,'合二为一','把两部分合在一起，成为一个整体。','combine two parts into one'),
(3,'改建','在原有建筑的基础上改变结构或用途。','alter or convert an existing building'),
(3,'标志性','具有代表性，容易让人认出的。','iconic; representing a place and easily recognised'),
(3,'殖民地','受到外来国家统治的地区。','a territory ruled by another country'),
(3,'扮演','这里指发挥某种作用。','here, to play a role'),
(3,'举足轻重','地位重要，足以影响整体。','important and influential'),
(3,'司法制度','国家处理审判等法律事务的制度。','the system of courts and the administration of justice'),
(3,'殿堂','本指高大的建筑，这里比喻重要、庄严的场所。','literally a grand hall; here, an important and respected institution'),
(3,'见证','亲历、证明某件事情发生。','witness a historical event'),
(3,'投降','停止抵抗，向对方屈服。','surrender; stop resisting'),
(3,'自治','自行管理内部事务。','self-government in internal affairs'),
(4,'原貌','原来的样子。','the original appearance'),
(4,'法庭','法院审理案件的场所。','a courtroom where cases are heard'),
(4,'法官','依法审理和裁决案件的人。','a judge'),
(4,'被告栏','法庭中供被告站立或坐着受审的位置。','the dock, where the accused stands or sits during a trial'),
(4,'棕色','像棕毛的褐色。','brown'),
(4,'天花板','房间内部上方的顶面。','the ceiling'),
(4,'鲜为人知','很少有人知道。','known to very few people'),
(4,'通道','供人通过的路线或空间。','a passageway'),
(5,'悬空桥','架在空中、连接建筑两侧的桥。','an elevated bridge linking parts of the building'),
(5,'两端','一件事物的两头。','the two ends'),
(5,'古色古香','具有古朴的色彩、风格和韵味。','having an antique style and charm'),
(5,'巧思妙想','巧妙而有创意的构思。','clever and imaginative ideas'),
(6,'观赏','观看并欣赏。','view and appreciate'),
(6,'圆顶','半球状的屋顶。','a dome'),
(6,'铜绿色','铜表面长期变化后常见的青绿色。','the green colour of aged copper'),
(6,'氧化','材料与氧等发生化学变化。','oxidation, a chemical change involving oxygen'),
(7,'馆藏','博物馆等机构收藏的物品。','a museum or gallery collection'),
(7,'余','用在数目后，表示超过这个数。','more than; over a stated number'),
(7,'名作','著名的作品。','a famous artwork or literary work'),
(7,'熟悉','知道、见过或了解得较多。','familiar; seen or known before'),
(7,'陌生','不熟悉、不了解。','unfamiliar; not well known to someone'),
(7,'钞票','纸币。','a banknote'),
(7,'同胞','同一个国家或民族的人。','fellow members of a nation or community'),
(7,'场景','某一地方或活动呈现的情景。','a scene or setting'),
(7,'宁静','安宁、平静。','quiet and peaceful'),
(7,'平和','平静、温和。','calm and gentle'),
(7,'沿海','靠近海岸的地区。','along the coast; coastal'),
(7,'村落','村庄。','a village or rural settlement'),
(7,'生动','表现得鲜明，好像就在眼前。','vivid and lifelike'),
(8,'里程碑','本指路边标距离的石碑，这里比喻发展中的重要事件。','a milestone; an important event in a process of development'),
(8,'尤其','特别是。','especially; in particular'),
(8,'永久','长久不变的。','permanent; lasting'),
(8,'展示','把事物陈列出来，让人观看。','display or present for people to see'),
(8,'交融','相互融合在一起。','blend or come together'),
(8,'发掘','这里指发现原来没有注意到的事物或意义。','uncover or discover something previously unnoticed'),
(8,'气息','这里指能感受到的特色或氛围。','an atmosphere or distinctive quality')
]
W={w:dict(meaning=m,en=en,paragraph=p) for p,w,m,en in VOC}
assert all(w in P[d['paragraph']-1] for w,d in W.items())
for n in range(1,5):
    src=UPLOAD/f'国家美术馆探秘-{n}.png';shutil.copyfile(src,OUT/f'assets/comic{n}.png')
# Lossless extraction of existing panel rectangles; no resizing, repainting or text edits.
rects_by_page=[
[(0,82,530,370),(535,82,489,370),(0,456,543,350),(549,456,475,350),(0,810,522,329),(527,810,497,329),(0,1145,474,391),(481,1145,543,391)],
[(0,82,528,343),(534,82,490,343),(0,433,523,361),(528,433,496,361),(0,800,517,336),(523,800,501,336),(0,1143,518,391),(524,1143,500,391)],
[(0,82,524,363),(529,82,495,363),(0,453,524,338),(529,453,495,338),(0,799,506,327),(513,799,511,327),(0,1133,480,394),(488,1133,536,394)],
[(0,81,527,330),(532,81,492,330),(0,416,536,341),(543,416,481,341),(0,763,511,334),(517,763,507,334),(0,1104,511,429),(517,1104,507,429)]
]
L['panelRects']=[];L['panelSheets']=[];L['panelImages']=[]
for sh,rs in enumerate(rects_by_page,1):
    im=Image.open(OUT/f'assets/comic{sh}.png')
    assert im.size==(1024,1536),im.size
    for rect in rs:
        n=len(L['panelImages'])+1;x,y,w,h=rect
        f=f'assets/panel-{n:02}.png';buffer=io.BytesIO();im.crop((x,y,x+w,y+h)).save(buffer,format='PNG',optimize=True);(OUT/f).write_bytes(buffer.getvalue())
        L['panelRects'].append(rect);L['panelSheets'].append(sh);L['panelImages'].append(f)
for t in L['tasks']:
    assert t['hints'] and t['points'] and t['scoreGuide']
for file,obj,prefix in [('lesson.json',L,''),('content.js',L,'window.LESSON='),('lexicon.js',W,'window.LESSON_WORDS=')]:
    (OUT/file).write_text(prefix+json.dumps(obj,ensure_ascii=False,indent=2)+(';' if prefix else '')+'\n')
(OUT/'lexicon.js').write_text((OUT/'lexicon.js').read_text()+'window.WORD_ALIASES={};\n')
print('Created',len(P),'paragraphs',len(L['tasks']),'tasks',len(W),'bilingual words')

(OUT/'content.js').write_text((OUT/'content.js').read_text()+'window.HWT_WORD_CONTEXT=()=>({lessonId:LESSON.id,lessonTitle:LESSON.title,grade:LESSON.grade,unit:LESSON.unit,paragraphs:LESSON.paragraphs});\nwindow.HWT_WORD_LEXICON=()=>window.LESSON_WORDS;\n')
