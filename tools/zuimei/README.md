# 《最美的姿势》配套生成

输出目录：`du/textbook/2hcl/unit4/zui-mei-de-zi-shi/`。课文标识 `s2u4l3`，复用 `shared/lesson-v1` 引擎和跨课文个人词语本。

内容底稿为 `content.py`，依据教师提供的两张课本截图、三张教参截图和四张原漫画核对。原漫画通过 `ZM_UPLOAD_DIR` 指定目录读入，文件名为 `最美的姿势-1.png` 至 `最美的姿势-4.png`，保持字节不变。缺少原图时应从当前发布目录恢复，不能生成替代原图。

生成顺序（从仓库根目录运行）：

1. 设置 `ZM_BUILD_DIR` 为仓库外构建目录；`ZM_REPO_DIR` 为仓库根目录。
2. 用 Python 运行 `content.py`、`web.py`、`teacher.py`。
3. 用装有 `@oai/artifact-tool` 的 Node 运行 `create.mjs`，生成候选 PPT、39 页投影图片与备注。
4. 运行 `finalize.mjs`，完成 PPT 结构、几何、字体及重导入验证。需配置 `CODEX_PRIMARY_RUNTIME_PYTHON`，并提供 Presentations 技能工具目录。
5. 使用 Documents 技能的 `render_docx.py` 渲染教师讲义，逐页检查。
6. 运行 `package.py`，同步离线 HTML、PPT 下载、ZIP、校验清单及在线投影。大文件自动分片，每片不超过 3 MiB。

`tests/zuimei.test.cjs` 使用 linkedom 运行实际学习单脚本；通过 `LINKEDOM_PATH` 指定依赖，通过 `LESSON_OFFLINE_PATH` 可检测独立离线 HTML。`tests/zuimei-resources.test.cjs` 检查在线投影路由与三个真实下载处理器。

修订后同步网页、投影、PPT、DOCX、离线 HTML 与整套 ZIP。原文与题目改动先核对附件证据。勿改动其他课文或共用引擎来迁就本课内容。
