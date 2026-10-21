from pathlib import Path
import re,json,base64,zipfile,hashlib,shutil
R=Path('/workspace/scratch/6e755f6b886c');repo=R/'huawentong-home';O=repo/'du/textbook/2hcl/unit6/xinjiapo-yu-shijie';S=repo/'du/textbook/shared/lesson-v1';URL='https://huawentong-home.lyqlym2015.workers.dev/du/textbook/2hcl/unit6/xinjiapo-yu-shijie/'
b64=lambda p:base64.b64encode(p.read_bytes()).decode()
assets={f'comic{i}':'data:image/png;base64,'+b64(O/'assets'/f'comic{i}.png') for i in range(1,5)}
s=(O/'reading.html').read_text();s=s.replace(' · 互动学习 · 华文通',' · 离线互动学习 · 华文通')
css=(S/'style.css').read_text()+'\n'+(O/'lesson.css').read_text();css=css.replace('url(wenkai.woff2)','url(data:font/woff2;base64,'+b64(S/'wenkai.woff2')+')');css=re.sub(r'@font-face\{font-family:LessonSong;[^}]+\}','',css);css=css.replace('LessonSong,serif','LessonSong,SimSun,"Songti SC",serif')
s=re.sub(r'<link rel="stylesheet"[^>]+>','',s);s=s.replace('</head>','<style>'+css+'</style></head>')
s=re.sub(r'<script src="([^"]+)"></script>',lambda m:'<script>'+(O/m[1].split('?')[0]).resolve().read_text().replace('</script','<\\/script')+'</script>',s)
s=s.replace('<script>window.LESSON =','<script>window.LESSON_ASSETS='+json.dumps(assets)+';</script><script>window.LESSON =',1)
s=s.replace('../../../../../assets/huawentong-logo.png','data:image/png;base64,'+b64(repo/'assets/huawentong-logo.png')).replace('../../../../../index.html#2/texts',URL+'index.html').replace('href="index.html"','href="'+URL+'index.html" target="_blank"')
intro=(O/'index.html').read_text();intro=re.search(r'<section id="intro">(.*?)</section>',intro,re.S)[1].replace('href="reading.html#paragraph-1"','href="#paragraph-1"')
extra='<section class="home notes" style="max-width:1120px;margin:20px auto;padding:0 20px"><details><summary>鸡饭导入（点开后口头讨论）</summary>'+intro+'</details><details id="offlineComics"><summary>完整漫画回读</summary><div id="offlineComicPages" class="comic-pages"></div></details><p class="muted">离线文件：记录保存在当前浏览器；与网站记录各自保存。换设备前请导出学习记录与词语本。</p></section>'
s=s.replace('<nav class="nav">',extra+'<nav class="nav">',1)
s=s.replace('</body>','<script>document.getElementById("offlineComics").addEventListener("toggle",function(){const host=document.getElementById("offlineComicPages");if(this.open&&!host.children.length)for(let i=1;i<=4;i++){const img=document.createElement("img");img.src=window.LESSON_ASSETS["comic"+i];img.alt="原漫画第"+i+"页";host.append(img)}});</script></body>')
(O/'downloads/offline-learning.html').write_text(s)
readme='''《新加坡与世界的联系》完整教学配套
中二高级华文｜单元六｜生活空间｜1课时
版本：2026-10-21

开始：用浏览器打开 offline-learning.html，含鸡饭导入、逐段原文与漫画、课本题、个人词语本与闪卡。
教师：teacher-guide.docx 为7页可编辑教案及答案；singapore-world.pptx 为28页可编辑课件。
漫画：comics 文件夹保留教师提供的四张原图，文件内容未改动。

课堂按50分钟设计，教师教案也提供40分钟安排。
学习记录与词语本分别导出备份；离线文件与网站记录各自保存，不会自动跨设备同步。
投影片使用霞鹜文楷及思源宋体系列字体。设备缺少字体时可能出现替代；在线投影可保持固定版面。
来源与参考见教师教案和教师专区；量表为课堂建议，不是课本官方分值。

学生入口：'''+URL+'index.html\n教师入口：'+URL+'teacher.html\n'
(O/'README.txt').write_text(readme)
archive=R/'build/singapore-world-teaching-package.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name in ['singapore-world.pptx','teacher-guide.docx','offline-learning.html']:z.write(O/'downloads'/name,name)
 z.write(O/'README.txt','README.txt')
 for i in range(1,5):z.write(O/'assets'/f'comic{i}.png',f'comics/comic{i}.png')
blob=archive.read_bytes();parts=[]
for i,start in enumerate(range(0,len(blob),8*1024*1024),1):
 b=blob[start:start+8*1024*1024];name=f'package-part-{i:02}.bin';(O/'downloads'/name).write_bytes(b);parts.append(dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
manifest=dict(filename=archive.name,bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),parts=parts)
(O/'downloads/package-manifest.json').write_text(json.dumps(manifest,indent=2))
# Repository audit: preserve source, release rationale and reproducible authoring scripts.
(O/'authoring').mkdir(exist_ok=True)
for name in ['build_lesson.py','build_web.py','create_slides.mjs','create_guide.py','package_lesson.py','dedupe_pptx.py']:shutil.copy2(R/'build'/name,O/'authoring'/name)
print(json.dumps({'offlineBytes':(O/'downloads/offline-learning.html').stat().st_size,'pptxBytes':(O/'downloads/singapore-world.pptx').stat().st_size,'zipBytes':len(blob),'parts':len(parts)},ensure_ascii=False))
assert (O/'downloads/offline-learning.html').stat().st_size<25*1024*1024
assert (O/'downloads/singapore-world.pptx').stat().st_size<25*1024*1024
assert b''.join((O/'downloads'/x['file']).read_bytes() for x in parts)==blob
assert zipfile.ZipFile(archive).testzip() is None
