"""Build the standalone student page and verified multipart classroom download."""
from pathlib import Path
import base64, hashlib, json, re, sys, zipfile
ROOT=Path(__file__).resolve().parents[2]
LESSON=ROOT/'du/textbook/2hcl/unit2/zhu-yang-ye-sheng-dong-wu'
SHARED=ROOT/'du/textbook/shared/lesson-v1'
OUT=Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
BASE='https://huawentong-home.lyqlym2015.workers.dev/'
URL=BASE+'du/textbook/2hcl/unit2/zhu-yang-ye-sheng-dong-wu/'
def data(p,mime):return 'data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()
css=(SHARED/'style.css').read_text()
for name in ['wenkai.woff2','songti.woff2']:
    css=css.replace(name,data(SHARED/name,'font/woff2'))
assets={f'comic{i}':data(LESSON/f'assets/comic{i}.png','image/png') for i in range(1,4)}
page=(LESSON/'reading.html').read_text()
page=re.sub(r'<link rel="stylesheet"[^>]+>',lambda _: '<style>'+css+'</style>',page)
page=page.replace('../../../../../assets/huawentong-logo.png',data(ROOT/'assets/huawentong-logo.png','image/png'))
page=page.replace('href="../../../../../index.html"','href="'+BASE+'"').replace('href="index.html"','href="'+URL+'index.html"')
page=page.replace('<main>','<main><p class="muted">离线版 · 关闭前请导出学习记录。</p>')
page=page.replace('<script src="content.js', '<script>window.LESSON_ASSETS='+json.dumps(assets)+';</script><script src="content.js',1)
def inline(match):
    src=match[1].split('?')[0]
    p=(LESSON/src).resolve()
    return '<script>'+p.read_text().replace('</script','<\\/script')+'</script>'
page=re.sub(r'<script src="([^"]+)"[^>]*></script>',inline,page)
offline=OUT/'student-offline.html'
offline.write_text(page)
# The self-contained HTML is delivered through checked 10 MiB parts below.
readme='《助养野生动物》完整教学配套\n中二高级华文 · 单元二 · 生活空间 · 一课时50分钟\n\n1. 学生互动学习.html：含逐段课文、对应原漫画、8组任务、个人词语本与闪卡，可离线使用。\n2. 可编辑课件.pptx：32页，问题与答案分开，原生文字至少30pt。\n3. 教师流程与答案.docx：一课时流程、原题、参考答案、依据、易错点及操作说明。\n4. 在线投影.html：解压后打开，请保留slides文件夹。\n5. 漫画原图：3张原图，采用用户附件1、3、4。\n\n动物特点先口头概括，再取原句核对；表格可按需要补写。开放回应必做且说明为什么，教师核对。\n系统只检查取证、词语与点选，不自动评分概括与开放题。\n记录只保存在当前设备与浏览器，可导出JSON、CSV、文字；不会自动上传或发给老师。\n个人词语本可导出导入，未知词标待补释义。离线文件与在线版记录不会自动互通。\n公益广告原题保留，使用NParks官方资源或自行找真实广告。外部链接需要联网，请课前准备。\n教师资源为公开页面。课堂发学生直达链接。\n\n学生在线：'+URL+'reading.html\n教师资料：'+URL+'teacher.html\n'
(LESSON/'downloads/使用说明.txt').write_text(readme)
projector=(LESSON/'slides.html').read_text()
projector=re.sub(r'<link rel="stylesheet"[^>]+>',lambda _:'<style>'+css+'</style>',projector)
projector=projector.replace('../../../../../assets/huawentong-logo.png',data(ROOT/'assets/huawentong-logo.png','image/png')).replace('href="../../../../../index.html"','href="'+BASE+'"').replace('href="teacher.html"','href="'+URL+'teacher.html"')
zpath=OUT/'zhu-yang-package.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    z.write(offline,'学生互动学习.html')
    z.write(LESSON/'downloads/zhu-yang.pptx','可编辑课件.pptx')
    z.write(LESSON/'downloads/teacher-guide.docx','教师流程与答案.docx')
    z.writestr('使用说明.txt',readme)
    z.writestr('在线投影.html',projector)
    for p in sorted((LESSON/'slides').glob('*.png')):z.write(p,'slides/'+p.name)
    for i in range(1,4):z.write(LESSON/f'assets/comic{i}.png',f'漫画原图/漫画{i}.png')
with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
raw=zpath.read_bytes(); parts=[]; limit=10*1024**2
for i,offset in enumerate(range(0,len(raw),limit),1):
    chunk=raw[offset:offset+limit];name=f'package.part{i:02d}.bin'
    (LESSON/'downloads'/name).write_bytes(chunk)
    parts.append({'file':name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
manifest={'name':'助养野生动物_完整教学配套.zip','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'parts':parts}
(LESSON/'downloads/package-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
offline_parts=[];offline_raw=offline.read_bytes()
for i,offset in enumerate(range(0,len(offline_raw),limit),1):
    chunk=offline_raw[offset:offset+limit];name=f'offline.part{i:02d}.bin'
    (LESSON/'downloads'/name).write_bytes(chunk)
    offline_parts.append({'file':name,'bytes':len(chunk),'sha256':hashlib.sha256(chunk).hexdigest()})
(LESSON/'downloads/offline-manifest.json').write_text(json.dumps({'name':'助养野生动物_学生互动学习.html','mime':'text/html;charset=utf-8','bytes':len(offline_raw),'sha256':hashlib.sha256(offline_raw).hexdigest(),'parts':offline_parts},ensure_ascii=False,indent=2))
print(json.dumps({'offline_bytes':offline.stat().st_size,'package_bytes':len(raw),'parts':len(parts)},indent=2))
