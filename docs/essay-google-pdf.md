# 作文图片、PDF 与 Google 服务

学生端：`/xie/zuowen-pigai/`；教师发码与管理：`/xie/zuowen-pigai/teacher`。

## 上传

可在登录前选择并预览文件；开始识别仍须通过原访问码认证。支持 JPG、PNG、WebP 与 PDF 混合追加，每篇最多 6 页，PDF 按展开后的实际页数计算。图片每张不超过 25 MiB，PDF 每份不超过 50 MiB。超页数、损坏或加密的 PDF 明确报错，不会只取前几页；本次选择失败时原有页面不变。

PDF.js 6.4.299 legacy 版本及字体、CMap、WASM 解码器均在本站提供。PDF 在设备上逐页转为最长边 2400 像素的 JPEG，只有点击识别后才提交这些页面。扫描 PDF 无需文本层。可转正、排序、删除页面；圈注和导出的报告使用同一张转换后的图片。

## Supabase 配置

项目的 Edge Functions → Secrets：

| 名称 | 内容 |
| --- | --- |
| `GOOGLE_CLOUD_VISION_API_KEY` | 已启用 Cloud Vision API 并配置计费的 Google Cloud API key |
| `GEMINI_API_KEY` | 可调用 Gemini API 的 Google AI Studio key |
| `GEMINI_MODEL` | 选填，默认 `gemini-3.8-flash` |

密钥只保存在服务器，不写入仓库或浏览器。Vision key 可限制为 Cloud Vision API；不要设置仅允许浏览器来源的限制，因为请求由服务器发出。

存在 Google key 时，相应步骤优先使用 Google；未配置时保留现有智谱／DeepSeek。Google 调用失败时不会偷偷改用另一家服务。公开健康检查只报告配置和数据库连接，不代表已完成付费 AI 实测。

Vision 的 symbol 字框用于字级圈注，缺少真实字框时降为区域提示或待定位。人工修改识别文字会使该页旧坐标失效，但批注保留。Gemini 沿用现有 17 套评分规则与逐段复核。没有声称发现全部错误，教师仍需核对原文与 AI 建议。

## 验证

运行 `node --test tests/essay.test.mjs tests/essay-documents.test.mjs tests/essay-google.test.mjs`。

2026-10-19：使用用户上传的 19 张照片私下制作 6 份扫描 PDF，验证全部页的实际解析、渲染、旋转、加密与损坏文件错误，以及超页数失败时资源清理。学生原图、PDF 与识别文字均不提交仓库。

当日部署时 Google 两个 key 尚未配置，因此 Google 实际手写识别准确率与批改质量尚待实测。配置后，应使用新的有效测试访问码，对照人工逐字稿检查错别字是否保留，并核对字符框的位置和遗漏问题。
