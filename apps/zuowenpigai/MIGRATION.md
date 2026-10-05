# 华文通照片批改迁移

Python 源码来自 `lf9675/zuowenpigai` 的 0408c2e，并包含 2026-10-05 圈注修复。原仓库修复提交为 dd7bdf5。

新学生端：`xie/zuowen-pigai/index.html`。后端：`supabase/functions/hwt-essay`。
现有 Cloudflare Workers 静态资源发布流程部署前端；Supabase Edge Function 处理访问码、OCR、评分与分段复核。

## 一次配置

在 Supabase 项目 `zuowenpigai` 的 Edge Functions → Secrets 中设置现有服务的两项密钥：

- `ZHIPU_API_KEY`：智谱 OCR。
- `DEEPSEEK_API_KEY`：DeepSeek 评分。
- `DEEPSEEK_MODEL` 可选，默认 `deepseek-flash`。

密钥不要写入仓库、网页或聊天。可从原 Streamlit 应用的 Secrets 安全复制；新服务不会自动继承 Streamlit Secrets。
`SUPABASE_URL` 和 `SUPABASE_SERVICE_ROLE_KEY` 由 Supabase 注入。无需向学生提供任何 AI 密钥。

已应用的建表脚本：`supabase/sql/hwt-essay.sql`。新表启用 RLS；学生只能经服务端访问本人记录。
Edge Function 设置 `verify_jwt=false`，因为每个私有操作在函数内验证原来的学生访问码，而非 Supabase Auth JWT。
调用次数和新增作文额度保留现有规则；失败不扣次数，全部完成后事务记账，同一任务重试不重复扣费。
新学生端目前提交的是新作文；旧版“修改后重交”及教师管理仍在原 Streamlit 应用。

## 重要范围

- 主评分完整沿用原 Python 提示词的 17 个考试段/文体组合，评分闸门移植为确定性代码。
- 独立语言复核不修改分数，成功分段保留，失败可继续。
- GLM-OCR 的区域框只能画待确认区域。只有服务商真实字框才能画精确字级框；不会按字数均分坐标。
- 未定位、重复位置不明确、疑似识别错误都保留在批注清单；不设置错误条数上限。
- 无题目时仅检查语言，不给内容分或总分。
- 原图留在当前浏览器页面。数据库保存核对文字、OCR 布局和批改结果；重新打开历史记录不会伪造原图。
- 下载的 HTML 报告含当次原图及完整批注，可用浏览器打印为 PDF。原 Python 版教师覆核和 PDF 功能保留。

## 验证

`node --test tests/essay.test.mjs`：定位、区域/字框区分、重复词、跨页、未定位保留、评分、拒绝越权、就绪状态。
`tests/essay-database.sql`：事务测试，测试记录全部回滚；验证归属、租约和幂等扣次数。
Python：`python -m unittest discover -s tests -v` 和 `python test_v610.py`，在本目录执行。

这些测试验证程序行为，不是学生作文的 AI 准确率。真实样本验收还须有可用密钥、完成 OCR/AI 请求，再与照片人工标注逐项对照。

## Python 版运行

教师功能继续由原仓库运行。此目录保留源码，未重复复制约 21 MB 的字体；单独运行此副本时，请将原仓库的 `fonts/` 放到此目录。
`.assetsignore` 排除本目录、后端和测试，避免将服务端源码作为 Cloudflare 静态资源发布。
