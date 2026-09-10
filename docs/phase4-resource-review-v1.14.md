# 第四阶段资源检查 V1.14

基线：4162f39ca88ef402a3eeefc02d54ff01e6bfe2c6。本文件所在提交记录本轮删除及本地资源检查。

## 本轮决定

Yun实际反馈：《培养好习惯》正常；中二《习惯》《交友之道》显示“暂时连不上课堂”，无法进入。截图证明课堂连接失败，不能据此确定后台根因。按最新明确指令，删除两套旧练习，不再排查旧课堂后台。本轮没有生成两篇替代练习；以后重做采用内嵌篇章、题库的单页HTML，不以课堂连接作为进入条件。

中二“活动本阅读理解”保留原分组位置，items为空，显示Coming soon。以下六个路径删除，旧练习网址停止维护；其他资源的旧址跳转保持。原篇章与题目可从基线Git历史找回。

- `du/workbook/2hcl/jiaoyouzhidao/reading-data.js`
- `du/workbook/2hcl/jiaoyouzhidao/reading-teacher.html`
- `du/workbook/2hcl/jiaoyouzhidao/reading.html`
- `du/workbook/2hcl/xiguan/reading-data.js`
- `du/workbook/2hcl/xiguan/reading-teacher.html`
- `du/workbook/2hcl/xiguan/reading.html`

## 已修复本地保存

`du/textbook/2hcl/unit5/2hcl-unit5-zuwu.html` 只使用window.storage，普通浏览器没有该接口时，保存失败被空catch吞掉。代码执行已复现失败。本轮在原平台接口可用时保持原行为，不可用时使用localStorage；保存、读取、清空均处理，保留zuwu-worksheet-v1键；保存失败不再显示已保存。题目、API、年级文字或网络成绩去向未改。

8项存储回归通过：普通浏览器保存、读取、重新载入、清空，原平台失败回退，原平台可用保留原行为，存储禁用结果，以及失败不虚报成功。这是代码执行测试，不是浏览器或iPad验收。

## 外部资源的16个本地候选

外部已部署源码尚未取得；当前连接只列出huawentong-home仓库，正式网页的浏览器访问此前被环境策略明确阻止，本轮没有绕过。因此只完成本地代码与依赖检查，未证明内外版本相同，未切换现有外链。

|资源／登记年级|本地路径|外部网址|实际依赖与成绩方式|结论／下一步|
|---|---|---|---|---|
|巩固课文 · 如果走散了／中二|du/textbook/2hcl/unit5/2hcl-unit5-zousan.html|https://2hcl-unit5-zousan.netlify.app/|CONFIG.API已配置；启动JSONP名单，失败转手动；15秒超时；fetch提交＋JSONP备用；真实读写及跨域未验|核对外部版本与同一后台，确认名单和成绩后再切换|
|核心课文 · 雨树／中二|du/textbook/2hcl/unit5/2hcl-unit5-yushu.html|https://2hcl-yushu.netlify.app/|CONFIG.API已配置；启动JSONP名单，失败转手动；15秒超时；fetch提交＋JSONP备用；真实读写及跨域未验|核对外部版本与同一后台，确认名单和成绩后再切换|
|生活空间 · 组屋，新加坡美丽的风景线／中二|du/textbook/2hcl/unit5/2hcl-unit5-zuwu.html|https://2hcl-zuwu.netlify.app/|单页内嵌题库，无课堂API；原window.storage专属依赖已补浏览器存储回退；本设备结果／复制成绩；没有网络成绩提交；页首为中一高级华文，首页登记中二单元五；姓名示例1E3|本轮修复本地保存；年级冲突未擅改；暂不替换外链|
|开放题／中一、中二|du/yuedujineng/kaifangti.html|https://kaifangti.netlify.app/|调用现有hwt-ai-proxy，需有效密钥；含教师/管理功能；本地记录或AI处理；无新成绩设置|先验学生与教师边界及AI请求；保留外链和本地文件|
|进阶课文 · 别上假信息的当／中二|du/textbook/2hcl/unit6/jiaxinxi/core-student.html|https://kewenxuexi.netlify.app/jiaxinxi/core-student|/api/live与/api/answer；与所删除两课不同，不共用本课题库；同域课堂答案接口|保留现有外部入口；本地版不列为独立单页候选|
|人物描写的作用／中一、中二|du/yuedujineng/renwumiaoxie.html|https://renwumiaoxie.netlify.app/|内嵌10题；无课堂/成绩API；音效依赖Web Audio；仅页内结果，无网络提交；题库结构计数 {"questions":10}|优先验收选择手法、点原文、书面作答、反馈及下一题；版本未对照，不切外链|
|iPad 手写听写／中一、中二|du/ciyu/tingxie/ipad/index.html|https://tingxieciyu.netlify.app/|jsDelivr加载Tesseract.js，识别模型需联网；语音/手写需iPad实测；浏览器本地记录|先测OCR模型、手写识别及语音；不能称完全离线单页|
|单元三／中一|du/ciyu/ciyu-lianxi/index.html|https://voca-revise.netlify.app/1hcl-unit3/|CONFIG.API为空；无后台时loadRoster转手动身份；浏览器本地保存；未配置Google成绩上传，不可当作已回流；题库结构计数 {"DECODE":6,"CTX":9,"COL":9,"SJ":3}|保留外链，先确认是否接受本地自练版；不自动切换成绩行为|
|单元四／中一|du/ciyu/ciyu-lianxi/s1danyuan4/index.html|https://voca-revise.netlify.app/1hcl-unit4/|CONFIG.API为空；无后台时loadRoster转手动身份；浏览器本地保存；未配置Google成绩上传，不可当作已回流；题库结构计数 {"DECODE":6,"CTX":9,"COL":9,"SJ":3}|保留外链，先确认是否接受本地自练版；不自动切换成绩行为|
|单元五、六／中一|du/ciyu/ciyu-lianxi/s1danyuan56/index.html|https://voca-revise.netlify.app/1hcl-unit5-6/|CONFIG.API为空；无后台时loadRoster转手动身份；浏览器本地保存；未配置Google成绩上传，不可当作已回流；题库结构计数 {"DECODE":6,"CTX":9,"COL":9,"SJ":3}|保留外链，先确认是否接受本地自练版；不自动切换成绩行为|
|单元四／中二|du/ciyu/ciyu-lianxi/s2danyuan4/index.html|https://voca-revise.netlify.app/2hcl-unit4/|CONFIG.API为空；无后台时loadRoster转手动身份；浏览器本地保存；未配置Google成绩上传，不可当作已回流；题库结构计数 {"DECODE":6,"CTX":9,"COL":9,"SJ":3}|保留外链，先确认是否接受本地自练版；不自动切换成绩行为|
|单元五／中二|du/ciyu/ciyu-lianxi/s2danyuan5/index.html|https://voca-revise.netlify.app/2hcl-unit5/|CONFIG.API为空；无后台时loadRoster转手动身份；浏览器本地保存；未配置Google成绩上传，不可当作已回流；题库结构计数 {"DECODE":6,"CTX":9,"COL":9,"SJ":3}|保留外链，先确认是否接受本地自练版；不自动切换成绩行为|
|单元六 A · 重点词语／中二|du/ciyu/ciyu-lianxi/s2danyuan6a/index.html|https://voca-revise.netlify.app/2hcl-unit6-1/|CONFIG.API为空；无后台时loadRoster转手动身份；浏览器本地保存；未配置Google成绩上传，不可当作已回流；题库结构计数 {"DECODE":6,"CTX":9,"COL":9,"SJ":3}|保留外链，先确认是否接受本地自练版；不自动切换成绩行为|
|单元六 B · 词语练习／中二|du/ciyu/ciyu-lianxi/s2danyuan6b/index.html|https://voca-revise.netlify.app/2hcl-unit6-2/|CONFIG.API为空；无后台时loadRoster转手动身份；浏览器本地保存；未配置Google成绩上传，不可当作已回流；题库结构计数 {"DECODE":6,"CTX":9,"COL":9,"SJ":3}|保留外链，先确认是否接受本地自练版；不自动切换成绩行为|
|修辞的作用／中一、中二|du/yuedujineng/xiuci.html|https://xiuci.netlify.app/|题库内嵌、无fetch/课堂API；Google字体及浏览器语音；仅页内积分，无网络成绩提交；题库结构计数 {"1":{"比喻":9,"拟人":6,"夸张":5,"反问":3,"设问":1,"排比":1},"2":{"比喻":7,"拟人":4,"夸张":2,"反问":2,"排比":3}}|优先验收两个年级的选择、关键词、反馈和结果；不以题量统计替代教学审查|
|作文指导／中一、中二|xie/shared/zuowenzhidao.html|https://zuowenzhidao.netlify.app/|调用现有hwt-ai-proxy，需有效密钥；含教师/管理功能；本地记录或AI处理；无新成绩设置|先验学生与教师边界及AI请求；保留外链和本地文件|

题库计数只表示代码条目，修辞题可能跨类别重复，不作为独立题数或教学质量验收。7份词语各有24条客观题，答案索引均在选项范围内，另有3条造句任务；不代表答案教学上全对。

## 验证范围

- 用户实际验证：《培养好习惯》正常；两篇活动本无法进入课堂。没有把用户简短反馈扩大为逐个按钮测试记录。
- 本地执行：组屋原保存失败已复现；8项存储回归通过；16候选的16段内联脚本语法通过；7份词语共168条客观题答案索引检查通过。
- 删除检查：6个文件删除，首页只撤下两项；现62项活动，30本地、32外部；其他分组与入口内容不变。共享课文脚本、73图片、教师生成器、登录及API配置保持。
- 未验证：修改后正式网页、真实语音／OCR、iPad、课堂API和Google成绩写入。部署状态另见本提交Workers Builds与V1.14进度记录。

## 接入顺序

1. 优先验收人物描写和修辞两个不依赖课堂API的本地页，对照外部题目和按钮；通过后切换首页。
2. 7份词语的本地API为空，不能默认切换后仍收成绩；须明确本地自练模式或接入既有成绩去向。
3. 组屋本地页写中一，登记为中二单元五；不凭文件名改年级，待对照课本或用户确认。
4. 雨树、如果走散了分别验Google名单及成绩；手写听写验OCR；AI工具验服务及学生／教师边界；假信息课堂版留待专项。

## 新单页资源最低要求

打开就能开始学习，不等待教师开课或班级名单；篇章、题目、必要样式和程序放入HTML。断网时核心作答能运行；联网语音、OCR或AI另注明。成绩上传可选，失败不能挡住作答；本地保存与网络提交分开提示，不把已保存说成已上传。
