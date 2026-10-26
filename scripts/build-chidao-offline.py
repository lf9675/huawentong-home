"""Rebuild the standalone student file from the canonical lesson and shared engine.
Run: python3 scripts/build-chidao-offline.py (no third-party dependencies).
"""
from pathlib import Path
import base64, json, re, hashlib
ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / 'du/textbook/1hcl/unit2/chidao'
SHARED = ROOT / 'du/textbook/shared/lesson-visual-v1'
ADAPTER = ROOT / 'scripts/chidao-offline'

def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('Shared engine changed; review offline adapter: ' + old[:80])
    return text.replace(old, new, 1)

def build():
    data = (COURSE/'data.js').read_text()
    css = (SHARED/'style.css').read_text()
    app = (SHARED/'app.js').read_text()
    app = replace_once(app, "const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(state))}catch(e){const n=$('#saveWarning');if(n)n.textContent='Storage full. Please export the record.（请导出记录）';}}", "const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(state))}catch(e){showStorageWarning();}}")
    app = app.replace("behavior:'instant'", "behavior:'auto'")
    app = app.replace('window.EMBEDDED_IMAGES?.[r.sheet]||`assets/comic${r.sheet}.webp`', 'window.EMBEDDED_IMAGES[r.sheet]')
    app = app.replace("loading=\"lazy\"", "loading=\"eager\"")
    # Inline navigation retains the existing comic renderer and paragraph mapping.
    app = app.replace('aspect-ratio:${r.w}/${r.h}', 'aspect-ratio:${r.w}/${r.h};--frame-ratio:${r.h/r.w*100}%')
    app = app.replace('href="comics.html#p${p}"', 'href="#comic-p${p}"')
    app = app.replace('href="reading.html#read-p${i+1}"', 'href="#read-p${i+1}"')
    start = app.index('function download(filename,content,type)')
    end = app.index('function exportCSV()', start)
    app = app[:start] + (ADAPTER/'record-tools.js').read_text() + '\n' + app[end:]
    app = replace_once(app, 'renderComics();\n})();', (ADAPTER/'navigation.js').read_text() + '\nrenderComics();\n})();')
    images = {str(i): 'data:image/webp;base64,' + base64.b64encode((COURSE/f'assets/comic{i}.webp').read_bytes()).decode() for i in range(1,6)}
    html = (COURSE/'reading.html').read_text()
    html = re.sub(r'<link rel="stylesheet"[^>]+>', '<style>'+css+'\n'+(ADAPTER/'offline.css').read_text()+'</style>', html)
    html = re.sub(r'<header>.*?</header>', '<header><div class="masthead"><b class="logo">华文通 · 迟到</b><small>Offline（离线版）· 2课时</small><nav class="site-nav"><a href="#read">Read（自读）</a><a href="#practice">Practice（练习）</a><a href="#comics">Comics（漫画）</a><a href="#record">Record（记录）</a></nav></div></header>', html)
    html = html.replace('<div id="lessonApp"></div>', '<p id="storageNotice" class="notice" hidden>Storage unavailable（无法自动保存）. Keep this page open and export JSON before leaving. 请先导出备份。</p><noscript><p class="notice">此预览器不能运行练习。请在允许 JavaScript 的浏览器或 HTML 阅读器中打开此文件；iPad“快速查看”不等于 Safari。</p></noscript><div id="lessonApp"></div><section id="comicView" hidden><h1>40格漫画</h1><div id="allComics"></div></section><section id="fileTools" class="section" hidden><h2>Backup（备份与恢复）</h2><p>Export JSON to keep all attempts and drafts. 用 JSON 备份全部作答；CSV供老师查看。</p><button id="importRecord">Import JSON（恢复记录）</button><input type="file" id="recordFile" accept=".json,application/json" hidden><p id="importStatus" role="status"></p><div id="exportFallback" hidden><p>若未出现下载文件，可用 Share 保存到“文件”，或复制下方内容另存。</p><button id="shareExport" hidden>Share（保存/分享）</button><a id="openExport" class="btn" target="_blank" rel="noopener">Open（打开导出文件）</a><label for="exportText">Record text（导出内容）</label><textarea id="exportText" readonly rows="8"></textarea></div></section>')
    def script(s): return '<script>'+s.replace('</script', '<\\/script')+'</script>'
    html = re.sub(r'<script src="data.js"></script><script src="[^"]+"></script>', lambda _:script('window.EMBEDDED_IMAGES='+json.dumps(images,separators=(',',':'))+';')+script(data)+script(app), html)
    html = html.replace('<title>迟到 · 自读与练习 · 华文通</title>', '<title>迟到 · 学生离线版 · 华文通</title>')
    if re.search(r'(?:src|href)="(?!#|data:|blob:|\$\{src\})[^"]+"', html):
        raise ValueError('External file reference remains: '+str(re.findall(r'(?:src|href)="(?!#|data:|blob:|\$\{src\})[^"]+"',html)))
    if re.search(r'@import|url\(', css): raise ValueError('Review CSS resource dependency')
    out = COURSE/'迟到-学生单文件版.html'
    out.write_text(html)
    print(out.relative_to(ROOT), out.stat().st_size, hashlib.sha256(out.read_bytes()).hexdigest())
if __name__ == '__main__': build()
