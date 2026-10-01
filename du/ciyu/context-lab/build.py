"""Build the authored lesson content; no model calls or external dependencies."""
import json,re
from pathlib import Path
P=Path(__file__).parent
source=json.loads((P/'source-data.json').read_text())
rows={}
for u in range(1,5):
    for line in (P/f'unit{u}.tsv').read_text().splitlines():
        if not line or line.startswith('#'):continue
        a=line.split('|');assert len(a)==7,a
        assert a[0] not in rows,a[0]
        rows[a[0]]=a
glyphs={}
for line in (P/'glyphs.tsv').read_text().splitlines():
    if not line or line.startswith('#'):continue
    a=line.split('|');assert len(a)==6,a
    glyphs[a[0]]=dict(zip(['char','layout','parts','answer','wrong','explain'],a))
    first=a[2].split(',')[0]==a[3]
    glyphs[a[0]]['focus']={'左右':('左部','右部整体'),'上下':('上部','下部整体'),'半包围':('包围部分','里面的部分'),'左中右':('中间部分','中间部分')}[a[1]][0 if first else 1]
    if a[0]=='旋':glyphs[a[0]]['focus']='左边的方形部件'
    if a[0]=='魁':glyphs[a[0]]['focus']='右下部分'
# Only show accurate complete components; partial forms explicitly labelled.
glyphs['蹒']['parts']='⻊,艹与两组成的右部'
lessons=[]
for old in source['lessons']:
    l={k:old[k] for k in ['id','grade','unit','lesson','title','sourceTitle','artRatio']}
    l['words']=[]
    for i,w in enumerate(old['words']):
        term,nodes,q,a,b,c,reason=rows[w['w']]
        para=w['source']
        if term=='匿名':para='【匿名】15:12\n我喜欢玩电子游戏，可是爸爸每天只允许我玩半个小时，还天天监督我。'
        extension=term=='吨'
        if extension:para='塑料在工业生产和人们的日常生活中，都扮演着重要的角色。'
        target='涂了蜡' if term=='涂上颜色' else term
        # Whole sentences around the target, without manufacturing quotations.
        parts=[s for s in re.split(r'(?<=[。！？])',para) if s.strip()]
        j=next((j for j,s in enumerate(parts) if target in s),0)
        excerpt=''.join(parts[max(0,j-1):min(len(parts),j+2)]).strip()
        if len(excerpt)>220:excerpt=parts[j].strip()
        assert excerpt in para,(term,excerpt)
        ns=[]
        for node in nodes.split(' > '):
            icon,label=node.split(':',1);ns.append({'icon':icon,'label':label})
        item={'word':term,'index':i,'nodes':ns,'question':q,'options':[a,b,c],
              'explain':reason,'en':w['en'],'source':excerpt,'fullSource':para,
              'sourceLabel':'词表延伸；下方为本课相关原句' if extension else ('课文原句（含相关词形）' if term=='涂上颜色' else '课文原句'),
              'target':target,'extension':extension or term=='涂上颜色',
              'glyphs':[glyphs[ch] for ch in dict.fromkeys(term) if ch in glyphs]}
        assert len(set(item['options']))==3,term
        assert len(ns) in (2,3),term
        l['words'].append(item)
    lessons.append(l)
assert sum(len(l['words']) for l in lessons)==204
(P/'data.json').write_text(json.dumps({'version':'20261001-context-1','lessons':lessons},ensure_ascii=False,indent=2)+'\n')
print('Built 16 lessons / 204 word inquiries;',sum(bool(w['glyphs']) for l in lessons for w in l['words']),'words with targeted glyph comparisons')
