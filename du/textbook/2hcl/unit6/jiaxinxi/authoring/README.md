维护说明

lesson.json 为教学内容与稳定题目编号的唯一数据源。修改后须同步 content.js、教师版和 PPT。build_content.py 是本轮原始生成记录，依赖教师上传图和旧文本；日常修订直接修改 lesson.json，不重新运行它覆盖内容。
共享引擎位于 du/textbook/shared/lesson-v1；本课只在 lesson-ui.js 增强顺序、结构表和排序。原漫画逐字节保留，不重画。
本轮生成脚本保留原工作区路径，迁移后需修改根路径与所用运行环境。PPT 使用 @oai/artifact-tool；DOCX 使用 python-docx。
