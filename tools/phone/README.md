# 《手机被丢弃之后》教学配套维护

教材正式题名用“之后”，旧目录“以后”作为同课别名；ID s2u3l3 不变。两课时，每课按50分钟。

content.py 保存原文、题目证据、评分建议、段落图格及52词释义；web.py 生成网页并更新单元入口；teacher.py 生成教师DOCX；create.mjs 生成原生可编辑36页PPT与在线投影图；package.py 生成离线学习单及完整ZIP。原有四张漫画字节不变。

设置 HWT_BUILD_WORKSPACE 为临时构建目录。Python脚本从仓库文件读取已有图像；如构建目录有原上传附件，会重新复制同一原件。PPT需当前Codex主要运行时的 @oai/artifact-tool，并可访问 presentations/container_tools。按 content、web、teacher、create 顺序构建。dedup-ppt.py 在构建目录运行，随后 finalize.mjs 执行原生图表、表格、字体、完整性及再导入验证。通过后将 output/phone-lesson.pptx 原样复制到课文 downloads，再运行 package.py。

不要手改下载分片。重新打包会同时写入字节数、SHA256及清单。最终资料页面是 du/textbook/2hcl/unit3/shou-ji-bei-diu-qi-zhi-hou/teacher.html。

验证：tests/phone.test.cjs 和 tests/phone-resources.test.cjs，依赖 linkedom（可用 LINKEDOM_PATH 指向其包目录）。LESSON_OFFLINE_PATH 可指定打包后的独立HTML。它们是DOM行为模拟，不声称实体iPad或原生PowerPoint实测。
