# 《心情手账》配套源码

在仓库根目录运行 Python 构建脚本。临时输出默认 `/tmp/huawentong-xinqing-build`，可用 `XQ_BUILD_DIR` 修改。既有漫画在课文 assets 中；可选 `XQ_SOURCE_DIR` 指向原始附件文件夹。

1. `python tools/xinqing/content.py`：课文、任务、词库、教学简报。
2. `python tools/xinqing/web.py`：网页与首页入口。
3. `python tools/xinqing/teacher.py`：可编辑教师DOCX。需 python-docx。
4. `node tools/xinqing/create.mjs`：原生可编辑PPT及29页投影图片。需 @oai/artifact-tool 与已安装的霞鹜文楷、思源宋体。
5. `python tools/xinqing/dedup-ppt.py`：合并字节相同的媒体，不改变幻灯片内容。
6. `node tools/xinqing/finalize.mjs`：使用演示文稿技能验证器，生成最终PPT与校验记录。将通过验证的PPT复制到本课 `downloads/mood-journal-lesson.pptx`。
7. 逐页渲染并目视检查PPT/DOCX；修正后再执行下一步。
8. `python tools/xinqing/package.py`：投影网页、说明、完整独立HTML、整套ZIP及部署分片。

DOM回归：`tests/xinqing.test.cjs` 与 `tests/xinqing-resources.test.cjs`；用 `LINKEDOM_PATH` 指定 linkedom 模块。设 `LESSON_OFFLINE_PATH` 可对独立HTML执行同一学习交互回归。

构建时间固定为本次版本；实际修订时更新版本号。网页、课件、教师资料与下载包必须同步更新。不要把DOM模拟称为真实iPad测试。
