# 《恐怖事件》配套维护

数据以 build_content.py 为主，输出 lesson.json、content.js、lexicon.js 和教学设计摘要。
漫画为用户提供的五张原文件，段落映射采用 CSS 与 PPT 裁切窗口，未重绘或修改原图。

生成顺序：build_content.py → build_pages.py → build_guide.py → build_deck.mjs。
Python 文档生成需要 python-docx；课件生成需要 @oai/artifact-tool 与已安装的霞鹜文楷、思源宋体。
课件在仓库同级 ppt-build 目录生成 candidate.pptx。deduplicate_pptx.py 从同级工作目录运行，只去除重复图片。
交付前须使用 Presentations 技能的 finalizePresentation 对候选稿验证并发布到 downloads/horror-lesson.pptx，逐页检查渲染；DOCX 须按 documents 技能渲染核对。
最后运行 build_package.py 更新独立离线页面、ZIP 与分片下载。

测试：LINKEDOM_PATH 指向 linkedom 安装目录，运行 node tests/kongbushijian.test.cjs。可另设 LESSON_OFFLINE_PATH 以同一测试核验生成的单文件版。
这是 DOM 模拟；不等同于实体 iPad、浏览器布局或原生 PowerPoint 实测。
