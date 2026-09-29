# 电邮工作室（2026-09-29）

## 入口
- 中一：`index.html?grade=1`
- 中二：`index.html?grade=2`
- 教师：`teacher.html`
- 直接分享：`index.html?grade=2#energy/4/editor`

## 教学内容
中一4组：中学生活、与同学相处、维系友情、谈论学习环境。
中二7组：无节制花钱、网上订餐、遇到难题、节约能源、假信息、垃圾分类、社会课题。
每组：地图、讯息与身份、逐问认题型、逐问要点、小编辑（3例）、写成段、开头结束语、范文追踪、换题迁移。

学习单中的错例为教学新编，不声称是本班真实作品。题目来自用户提供的文件；来源与疑点在data.js及每题资料说明中保留。原题元数据和题目中的历史调查不视作当前已核实事实。

课程是“教师示范→师生判断→独立写作→针对性讲评”的支架。自由作答不通过关键词自动评分。学生可查看其他合理写法；不用固定六段／五行或排名计时。原题需三个要点的部分保留三项规划。

## 保存与教师工具
学生答案存本浏览器localStorage（按题分开）；可下载TXT。没有后台提交，不宣称老师已收到。
教师可预览本地照片、复制AI整理指令、导入带lessonId的错例JSON、逐条编辑确认、导出匿名互动HTML或JSON。照片不上传、不导出。当前无OCR、无AI接口、无云端成绩汇总。

教师修改候选内容后，确认勾选自动清除，需重新核对。导入校验题目、字段、类别、问题编号；学生导出不包含原图位置或照片。

## 来源处理
- 中学生活：原题200字以上，仅用于该题。
- 与同学相处／维系友情：日期与正文时间存在疑点，保留并注明，不用于学生评分。
- 遇到难题：接受不同合理立场；建议依两详一略。
- 垃圾分类：结束语不等同祝词。本地回收按NEA核对；用旧箱子可减少新增容器负担，不强制按每种材料买桶。
- 社会课题：保留题目中的历史调查作为题设，不当作现状；移除插入来信的教学批注及重复短语。
- 网上订餐：保留原题，重做支架；可能风险不写成朋友已发生的事实。

NEA依据（2026-09-29核对）：
https://www.nea.gov.sg/our-services/waste-management/3r-programmes-and-resources/national-recycling-programme
https://www.nea.gov.sg/our-services/waste-management/3r-programmes-and-resources/waste-minimisation-and-recycling/at-home
https://www.nea.gov.sg/our-services/waste-management/beverage-container-return-scheme/for-consumers

## 技术
纯HTML/CSS/JS，无构建步骤、无外部字体依赖。数据与UI分开，可从文件夹离线打开index.html。生产路径在华文通xie/shared/email-course，首页中一/中二实用文均已接入；旧网上订餐文件保留，首页指向新版。
