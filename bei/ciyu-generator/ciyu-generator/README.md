# 华文通词语学习单生成器

上传位置：

```text
huawentong-home/bei/ciyu-generator/index.html
```

使用：打开教师备课页面，填写年级、单元、课文／主题和词语清单，输入 DeepSeek API Key，点击“生成学习单”。生成后先检查学生版和教师版，再下载文件。

学生版上传到：

```text
huawentong-home/du/ciyu/ciyu-lianxi/<年级>/<单元>/<练习名称>/index.html
```

教师版 `teacher.html` 可放在同一文件夹，但不要加入学生总站导航。

本页面使用现有 Worker：

```text
https://hwt-ai-proxy.lyqlym2015.workers.dev/
```

API Key 只在浏览器本次请求中使用，不要写入 GitHub 文件。生成页面目前不会自动写入 GitHub，需要教师检查后手动上传。
