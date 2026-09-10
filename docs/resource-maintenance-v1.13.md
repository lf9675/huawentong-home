# 华文通仓库整理 V1.13

日期：2026-09-10。基线：`7e87127243fb94b5d5382c6564718175872a0563`。本文件所在提交记录本轮清理。

Yun 已授权执行删除、合并和迁移；同时要求不改教师生成器、登录、API和成绩去向。

## 已执行

- 删除68个内容只有换行的 zhanwei；全部具有相同Git blob，且HTML/JS/CSS没有引用。原空目录可能自动消失，不代表学习资源丢失。
- 合并15个重复学习页或目录页：删除重复实现，原文件保留小型HTML跳转；查询参数和片段原样保留，无跳转链。
- 将《培养好习惯》完整迁至中一词语目录；16词及全部程序字节保持原样。旧网址保留跳转。中一两个入口改为完整课名；中二两个错误入口撤下，分组次序不变。
- 首页及旧目录改用正式维护地址；旧教师说明加历史标识，保留原文。

## 维护位置与旧网址

下表每行是一个兼容入口。更新内容时只修改右列；不要覆盖左列为第二份完整网页，也不要删除左列。

|旧仓库路径（保留跳转）|唯一维护路径|
|---|---|
|`du/jiciyu.html`|`du/ciyu/bihua/jiciyu/index.html`|
|`du/tingxieciyu.html`|`du/ciyu/tingxie/ipad/index.html`|
|`du/kaifangti.html`|`du/yuedujineng/kaifangti.html`|
|`du/kewenfenxi.html`|`du/textbook/2hcl/unit4/kongbushijian/index.html`|
|`du/renwumiaoxie.html`|`du/yuedujineng/renwumiaoxie.html`|
|`du/xiuci.html`|`du/yuedujineng/xiuci.html`|
|`xie/1hcl/zuowen/fanwen/S1-fanwen/s1-jixuwen1.html`|`xiezuo/fanwen/s1-jixuwen.html`|
|`xie/2hcl/zuowen/jixuwen/fanwen/S2-fanwen/s2-jixuwen1.html`|`xiezuo/fanwen/s2-jixuwen.html`|
|`xie/2hcl/zuowen/jixuwen/fanwen/S2-fanwen/s2-jixuwen2.html`|`xiezuo/fanwen/s2-qingjing-jixuwen.html`|
|`xie/dianyou.html`|`xie/2hcl/dianyou/dingcan.html`|
|`xie/shared/narraessay.html`|`xie/narraessay.html`|
|`xie/zuowenzhidao.html`|`xie/shared/zuowenzhidao.html`|
|`xie/1hcl/zuowen/index.html`|`xiezuo/index.html`|
|`xie/2hcl/zuowen/index.html`|`xiezuo/index.html`|
|`xie/2hcl/zuowen/jixuwen/fanwen/S2-fanwen/index.html`|`xiezuo/fanwen/index.html`|
|`du/kewenxuexi.html`|`du/ciyu/1hcl/unit4/peiyang-hao-xiguan/index.html`|

## 为什么 xiezuo 仍保留

`xiezuo/` 是首页实际使用的作文正式目录，不是废弃文件夹。三份 page2.html 只有这里具备；当前 config.js 的成绩后台与 xie/1hcl、xie/2hcl 副本不同，当前 hook.js 逐题上传正误，旧副本只上传错题。直接把八份旧作文跳到这里会改变旧入口的成绩去向和字段，所以八份旧作文及两套共四个 config.js/hook.js 本轮保留原字节。下一次处理这些版本，须先完成成绩专项核对，再确定统一后台方案。

保留的八份旧作文是：

- `xie/1hcl/zuowen/shenti/chenmo-zeren/index.html`
- `xie/1hcl/zuowen/shenti/zhiding-jihua/index.html`
- `xie/1hcl/zuowen/shenti/jianchi-kanfa/index.html`
- `xie/2hcl/zuowen/jixuwen/shenti/duibuqi-pengyou/index.html`
- `xie/2hcl/zuowen/jixuwen/shenti/neixiang-gongxian/index.html`
- `xie/2hcl/zuowen/jixuwen/shenti/shequ-wenqing/index.html`
- `xie/1hcl/zuowen/xiezuo-jineng/kaitou-jiewei/s1-jineng/index.html`
- `xie/2hcl/zuowen/jixuwen/xiezuo-jineng/kaitou-jiewei/s2-jineng/index.html`

外部资源及其本地版本、教师页面、共享题库、73张图片、独立口语页和 legacy-tools.html 均保留。du/exam 沿用现有路径。不补写未知的Cloudflare部署配置。

## 本轮验证与限制

- 已执行代码验证：16个跳转各3种参数/片段情形共48例；三个作文目录共24个生成链接目标一致；64条有效首页映射（32本地、32外部）检查；中一词语2入口、中二0入口；已识别非API本地引用无缺失；73个动态图片地址存在；19段变更页内联脚本语法通过。
- 90个未修改文本文件与基线逐字节相同，包括生成器、登录、API配置、成绩hook、八份旧作文和三份第二页。新词语页与旧页逐字节一致。
- 这些是代码执行和路径检查，不是正式浏览器按钮验收。前轮浏览器访问正式站点已被环境策略明确阻止，本轮没有绕过；语音、iPad、真实AI、成绩写入、正式跳转与缓存待用户端复验。
- 提交与Cloudflare构建结果以GitHub该提交的检查记录及V1.13进度表为准；构建成功不等同于正式页面交互验收。

## 新资源规则

1. 同一资源一个维护位置，先确定年级、单元、篇章、学生/教师和成绩方式。
2. 新的课文词语闯关：`du/ciyu/1hcl/unit4/peiyang-hao-xiguan/index.html` 是已建立的示例；以后用 `du/ciyu/<年级>/<单元>/<篇章>/index.html`，替换真实词语、例句和答案，保留本课。
3. 作文审题和技能继续用 `xiezuo/<topic>/index.html`；范文用 `xiezuo/fanwen/`。不要把新版本上传到 xie 的旧副本。
4. 其他目录沿用 du/textbook、du/workbook、du/exam、xie/<年级>/dianyou；共享代码和图片无需接入导航。
5. 根 index.html 的 DATA 控制首页，上传不会自动加卡片。保留现有方框卡片和数字分组次序；未完成分组用 items:[]，不创建 zhanwei。
6. GitHub：main → 目标目录 → Add file → Upload files → choose your files → Commit changes。没有目录时用 Create new file 填完整 README.md 路径并写真实说明，再上传网页。
7. 等 Workers Builds 成功，打开正式域名加路径，Ctrl+F5；检查标题、选项反馈、下一步、第二页、图片/语音。测试成绩须安排测试班级，不能把构建成功当作成绩已存。

## 删除文件逐项清单

原内容可从基线提交的Git历史恢复；以下不是学生HTML，不为它们伪造学习页。

- `bei/ciyu-generator/zhanwei`
- `bei/textbook-generator/zhanwei`
- `bei/zuowen-generator/zhanwei`
- `du/ciyu/bihua/zhanwei`
- `du/ciyu/chengyu-lianxi/chengyu1-23/zhanwei`
- `du/ciyu/chengyu-lianxi/chengyu107-122/zhanwei`
- `du/ciyu/chengyu-lianxi/chengyu123-138/zhanwei`
- `du/ciyu/chengyu-lianxi/chengyu24-46/zhanwei`
- `du/ciyu/chengyu-lianxi/chengyu47-70/zhanwei`
- `du/ciyu/chengyu-lianxi/chengyu71-87/zhanwei`
- `du/ciyu/chengyu-lianxi/chengyu88-106/zhanwei`
- `du/ciyu/chengyu-lianxi/zhanwei`
- `du/ciyu/chengyu-manhua/zhanwei`
- `du/ciyu/chengyu-youxi/zhanwei`
- `du/ciyu/ciyi/zhanwei`
- `du/ciyu/ciyu-lianxi/zhanwei`
- `du/ciyu/quizlet/zhanwei`
- `du/ciyu/tingxie/zhanwei`
- `du/ciyu/zhanwei`
- `du/exam/1hcl/jixuwen/zhanwei`
- `du/exam/1hcl/shuomingwen/zhanwei`
- `du/exam/1hcl/zhanwei`
- `du/exam/2hcl/jixuwen/zhanwei`
- `du/exam/2hcl/shuomingwen/zhanwei`
- `du/exam/2hcl/yilunwen/zhanwei`
- `du/exam/2hcl/zhanwei`
- `du/exam/zhanwei`
- `du/textbook/1hcl/unit1/zhanwei`
- `du/textbook/1hcl/unit2/zhanwei`
- `du/textbook/1hcl/unit3/zhanwei`
- `du/textbook/1hcl/unit4/zhanwei`
- `du/textbook/1hcl/unit5/zhanwei`
- `du/textbook/1hcl/unit6/zhanwei`
- `du/textbook/1hcl/zhanwei`
- `du/textbook/2hcl/unit1/zhanwei`
- `du/textbook/2hcl/unit2/zhanwei`
- `du/textbook/2hcl/unit3/zhanwei`
- `du/textbook/2hcl/unit4/zhanwei`
- `du/textbook/2hcl/unit5/zhanwei`
- `du/textbook/2hcl/unit6/jiaxinxi/slides/l3/zhanwei`
- `du/textbook/2hcl/unit6/zhanwei`
- `du/textbook/2hcl/zhanwei`
- `du/textbook/zhanwei`
- `du/workbook/1hcl/zhanwei`
- `du/workbook/2hcl/zhanwei`
- `du/workbook/zhanwei`
- `du/yuedujineng/zhanwei`
- `xie/1hcl/dianyou/zhanwei`
- `xie/1hcl/zhanwei`
- `xie/1hcl/zuowen/fanwen/zhanwei`
- `xie/1hcl/zuowen/shenti/chenmo-zeren/zhanwei`
- `xie/1hcl/zuowen/shenti/jianchi-kanfa/zhanwei`
- `xie/1hcl/zuowen/shenti/zhiding-jihua/zhanwei`
- `xie/1hcl/zuowen/xiezuo-jineng/kaitou-jiewei/zhanwei`
- `xie/1hcl/zuowen/xiezuo-jineng/zhanwei`
- `xie/1hcl/zuowen/zuowen-pigai/zhanwei`
- `xie/2hcl/dianyou/zhanwei`
- `xie/2hcl/zhanwei`
- `xie/2hcl/zuowen/jixuwen/fanwen/zhanwei`
- `xie/2hcl/zuowen/jixuwen/shenti/duibuqi-pengyou/zhanwei`
- `xie/2hcl/zuowen/jixuwen/shenti/neixiang-gongxian/zhanwei`
- `xie/2hcl/zuowen/jixuwen/shenti/shequ-wenqing/zhanwei`
- `xie/2hcl/zuowen/jixuwen/xiezuo-jineng/kaitou-jiewei/zhanwei`
- `xie/2hcl/zuowen/jixuwen/xiezuo-jineng/zhanwei`
- `xie/2hcl/zuowen/yilunwen/zhanwei`
- `xie/2hcl/zuowen/zuowen-pigai/zhanwei`
- `xie/3hcl/zhanwei`
- `xie/4hcl/zhanwei`
