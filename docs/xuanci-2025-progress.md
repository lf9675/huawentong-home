# 选词填空（2025）：发布与成绩交接

- 学生页：`du/ciyu/ciyu-lianxi/s2-xuanci-2025/index.html`
- 首页：中二 → 词语和成语 → 词语练习试一试 → 选词填空（2025）。
- 本课保留原卷16—30题；第25题接受“潜移默化”“逐渐”。
- 原匿名保存键 `huawentong:vocab:2hcl:2025:exercise-1:v1` 保留。署名后按姓名、班级、学号隔离本机记录；认领未署名作答需明确确认。

## 成绩状态：尚未启用

指定原表：`1I6gXsqkfyRjXIwrAoJW8GlthFbB6cTGOOJ9Pzjc32lA`（词语练习-成绩）。Google Drive连接已成功读取此原表，但2026-09-15原表写入被拒绝，错误为 `ACCESS_TOKEN_SCOPE_INSUFFICIENT`。未向原表写入测试数据，未修改旧表、旧脚本或旧词语练习。

旧网页 `https://voca-revise.netlify.app/2hcl-unit4/` 中发现旧接口：
`https://script.google.com/macros/s/AKfycbx-W_YUOXLrnrPXP93r9ko-x6gGGFwYjEMX3UUneajpR842PC7Fm92p8r1mkE9UFbNv/exec`
其 `a=roster` 读取可用，但尚未核验它与指定原表的精确对应，也未验证提交去重。不得据此声称成绩已连接。不要用该接口绕过连接授权失败。

## 已准备的提交实现

`progress-sync.js` 保存可重试的固定提交ID；首次答案与订正、错题重做分开；每个身份独立保存；离线不丢答案；只有包含相同提交ID、版本、学习单ID和原表ID的明确保存回执才显示“已提交老师”。当前 `submission-config.json` 的 `enabled=false`，因此不会向任何成绩服务发送学生数据。

完整配套接收器位于 `bei/management/vocab-xuanci-2025-receiver.gs`。此代码尚未部署；它固定只写指定原表中的“选词填空2025-进度”“选词填空2025-逐题”，保留原有分页。逐题答案由服务器重新核对；首次答案保留；重复提交去重；较旧版本不会覆盖新进度；GET不返回学生资料。

## 继续时的顺序

1. 用户重新授权 Google Drive 的表格写入权限后，读取原表当前元数据和精确目标范围。先验证已有旧接口的去向和去重行为，能可靠复用才沿用。
2. 若旧接口无法满足进度记录及可靠去重，使用提供的独立接收器，不覆盖旧 Apps Script。当前连接没有 Apps Script 创建/部署动作；若仍没有能力，需要用户在 Google Apps Script 完成授权与Web应用部署。此步骤不能只用表格写权限替代。
3. 接收器部署为“以自己身份执行”，仅提供本课写入和无学生数据的健康检查。执行 `setupVocabProgress` 建立两个新分页。核对部署URL的GET返回协议、学习单ID和指定原表ID。
4. 将经验证的URL写入 `submission-config.json`，保持 `enabled=false`，先用明确标为验收的模拟学生测试真实写入、重复提交、较旧版本、改错后的首次答案保留和错题重做。按精准测试ID清理测试行。
5. 真实验收通过后才设 `enabled=true`，提交GitHub，检查Cloudflare构建以及线上提交状态。

未执行的步骤不能标为已完成。网页可正常练习不等于成绩已经回流。
