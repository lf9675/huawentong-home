from pathlib import Path
import json
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1];O=R/'repo/du/textbook/1hcl/unit2/xingyun-jiaozi';L=json.loads((O/'lesson.json').read_text())
D=Document();sec=D.sections[0];sec.page_height=Inches(11.69);sec.page_width=Inches(8.27);sec.top_margin=sec.bottom_margin=Inches(.7);sec.left_margin=sec.right_margin=Inches(.75)
for name in ['Normal','Title','Heading 1','Heading 2','Heading 3']:
 st=D.styles[name];st.font.name='Noto Serif CJK SC';st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Noto Serif CJK SC');st.font.color.rgb=RGBColor(0,0,0)
D.styles['Normal'].font.size=Pt(11);D.styles['Normal'].paragraph_format.space_after=Pt(3);D.styles['Normal'].paragraph_format.line_spacing=Pt(15)
for name,size in [('Title',24),('Heading 1',18),('Heading 2',14),('Heading 3',12)]:D.styles[name].font.size=Pt(size)
def p(t,style=None,kai=False):
 z=D.add_paragraph(t,style);z.paragraph_format.widow_control=True
 if kai:
  for run in z.runs:run.font.name='Huawentong WenKai';run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Huawentong WenKai')
 return z
def h(t,new=False):
 z=D.add_heading(t,1);z.paragraph_format.space_before=Pt(8);z.paragraph_format.space_after=Pt(5);z.paragraph_format.page_break_before=new;return z
def table(headers,rows,widths):
 t=D.add_table(rows=1,cols=len(headers));t.autofit=False
 for c,w in zip(t.columns,widths):c.width=Inches(w)
 for i,v in enumerate(headers):t.rows[0].cells[i].text=v
 rep=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(rep)
 for row in rows:
  for c,v in zip(t.add_row().cells,row):c.text=str(v)
 for ri,row in enumerate(t.rows):
  for i,c in enumerate(row.cells):
   c.width=Inches(widths[i]);pr=c._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
   for side in ['top','left','bottom','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');b.append(el)
   pr.append(b);mar=OxmlElement('w:tcMar')
   for side in ['top','bottom','left','right']:
    x=OxmlElement('w:'+side);x.set(qn('w:w'),'80');x.set(qn('w:type'),'dxa');mar.append(x)
   pr.append(mar)
   if ri==0:
    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'DDEBF5');pr.append(shade)
   for par in c.paragraphs:
    par.paragraph_format.space_after=Pt(2);par.paragraph_format.line_spacing=1.1
    for run in par.runs:run.font.size=Pt(10);run.bold=ri==0
 return t
p('幸运饺子 教师教学流程与参考答案','Title')
p('中一高级华文  单元二  巩固课文  1—2课时')
p('本课按人物行动读懂亲情，再解释词句、分清线索与主题。学生先答后对照，书面任务集中在人物证据、开放回应与一句仿写。建议两课各40分钟。')
h('核心目标')
for x in ['依据人物动作和语言，说明转送饺子的用意。','结合语境解释“眨眨眼”“偷龙转凤”与引号。','分清事物线索与主题，并用课文和真实经历支持理解。']:p('• '+x)
h('两课时流程')
table(['课次','环节','分钟','安排'],L['flow'],[.65,1.25,.45,4.35])
p('两课分别40分钟，共80分钟。资料比较为口头任务，不增加一份长篇报告。')
h('文本结构与图文对应',True)
table(['段落','主要内容','漫画格'],[(str(i+1),L['paragraphIdeas'][i],str(L['panels'][i][0])+'—'+str(L['panels'][i][-1]) if len(L['panels'][i])>1 else str(L['panels'][i][0])) for i in range(8)],[.55,4.9,1.25])
h('教学难点与支架')
p('“送出”与“不要”：人物把幸运饺子给家人，是把祝愿送给对方。要求学生把行动和原因一起读。')
p('“细心”与“手巧”：用发现小动作、发现换碗证明细心；包得漂亮不能直接证明本题的细心。')
p('词语本义与语境义：“偷龙转凤”在本课借写悄悄送祝福，不能按本义把姑姑说成做坏事。')
p('线索与主题：先给具体例子讲“串起几件事”，再看课本七行；线索不只凭词语反复出现。')
h('一课时安排')
p('适用于已完成图文预读的班级。50分钟：导入3，逐段原题15，人物证据7，线索主题5，开放回应9，仿句4，资料比较5，检查2。保留全部课本题，压缩重复展示与汇报。未预读且阅读困难时采用两课时。')
h('第1段导入')
p('原题：中国北方人为什么喜欢在大年三十吃饺子？',kai=True)
p('先依据课文回答传统与喜悦；可补充饺子寄托团圆、好运的祝愿（中国文化网）。不把资料补充当课文原句。原漫画的人物性别、场景装饰不作为文本推断的证据。')
Q={
'mark':'第2段：“我想偷偷在幸运饺子上做个记号，却被姑姑打了手。”',
'grandma':'第3段：“我赶紧把幸运饺子夹到奶奶的碗里，因为奶奶向来最疼爱我。”',
'wink':'第4段：“奶奶虽然视力不好，但还是发现了。她慈爱地对我眨眨眼，然后把幸运饺子夹到妈妈的碗里。”',
'careful':'第2段：偷偷做记号，却被姑姑打了手。第5段：“妈妈趁姑姑不注意，又和姑姑换了碗。姑姑是个细心的人，马上就发现了碗里的幸运饺子。”',
'swap':'第6段：“原来是姑姑‘偷龙转凤’，把幸运饺子放到了我的碗里。”',
'family':'第7段：“爸爸装出可怜的样子”；“大家立刻把自己碗里的饺子夹到他的碗里”；“爸爸笑了，一家人都笑了。”',
'thread':'第1—7段围绕幸运饺子展开，第8段点明开心团聚更重要。课本七行完整显示在互动页。',
'open':'第2—7段互送祝愿，第8段：“吃没吃到幸运饺子并不重要，重要的是，我们一家人能够开开心心地团聚在一起。”',
'sentence':'第8段课本例句；“并不重要，重要的是”比较同一件事的轻重。',
'compare':'资料：北方常见饺子；新加坡华人常见捞鱼生和吉祥话。只概括常见习俗，不断言所有家庭。'}
scores={'mark':'教师参考2点：有记号可有意挑选1点；维护凭运气吃到的规则1点。','grandma':'教师参考2点：具体行动1点；回报奶奶疼爱的心意1点。','wink':'教师参考2点：眨眼较隐蔽、不易被别人发现1点；能表现彼此默契1点。','swap':'教师参考3点：本义1点；文中具体动作1点；借用引号作用1点。','family':'教师参考3点：转送祝愿1点；融洽互爱1点；普通饺子也带着心意1点。','thread':'教师参考2点：幸运饺子为事物线索1点；亲情与开心团聚的主题1点。'}
for ix,t in enumerate(L['tasks']):
 h(str(ix+1)+' '+t['title'],ix%2==0)
 p(t['role']+'。'+t['source'])
 for q in t['questions']:p(q,kai=True)
 p('文本依据：'+Q[t['id']],kai=True)
 p('参考答案：'+t['answer'],kai=True)
 p('信息加工与接受范围：'+t['explain'])
 p('常见失分：'+t['reject'])
 p('评价：'+scores.get(t['id'],t['scoreGuide']))
 p('提示一：'+t['hints'][0]+'  提示二：'+t['hints'][1])
 for q,a in t.get('oral',[]):p('口头追问：'+q+'  参考：'+a)
h('课堂操作与数据解释',True)
p('普通入口保留首次作答、尝试和订正，可填写姓名、班级、学号并导出完整备份、逐题CSV或文字记录。更换设备或清理浏览器前先导出。课文作答与个人词语本分开，重置本课不删除词语。')
p('教师从现有课文课堂看板创建班级任务，使用学生专属链接时，可沿用平台收件功能。普通链接和离线包不自动收件。主观题由教师覆核，页面“已对照”不等于理解正确。')
p('6组客观任务：做记号、送奶奶、眨眼、成语与引号、家庭关系与借称、线索主题。共有8个选择判断、1个线索点选，另有1处原文证据校验。首次全部答对率按已提交客观任务组数计算，不等同于逐项得分。教师示范与师生共构不能作为独立掌握证据。')
p('3道书面题：姑姑细心（参考3点）、第8段理解（4点）、仿句（2点）。评分按独立意义单位，不用字数或关键词命中假装自动判分。资料比较为口头任务，不纳入自动正确率。')
p('个人词语本沿用跨课文格式，按年级、单元、课文筛选。预设39条语境释义，学生自己收藏；未收录词仍可建卡并标“释义待补充”。闪卡“已记住”是自我标记。')
h('资源使用')
p('学生从reading.html进入。PPT在downloads；在线投影与PPT同序。四页原漫画完整保留在comics.html。整套包含字体与可编辑源文件。离线包可直接打开reading.html；投影用PPT或正式网页。教师资料公开含答案。')
h('资料来源')
p('课文、巩固练习、教参和四页漫画均由教师提供。参考答案为依据教材与教参整理的教学答案，不冒充官方评分细则。')
for s in L['sources']:p(s['label']+'\n'+s['url'])
p('外部资料于2026年10月22日核对。比较题只用年节食物与常见参与方式，不展开未经核实的起源传说。')
# A plain page number supports classroom reference.
f=sec.footer.paragraphs[0];f.alignment=2;r=f.add_run();fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');r._r.addnext(fld)
for node in D.styles.element.xpath('.//w:pBdr'):
 node.getparent().remove(node)
for node in D.element.xpath('.//w:pBdr'):
 node.getparent().remove(node)
D.save(O/'downloads/teacher-guide.docx');print('docx saved')
