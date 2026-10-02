"""Build the teacher-approved concise vocabulary format from reviewed TSV content."""
import json, re, html
from pathlib import Path
P=Path(__file__).parent; ROOT=P.parent

def rows(name,n):
    out=[]
    for line in (P/name).read_text().splitlines():
        if not line or line.startswith('#'):continue
        a=line.split('|');assert len(a)==n,(name,a);out.append(a)
    return out
C={a[0]:a[1:] for a in rows('contexts.tsv',3)}
Q={a[0]:a[1:] for a in rows('questions.tsv',5)}
cloze=rows('cloze.tsv',4)
cores=json.loads((P/'core.json').read_text())
original=json.loads((ROOT/'data.json').read_text())['lessons']
# Core words match the five transfer items; the rest remain available for targeted practice.
visual=set('犹豫 不分青红皂白 窒息 代沟 疏远 迎刃而解 碰钉子 泼冷水 疙瘩 心不在焉 安抚 和事佬 缠绕 蹒跚 光辉 穿梭 辨识 馋 光泽 仰 凝望 畏罪潜逃 盘旋 面面相觑 茂盛 扒开 掀开 俯下 水喉 蓄水池 趋势 风靡 垄断 遏制 泛滥 渗透 锐减 罪魁祸首 羡慕 诱惑 毅力 闪烁其词 魂不守舍 蜷缩 通宵 掩饰 涩涩 涌动 捅'.split())
feedback={
'疲惫':'“瘫坐”“连说话的力气也没有”，说明爸爸累得厉害，不是故意不理家人。',
'犹豫':'想进去又退回来：想安慰，又担心打扰，所以拿不定主意。',
'内疚':'不安来自“可能错怪了孩子”，是觉得自己有过错。',
'代沟':'爸爸和孩子对游戏的看法不同，又难以理解彼此，形成了两代人的隔阂。',
'崇拜':'“您真的好棒”表现出钦佩，不只是同情妈妈。',
'爱不释手':'看完还要再看，是喜爱得舍不得放下，不是手放不开。',
'精疲力竭':'累得连站起来做饭都困难，突出精神和力气快耗尽。',
'抑郁':'沉默、少有笑容，写失去亲人后低落苦闷的心情；这里不作医学诊断。',
'仓促':'抓起包就跑，连告别也没说完整，说明匆忙、没从容安排。',
'庸俗':'作者起初觉得穿戴俗气，这是主观印象，不能由外貌判断一个人的品格。',
'摔跤':'两只小熊相互较力，想让对方倒下；这里不是走路时自己跌倒。',
'惩罚':'因认定有过错而处罚，叫惩罚；但课文中的认定后来被证明是错的。',
'畏罪潜逃':'畏罪是怕因犯罪受罚，潜逃是偷偷逃走。课文中只是家人的错误猜测。',
'光彩夺目':'鲜亮的颜色一下吸引了大家的目光，突出鲜明耀眼。',
'啼':'对象是小鸟，所以是鸟叫；如果是婴儿，“啼”也可以指哭。',
'娇嫩':'这里描写雏鸟的叫声细弱柔嫩；娇嫩也能形容皮肤、花叶等。',
'掀开':'掀开是往上揭起。作者说“决不掀开”，是怕惊动鸟，并没有真的这样做。',
'涂上颜色':'用画笔把颜料抹到表面，是涂；不是剪纸或折纸。',
'吨':'1000千克＝1吨；吨用来表示质量，不是长度。',
'亿':'1亿＝10000万＝100000000；注意“万”与“亿”的倍数。',
'因素':'有水才能支持生产、生活，所以水是影响发展的条件，不是发展的结果。',
'锐减':'两年内由十万减到四万，时间短、减得多，所以用锐减。',
'庸俗':'说穿戴俗气、不高雅，是作者最初的主观印象，不是说母亲贫穷或没有爱心。',
'罪魁祸首':'鹿群过多导致过量啃食，成为主要祸因；不是说鹿有人的犯罪意图。',
'反驳':'不同意“没影响”，并说明灯光照在脸上，提出理由反对原来的说法。',
'诡异':'古怪的笑让观察者不安；不能只凭“诡异”就认定真的有鬼。',
'瑟瑟':'这段情境写她害怕，所以发抖；瑟瑟发抖也可以由寒冷引起。',
'棉':'棉说的是材料；即使染成蓝色，仍然可以是棉帽。',
'县':'邻是附近、相邻；邻县是附近的另一个县，不是邻居家。'
}
refs={
'疲惫':['香港中文大学《汉语多功能字库》：疲','https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/search.php?word=%E7%96%B2'],
'迎刃而解':['教育部《成语典》：迎刃而解','https://dict.idioms.moe.edu.tw/idiomView.jsp?ID=-247&la=0&webMd=1'],
'不分青红皂白':['教育部辞典：青红皂白','https://dict.revised.moe.edu.tw/dictView.jsp?ID=20200&la=0&powerMode=0'],
'爱不释手':['教育部辞典：爱不释手','https://dict.revised.moe.edu.tw/dictView.jsp?ID=147208&la=0&powerMode=0'],
'扪心自问':['教育部辞典：扪心自问','https://dict.revised.moe.edu.tw/dictView.jsp?ID=30250&la=0&powerMode=0'],
'风靡':['教育部辞典：风靡一时','https://dict.revised.moe.edu.tw/dictView.jsp?ID=36944&la=1&powerMode=0'],
'穿梭':['教育部《成语典》：梭的形象','https://dict.idioms.moe.edu.tw/idiomView.jsp?ID=869&la=0&webMd=1'],
'炙':['香港中文大学《汉语多功能字库》：炙','https://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/search.php?word=%E7%82%99']}
lessons=[]
for old in original:
    l={k:old[k] for k in ['id','unit','lesson','title']}
    l['cloze']=[dict(word=w,sentence=s,hint=h) for id,w,s,h in cloze if id==l['id']]
    l['core']=cores[l['id']]
    l['groups']=[list(range(len(l['cloze']))) ]
    l['words']=[]
    for w in old['words']:
        word=w['word'];note,scene=C[word];q,*opts=Q[word]
        ex=feedback.get(word,re.split(r'(?<=[。！？])',w['explain'])[0])
        # Preserve source-only evidence separately; the student sees clearly labelled learning scenarios.
        item=dict(word=word,note=note,scene=scene,question=q,options=opts,explain=ex,en=w['en'],
                  source=w['source'],sourceLabel=w['sourceLabel'],core=word in l['core'],
                  nodes=w['nodes'] if word in visual else [],reference=refs.get(word))
        if word=='代沟':item['nodes']=[{'icon':'person','label':'爸爸：游戏浪费时间'},{'icon':'gap','label':'彼此不理解'},{'icon':'person','label':'孩子：游戏让我放松'}]
        if word=='犹豫':item['nodes']=[{'icon':'heart','label':'想安慰爸爸'},{'icon':'person','label':'国明：进？不进？'},{'icon':'thought','label':'又怕打扰他'}]
        if word=='不分青红皂白':item['nodes']=[{'icon':'door','label':'孩子晚归'},{'icon':'ear','label':'没问清原因'},{'icon':'speech','label':'先责骂孩子'}]
        if word=='掩饰':item['nodes']=[{'icon':'heart','label':'真实：紧张'},{'icon':'face','label':'外表：微笑'}]
        if word=='罪魁祸首':item['nodes']=[{'icon':'deer','label':'鹿群过多'},{'icon':'leaf','label':'过量啃食'},{'icon':'forest','label':'森林受损'}]
        if word=='疲惫':item['culture']='疲：疒提示困乏状态，皮提示读音。惫原写作憊，从心，備声。可联系身体与精神来记，但两字的用法有重叠，不能硬分身体累与心累。'
        l['words'].append(item)
    assert len(set(l['core']))==5
    assert len(l['cloze'])==len(l['words'])
    assert {c['word'] for c in l['cloze']}=={w['word'] for w in l['words']}
    assert set(l['core'])<=set(w['word'] for w in l['words'])
    for c in l['cloze']:assert c['sentence'].count('__')==1
    lessons.append(l)
words=[w for l in lessons for w in l['words']]
assert len(words)==204 and len(C)==len(Q)==204
for w in words:
    assert len(w['options'])==3 and len(set(w['options']))==3,w['word']
    assert len(w['scene'])<=110,w['word']
    assert len(w['explain'])<=110,(w['word'],w['explain'])
D={'version':'20261002-full-bank-2','lessons':lessons}
(ROOT/'concise-data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
# Teacher reference is printable, with source quotations, never mixed into the initial student task.
esc=html.escape
h=['<!doctype html><html lang="zh-Hans"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>中二词语 · 教师参考</title><style>body{max-width:960px;margin:auto;padding:24px;font:18px/1.7 system-ui}h1,h2,h3,.cn{font-family:KaiTi,"Kaiti SC",serif}details{border-bottom:1px solid #ddd;padding:10px}summary{cursor:pointer}blockquote{color:#555;border-left:3px solid #aaa;padding-left:12px}small{color:#666}@media print{details>*{display:block}summary{font-weight:bold}h2{break-before:page}}</style><a href="index.html">学生学习单</a><h1>中二词语 · 教师参考</h1><p>每课保留 5 个课堂重点词；选词填空覆盖本课全部词语，全课词语放在同一个词库中供每题选择。其余词义练习按需补练。中文情境是教学改编或新设，非逐字原句。教学目标：联系字词线索理解词义、辨明语境用法、迁移选词。无需打字，不计时、不排名。</p><p>字源有据才讲；语义拆解和形象联想不冒充字源。“疲／惫”的身体与精神只是记忆线索。首次选对、重试后选对分开记录在本机，不作考试评分。</p><p>词表核对：捧跤依原文改作摔跤；末课重复词去重。吨为词表延伸；“涂上颜色”为词表短语，课文相关说法是“涂了蜡似的小红嘴”。《猫》中的畏罪潜逃是人物的错误猜测；《恐怖事件》的诡异不证明有鬼。</p>']
for l in lessons:
    h.append(f'<h2>单元{l["unit"]} · 第{l["lesson"]}课《{esc(l["title"])}》</h2><a href="index.html#{l["id"]}">打开本课</a><p>课堂重点：{esc("、".join(l["core"]))}</p>')
    for w in l['words']:
        h.append(f'<details><summary>{esc(w["word"])} · {esc(w["question"])}</summary><p>线索：{esc(w["note"])}</p><p>学习情境：{esc(w["scene"])}</p><p><b>答案：</b>{esc(w["options"][0])}</p><p>解析：{esc(w["explain"])}</p><p>干扰项：{esc("；".join(w["options"][1:]))}</p><blockquote>{esc(w["source"])}</blockquote><small>{esc(w["sourceLabel"])}；用于复核词义，不要求学生逐词找证据。</small>')
        if w['reference']:h.append(f'<p><a href="{w["reference"][1]}">{esc(w["reference"][0])}</a></p>')
        if w['word']=='疲惫':h.append('<p><a href="https://dict.variants.moe.edu.tw/dictView.jsp?ID=15964&la=0">教育部字典：憊</a></p>')
        h.append('</details>')
    h.append('<h3>填空参考</h3><ol>')
    for c in l['cloze']:h.append('<li>'+esc(c['sentence']).replace('__','<b>〔'+esc(c['word'])+'〕</b>')+'</li>')
    h.append('</ol>')
h.append('</html>');(ROOT/'teacher.html').write_text('\n'.join(h))
print(f'Built {len(lessons)} lessons, {len(words)} context questions, {len(cloze)} cloze items; {sum(bool(w["nodes"]) for w in words)} visual supports.')
