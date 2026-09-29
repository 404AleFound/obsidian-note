# Git 常见命令行

快速开始

```bash
# 初始化仓库
git init

# 将所有内容加入暂存区
git add .

# 提交内容
git commit -m 'init commit.'

# 链接远端仓库
git remote add <REMOTE_REPO_NAME> <REMOTE_REPO_URL>

# 推送到远端，首次提交需要指定远程仓库和分支，使用 -u
git push -u <REMOTE_REPO_NAME> <REMOTE_REPO_URL>
```

提交分支

```bash
git push -u <REMOTE_REPO_NAME> <REMOTE_REPO_URL>
git push

git push --force

git push <REMOTE_REPO_NAME> <REMOTE_REPO_URL>

```

新建分支

```bash
git checkout -b <NEW_LOCAL_BRANCH_NAME>
```

拉取分支

```bash

```

删除分支

```bash
# 删除本地分支
git branch -d <LOCAL_BRANCH_NAME>

# 删除远端分支
git push origin --delete <REMOTE_BRANCH_NAME>

```

回滚提交

```bash

```

# Git 事件 - merge 冲突

一般的合并流程：

```shell
# 方式一：merge（保留分叉历史）                                               
  git fetch origin                                                              
  git merge origin/main                                                         

  # 解决冲突后                                                                  
  git add <冲突文件>
  git commit                                                                    

# 方式二：rebase（线性历史）                                                  
  git fetch origin                                                              
  git rebase origin/main                                                        

  # 每个冲突逐步解决                                                            
  git add <冲突文件>                                                            
  git rebase --continue
```

如果 rebase 搞乱了，可以随时终止：

```shell
git rebase --abort
```

出现报错：

```shell
(base) ➜  obsidian-note git:(677b46a) ✗ git pull
	error: Pulling is not possible because you have unmerged files.
	hint: Fix them up in the work tree, and then use 'git add/rm <file>'
	hint: as appropriate to mark resolution and make a commit.
	fatal: Exiting because of an unresolved conflict.
```

解释：推送失败，又一次未完成的合并，Git 拒绝执行 pull。

原因：Git 处于一个"中间状态"——之前的 merge 或 rebase 产生了冲突，你还没处理完。在这个状态下，Git 不允许你做任何新的 pull/merge 操作。

解决方案：可以手动修复本次冲突，完成合并；但是， 本地仓库当前应当严格遵循远端仓库，且发现远端仓库不知道因为什么原因已经脏了，因此选择直接回滚 commit ，回退版本。

```shell
git status
```

输出：

```shell
(base) ➜  obsidian-note git:(677b46a) ✗ git status
	interactive rebase in progress; onto 677b46a
	
	Last command done (1 command done):
		pick e09b21d # obsidian note auto commit 2026-05-25 10:53:06
		bilibilideMacBook-Pro.local
		No commands remaining.
	
	You are currently rebasing branch 'master' on '677b46a'.
		(fix conflicts and then run "git rebase --continue")
		(use "git rebase --skip" to skip this patch)
	    (use "git rebase --abort" to check out the original branch)
	    
	Unmerged paths:
		(use "git restore --staged <file>..." to unstage)
		(use "git add <file>..." to mark resolution)
		
	both modified:
		programming-languages/kotlin-note/9-kotlin-concurrency.md
		
	Changes not staged for commit:
		(use "git add <file>..." to update what will be committed)
		(use "git restore <file>..." to discard changes in working directory)
		modified:   bilibili-module/work-diary/2026-05.md
		
	Untracked files:
		(use "git add <file>..." to include in what will be committed)
		conflict-files-obsidian-git.md
		no changes added to commit (use "git add" and/or "git commit -a")
```

太混乱了，还出现了 obsidian 自动生成的冲突文件，直接回滚，回滚 commit 命令如下：

```shell
git revert <commit-hash>
# 生成一个新的反向 commit

git reset --soft HEAD~1 
# 回滚一个 commit，保留改动在工作区

git reset --mixed HEAD~1
# 回滚一个 commit，保留改动但是取消暂存

git reset --hard HEAD~1
# 回滚一个 commit，丢弃所有改动

git reset --<reset_model> HEAD~4
# 回滚 4 个 commit 提交，根据对应模式

git reset --<reset_model> <hash>
# 回滚到对应的 commit 提交，根据对应模式
```

如果想要放弃 rebase 的中间态，回到 rebase 之前的状态，如下：

```shell
git rebase --absort
```
 
本次，采用直接回滚 commit 的方式，且采用 hard 模式，直接丢弃前几个 commit。如果使用 soft 或者 mixed 模式的回滚，可能需要如下命令：

```shell
# 丢弃单个文件
git checkout -- <file>

# 丢弃所有已跟踪文件的改动
git checkout -- .

# 或者用新语法（更清晰）
git restore <file>                                                            
git restore .                                                                 

# 如果还想清除未跟踪的新文件
git clean -fd
```

最后，回滚完本地提交后，需要同步远端的提交记录，使用命令：

```shell
# 强制推送到远端
git push --force
```

> [!note]
> 对于冲突事件遇见少，对于 rebase 中间态不够熟悉，当发生冲突时，文件会被 Git 修改，插入冲突标记：
>```
><<<<<<< HEAD
>远端的内容（rebase 目标分支 677b46a 的版本）
>=======
>本地的内容（commit e09b21d 的版本）
> >>>>  e09b21d
>```
>注意，`>>>>` 符合在 .md 文件中会被特殊渲染，因此需要打开看源码比较好。
>下次可以先放弃合并，回到合并之前的状态，然后再解决冲突。

# git 的分支范式

> [!note]
> 
> 这是根据 Vincent Diressen 的博客 —— "A successful Git branching model" 内容所写的一篇笔记。

这篇博客提出一种 Git 仓库模式 —— “去中心化但集中化”。

![](distributed-git-team-workflow-diagram.png)



![](git-flow-branching-workflow-diagram.png)