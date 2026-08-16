# 01　把 xiezuo 上传到网站

预计 10 分钟。全程在浏览器里点，不必用命令行。

---

## 做之前先确认一件事

你的华文通主站是用 **GitHub 仓库 `huawentong-home`** 管理的：
你把文件传到 GitHub，Cloudflare 会自动重新部署。

如果你不确定，先做这个检查：

1. 浏览器开 `https://github.com/lf9675`
2. 看有没有一个叫 **huawentong-home** 的仓库
3. **有** → 照下面做。**没有** → 先告诉我仓库叫什么名字，我改写步骤给你。

---

## 步骤一：进入仓库

1. 浏览器开 `https://github.com/lf9675`
2. 点仓库名 **huawentong-home**
3. 你会看到一堆文件的列表（`index.html`、各个文件夹等）

**预期看到**：页面中间是文件列表，右上角有一个绿色的 **Code** 按钮。

---

## 步骤二：先开一个分支（安全网）

不要直接改 main。开分支的话，出问题一键就能退回。

1. 在文件列表**左上角**，有一个写着 **main** 的按钮，点它
2. 会跳出一个输入框，写着「Find or create a branch…」
3. 输入：`feat/xiezuo`
4. 下面会出现一行 **Create branch: feat/xiezuo from 'main'**，点它

**预期看到**：左上角那颗按钮从 **main** 变成 **feat/xiezuo**。
往后每一步都要确认它显示的是 `feat/xiezuo`，不是 `main`。

---

## 步骤三：上传 xiezuo 文件夹

1. 确认左上角是 **feat/xiezuo**
2. 文件列表右上角，点 **Add file**（在绿色 Code 按钮左边）
3. 选 **Upload files**
4. 打开你电脑上的文件总管，找到解压出来的 **xiezuo** 文件夹
5. **整个文件夹直接拖进网页中间那块虚线方框**

**预期看到**：方框下方开始列出一长串文件名，像
`xiezuo/index.html`、`xiezuo/config.js`、`xiezuo/duibuqi-pengyou/index.html`……
一共 **15 个文件**。

⚠️ 如果只看到几个文件、没有 `xiezuo/` 这个前缀，表示你拖的是文件夹**里面**的东西。
点旁边的叉删掉重来，要拖**文件夹本身**。

6. 往下滚，在 **Commit changes** 那一块，第一格输入：`加入作文审题区`
7. 下面选 **Commit directly to the feat/xiezuo branch**（应该已经默认选好）
8. 点绿色 **Commit changes**

**预期看到**：回到文件列表，多出一个 **xiezuo** 文件夹。

---

## 步骤四：合并到正式网站

1. 页面上方会出现一条黄色横条：「feat/xiezuo had recent pushes」，右边有绿色按钮 **Compare & pull request**，点它
   - 没看到这条？点上方选单的 **Pull requests** → 绿色 **New pull request** → base 选 `main`、compare 选 `feat/xiezuo`
2. 点绿色 **Create pull request**
3. 页面往下滚，点绿色 **Merge pull request**
4. 再点 **Confirm merge**

**预期看到**：一行紫色的字 **Pull request successfully merged and closed**。

---

## 步骤五：等部署，然后开来看

Cloudflare 通常 1–3 分钟内自动重新部署。

浏览器开：`你的网址/xiezuo/`

**预期看到**：米色底、「作文审题互动单」大标题，下面「中一」三张卡、「中二」三张卡，
每张卡有朱红色的「第一页　开始」按钮。

点其中一张卡的「第一页」，应该正常进入，要你填姓名和班级。

---

## 万一出事

### 网站整个打不开了
1. 回到 GitHub 那个刚才合并的 Pull Request 页面
2. 滚到最下面，有一颗 **Revert** 按钮，点它
3. 建立并合并这个还原的 PR
4. 约 2 分钟后网站回到上传前的样子，历史记录完整保留

### `/xiezuo/` 打得开，但卡片是空的、写着「设置文件没读到」
表示 `config.js` 没传上去，或不在 `xiezuo` 文件夹的最外层。
回 GitHub 进 `xiezuo` 文件夹看看，`config.js` 应该和 `index.html` 并排，
不是在某个作文文件夹里面。

### 点进作文页，第二页跳不过去
先确认第一页和第二页真的在**同一个文件夹**里，而且档名正好是
`index.html` 和 `page2.html`（全小写，没有多余的字）。

---

## 做完这一步，现在是什么状态

- 六篇作文全部能用，学生能做、能出审题卡、能打印
- 教师总控台的口令能用（在你自己电脑上开）
- **还不会**自动上传给你 → 那是第 02 份文件
- **还没有** AI 按钮 → 那是第 03 份文件

也就是说，现在就已经可以上课了。后面两步是加分项，慢慢补没关系。
