# 维护与更新

给后续维护者看的。改完包之后怎么重新发版，写在这。

## 一、改了包内容之后

### 1. 先自检

```bash
python <专家管理脚本目录>/validate_expert.py <专家目录>
```

必须零错误。改了 `plugin.json` 的展示字段（名称、简介、标签、提示词）后再跑一次注册，否则市场里显示的还是旧的。

### 2. 重新打包

```bash
python <专家管理脚本目录>/package_expert.py <专家目录> <输出目录>
```

产物是 `thalassemia-research-team.zip`。**注意**：压缩包内顶层目录必须是 `thalassemia-research-team/`，否则使用者解压后目录名不对，装进专家目录会失效。

### 3. 推送到仓库

```bash
python <发布脚本目录>/publish.py code <专家目录> --message "改了什么"
```

这个脚本走 GitHub API，**只上传有变化的文件**，改几个文件通常几秒完成。先加 `--dry-run` 可以只看差异不动远端。

> 如果你的网络环境能正常 `git push`，直接用 git 更省事。上面这个脚本是为「git 传输被代理拦断、只有 API 通」的环境准备的。

### 4. 发新版

```bash
python <发布脚本目录>/publish.py release <zip路径> --tag v1.0.1 --title "地贫科研团队 v1.0.1" --notes-file 说明.md
```

标签不能重复。发完会打印两个链接：Release 页面和 zip 直链，把直链给使用者即可。

## 二、改内容时的几条硬约束

| 约束 | 原因 |
|------|------|
| `plugin.json` 的 `name`、`agentName` 不能改 | 它们是唯一标识，改了专家会从市场消失 |
| `agents/*.md` 的文件名不能改 | `agentName` 就等于文件名 |
| 主理人 md 的 `name` 必须与文件名一致 | 否则加载失败 |
| `tags` 固定 3 个、`quickPrompts` 固定 3 个 | 校验脚本会报错 |
| `profession` 必须等于 `displayName`（Team 型） | 校验脚本会报错 |
| `members` 里必须有且只有一个 `role: "lead"` | 同上 |
| agent md 的 frontmatter **不要**写 `tools` | 工具权限由系统分配，写了会报错 |

## 三、加成员的正确姿势

内置成员有对应的 agent 文件，改它们要动 `plugin.json` 的 `agents`、`teamInfo.memberAgents`、`members` 三处，还要补头像。

**但使用者加成员不需要动包**——团队配置存在各自工作区的 `团队宪章/team-profile.json` 里，用 `manage_members.py` 增删改即可。包里的 9 人是「出厂默认」，不是上限。

所以：**只有当你想改出厂默认值时，才需要动包**。

## 四、不要做的事

- 不要把任何人的真实研究数据、病例、未发表结果放进包里
- 不要把服务器地址、账号、密钥写进任何 md
- 不要删 `skills/*/LICENSE`、`SOURCE.md`、`NOTICE.md`——那是第三方许可要求
- 不要改 `academic-research-skills` 上游 `references/upstream/` 下的文件，升级时会冲突
