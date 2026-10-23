"""Apply approved direct-image and bilingual glossary fixes without changing lessons or records."""
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import json,re,subprocess
ROOT=Path(__file__).resolve().parents[2];VERSION='20261023-ipad-all1'
A=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./tools/textbook-ipad/inventory.cjs')(true)))"],cwd=ROOT))
translations={}
for line in Path(__file__).with_name('english.txt').read_text().splitlines():
 w,en=line.split('|',1);assert w not in translations,w;translations[w]=en
lookup={};jobs=[];report=[]
def replace_object(p,obj):
 s=p.read_text();i=s.index('{');_,n=json.JSONDecoder().raw_decode(s[i:]);p.write_text(s[:i]+json.dumps(obj,ensure_ascii=False,indent=2)+s[i+n:])
for a in A:
 d=ROOT/a['dir'];L=a['L'];legacy=d.name=='tuanyuanfan';words=a['words'];added=0
 for w,v in words.items():
  if not v.get('en'):
   v['en']=translations[w];added+=1
   if d.name=='yushu' and w=='随意':v['en']='freely, without a fixed pattern'
   if d.name=='yushu' and w=='疲惫':v['en']='exhausted; here, a human feeling attributed to leaves'
  lookup[w+'\n'+v['meaning']]=v['en']
 if d.name!='ba-ai-shuo-chu-lai':replace_object(d/'lexicon.js',words)
 if legacy:
  rects=[];sheets=[];ys=[[102,374,663,950,1222],[102,372,630,892,1172],[102,373,634,897,1174]];hs=[[264,282,282,267,302],[264,252,256,273,354],[264,255,256,269,351]]
  for n in range(30):sh=n//10;row=n%10//2;rects.append([517 if n%2 else 5,ys[sh][row],503,hs[sh][row]]);sheets.append(sh+1)
 else:rects=L['panelRects'];sheets=L.get('panelSheets') or [i//10+1 for i in range(len(rects))]
 paths=[];(d/'assets/panels').mkdir(exist_ok=True)
 for i,(r,sheet) in enumerate(zip(rects,sheets),1):
  source=d/(a['assets'][sheet-1] if legacy else f'assets/comic{sheet}.png');dest=d/f'assets/panels/panel-{i:02d}.png';paths.append(dest.relative_to(d).as_posix());jobs.append((source,r,dest))
 if legacy:
  s=subprocess.check_output(['git','show','88d102f6d15c4c7cc8672d2f31d332b4d3a91eaa:'+a['dir']+'/content.js'],cwd=ROOT).decode();s+='\nDATA.wordEnglishVisible=true;\nDATA.panelImages='+json.dumps(paths)+';\nDATA.panelRects='+json.dumps(rects)+';\n';(d/'content.js').write_text(s)
 else:
  L.update(wordEnglishVisible=True,panelImages=paths,version=VERSION)
  for row in L.get('idioms',[]):
   if len(row)<3:row.append(words[row[0]]['en'])
  for key,f in L.get('figures',{}).items():
   if f['kind'] in ('sourceImage','diagram'):
    dest=d/f'assets/panels/figure-{key}.png';jobs.append((d/f['src'],f['rect'],dest));f['directSrc']=dest.relative_to(d).as_posix()
  replace_object(d/'content.js',L)
 for p in d.glob('*.html'):
  s=p.read_text();s=re.sub(r'((?:src|href)=["\'][^"\']+\.(?:js|css))(?:\?[^"\']*)?(["\'])',lambda m:m[1]+'?v='+VERSION+m[2],s)
  def static_panel(m):
   alt=re.search(r'alt="([^"]+)"',m[0]);number=re.search(r'第(\d+|一)格',alt[1]) if alt else None
   if not number:return m[0]
   n=1 if number[1]=='一' else int(number[1]);r=rects[n-1]
   return f'<div class="panel panel-direct"><img src="{paths[n-1]}" alt="{alt[1]}" width="{r[2]}" height="{r[3]}" loading="eager" decoding="async"></div>'
  s=re.sub(r'<div class="panel"[^>]*>\s*<img[^>]*style="[^">]*left:[^">]*"[^>]*>\s*</div>',static_panel,s)
  old='`<div class="panel" style="aspect-ratio:${r[2]}/${r[3]}"><img src="assets/comic${L.panelSheets[n-1]}.png" alt="原有漫画第${n}格" style="width:${1024/r[2]*100}%;left:${-r[0]/r[2]*100}%;top:${-r[1]/r[3]*100}%" loading="lazy"></div>`'
  s=s.replace(old,'`<div class="panel panel-direct"><img src="${L.panelImages[n-1]}" alt="原有漫画第${n}格" width="${r[2]}" height="${r[3]}" loading="eager" decoding="async"></div>`')
  old='`<div class="figure-crop" style="aspect-ratio:${r[2]}/${r[3]}"><img src="${f.src}" alt="${esc(f.alt||f.title)}" style="width:${f.imageWidth/r[2]*100}%;left:${-r[0]/r[2]*100}%;top:${-r[1]/r[3]*100}%"></div>`'
  s=s.replace(old,'`<div class="panel panel-direct"><img src="${f.directSrc}" alt="${esc(f.alt||f.title)}" width="${r[2]}" height="${r[3]}" loading="eager" decoding="async"></div>`');p.write_text(s)
 report.append({'dir':a['dir'],'title':L.get('title','团圆饭'),'words':len(words),'englishAdded':added,'panels':len(paths)})
# Current shared engine already has the pilot's direct panel and visible glossary support.
p=ROOT/'du/textbook/shared/lesson-v1/app.js';s=p.read_text();old='const sourceImage=()=>{const r=f.rect,src=window.LESSON_ASSETS?.[f.src]||f.src;'
new='const sourceImage=()=>{const r=f.rect;if(f.directSrc){const src=window.LESSON_ASSETS?.[f.directSrc]||f.directSrc;return `<div class="panel panel-direct"><img src="${esc(src)}" alt="${esc(f.alt||f.title)}" width="${r[2]}" height="${r[3]}" loading="eager" decoding="async"></div>`}const src=window.LESSON_ASSETS?.[f.src]||f.src;'
assert old in s;s=s.replace(old,new);p.write_text(s)
p=ROOT/'du/textbook/1hcl/unit2/tuanyuanfan/app.js';s=p.read_text();s="document.body.classList.add('word-support-visible');\n"+s;s=s.replace('Object.keys(DATA.glossary).sort','Object.keys(LESSON_WORDS).sort').replace('DATA.glossary[x]?','LESSON_WORDS[x]?');i=s.index('function comic(');j=s.index('\nfunction progress',i)
s=s[:i]+'''function comic(n,panel){const path=DATA.panelImages[panel-1],src=window.LESSON_ASSETS?.[path]||path,r=DATA.panelRects[panel-1];return `<div class="comic-panel panel-direct" data-panel="${panel}"><img src="${esc(src)}" width="${r[2]}" height="${r[3]}" loading="eager" decoding="async" alt="${DATA.paragraphNames[state.chunk]}，漫画第${panel}格"></div>`}'''+s[j:];s=s.replace('${bi(def.meaning,def.en)}','<p>${esc(def.meaning)}</p><p class="word-english" lang="en">${esc(def.en)}</p>');p.write_text(s)
p=ROOT/'du/textbook/1hcl/unit2/tuanyuanfan/style.css';s=p.read_text();s+='\n.word-support-visible .word{color:#bd202b;-webkit-text-fill-color:#bd202b;font-weight:700;text-decoration:underline solid #bd202b;text-underline-offset:5px}.comic-panel.panel-direct{background:transparent;aspect-ratio:auto;overflow:visible}.comic-panel.panel-direct img{display:block;width:100%;height:auto;position:static;max-width:100%}.word-english{font:18px/1.6 Arial,sans-serif;color:#34443d;margin:8px 0 18px}\n';p.write_text(s)
p=ROOT/'du/textbook/shared/lesson-v1/wordbook.js';s=p.read_text();s=s.replace("const englishVisible=()=>window.LESSON?.wordEnglishVisible===true;","const englishVisible=()=>window.LESSON?.wordEnglishVisible===true||(typeof DATA!=='undefined'&&DATA.wordEnglishVisible===true)||!!resolve(context().lessonId);")
s=s.replace(' const KEY=',' const textbookEnglish='+json.dumps(lookup,ensure_ascii=False,separators=(',',':'))+';\n const KEY=',1)
s=s.replace("function reload(){try{const v=JSON.parse(localStorage.getItem(KEY));if(v?.schema===SCHEMA&&Array.isArray(v.entries))book=v}catch{}}",'''function enrichEnglish(){if(!englishVisible())return;let changed=false;for(const e of book.entries){if(!e.en&&e.source!=='我的补充'){const en=textbookEnglish[e.word+'\\n'+e.meaning];if(en){e.en=en;changed=true}}for(const v of e.senses||[]){if(!v.en){const en=textbookEnglish[e.word+'\\n'+v.meaning];if(en){v.en=en;changed=true}}}}if(changed)persist()}
 function reload(){try{const v=JSON.parse(localStorage.getItem(KEY));if(v?.schema===SCHEMA&&Array.isArray(v.entries))book=v}catch{}enrichEnglish()}''')
s=s.replace('const saved=persist();return `新增','enrichEnglish();const saved=persist();return `新增');p.write_text(s)
def crop(job):
 source,r,dest=job;im=Image.open(source);x,y,w,h=r;assert min(x,y)>=0 and x+w<=im.width and y+h<=im.height,(source,r,im.size);piece=im.crop((x,y,x+w,y+h));piece.save(dest,compress_level=6);assert Image.open(dest).tobytes()==piece.tobytes()
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(crop,jobs))
Path(__file__).with_name('report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(len(report),'lessons;',sum(x['panels'] for x in report),'panels;',sum(x['englishAdded'] for x in report),'English additions')
