# 华文通·改（CLever）— 新加坡中学华文作文 AI 批改平台

新加坡中学华文/高级华文作文 AI 批改系统 — **基于 SEAB 官方评分标准 + 30 年 HCL 教学方法论**。

> 本仓库为**内测正式版**（2026 年 8 月免费内测使用）。
> 旧版（Claude API 架构）已存档于 `huawentong` 仓库，不再维护。

## 技术栈

| 环节 | 服务 | 说明 |
|------|------|------|
| 作文评分 | **DeepSeek**（OpenAI 兼容 SDK） | `base_url="https://api.deepseek.com"`，streaming 输出，`max_tokens=32000` |
| 手写 OCR | **智谱 GLM-OCR**（bigmodel.cn） | 手写体专项，base64 直传，标准库 `urllib` 调用，无额外 SDK |
| 前端/托管 | Streamlit + Streamlit Community Cloud | 私有仓库部署 |
| 数据库 | Supabase Postgres（psycopg2） | `SUPABASE_DB_URL` 使用现有连接串；本次无需改表 |

## 核心功能

1. **评分哲学**：语言宽松（学生程度弱，弱句病句不苛求）、内容严格（审题、逻辑、PEEL 结构不让步）
2. **段落式批改**：AI 按"语义+结构"识别段落，每段独立呈现原文 + 问题诊断 + 修改示范
3. **教育而非指令**：每个示范改写前先讲"为什么要这样改"
4. **分层示范**：按学生当前水平给出不同层级的改写目标
5. **学生流程**：拍照上传 → OCR 识别 → 学生核对修正 → 提交批改 → 逐段反馈

## 文件结构

```
zuowenpigai/
├── app.py            ← 主入口，顶部导航
├── prompts.py        ← 评分标准 + 方法论 prompt（核心 IP）
├── database.py       ← Supabase Postgres 数据层
├── requirements.txt
└── pages/
    ├── student.py    ← 学生端：OCR + 批改 UI
    ├── admin.py      ← 老师后台
    └── progress.py   ← 成长档案
```

## 部署

1. 安装依赖：`pip install -r requirements.txt`
2. 在 Streamlit Cloud 的 Secrets 中设置：

```toml
DEEPSEEK_API_KEY = "sk-..."   # 必填，评分（platform.deepseek.com）
ZHIPU_API_KEY   = "..."       # 必填，OCR（bigmodel.cn）
ADMIN_PASSWORD  = "..."      # 原图教师修正必须显式配置教师密码
SUPABASE_DB_URL = "..."      # 现有 Supabase Postgres pooler 连接串
# LANGUAGE_AUDIT_MODEL = "deepseek-v4-flash"  # 可选：独立语言复核使用的模型
```

⚠️ 不再需要 `ANTHROPIC_API_KEY` 和 `HF_TOKEN`，如 Secrets 中仍存在请删除。

3. 运行：`streamlit run app.py`

## 评分标准（唯一权威来源）

等级区间、题型分类、PEEL 顺序等硬事实以 `0_核心事实_勿改.md` 为准（依据 SEAB 官方 PDF）：

A1 ≥ 45　A2 42–44　B3 39–41　B4 36–38　C5 33–35　C6 30–32　D7 27–29（满分 60）

## 隐私与合规（PDPA）

- 仅收集作文文本与照片，不收集学生姓名、学校等个人身份信息
- 学生上传前提示"作文中勿写真实姓名和学校"
- 数据处理方：DeepSeek、智谱 AI（服务器位于中国大陆）
- 内测阶段仅限 B2C 自愿参与，不与学校建立数据关系


## 原图批注修复（2026-10）

- 图片先转正，OCR、网页与 PDF 使用同一张图片。核对文字按页编辑，修改后只失效该页旧坐标。
- 批注先确定原文位置，再找图片坐标。重复字必须由段落和相邻文字消歧，禁止默认圈第一处。
- 只有供应商返回真实字框或教师确认的位置才画精确记号。现有 GLM-OCR 主要返回区域框；区域框不再按字数均分，改为黄色待确认范围。此版本未新增可保证手写字级坐标的 OCR 服务。
- 已发现的批注全部进入清单，定位失败不会消失。跨页问题按页展示；PDF 附完整清单。
- 主评分后增加独立分段语言复核，成功分段缓存，失败状态明确，可重试。复核完成只代表调用完成，不代表找出了所有错误；补充结果不自动改分。
- 教师在原图页输入已配置的教师密码，可框选、补批、修改批语和取消误判。保存到当前提交的 `feedback_json.annotation_overrides`。

照片仍只在当次会话中用于显示和导出；本次未增加照片持久化。历史记录只有文字和批改 JSON 时，无法重建原图。

验收范围与复现实测说明见 [docs/annotation-validation.md](docs/annotation-validation.md)。
