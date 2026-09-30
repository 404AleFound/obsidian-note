---
name: paper-to-notes
description: 将论文 PDF 转换为结构化 Obsidian 笔记，支持本地 00-reference-lib/papers 的 PDF 或经 Zotero MCP 选取的文献；优先复用 llm-for-zotero 插件已有的 MinerU 转写，缺失时才用 MinerU MCP 解析。笔记生成到 01-assay-note。适用于论文速览或数据流梳理，不用于普通 PDF 摘要。
---

# Paper to Notes

将论文 PDF 转换为结构化 Obsidian 笔记。主代理负责编排和文件管理；论文内容只交给独立的 `note-writer` Agent 阅读和撰写。

## 核心边界

主代理必须遵守以下约束：

- 不读取完整 PDF、MinerU 临时 Markdown、原始图片或论文全文。
- PDF 初筛只读取开头少量内容，优先前 1 页或约 2000 个字符。
- 初筛通过后只能使用 MinerU 解析；已有 MinerU 转写（如 llm-for-zotero 缓存）时直接复用，缺失时才调用 MinerU MCP，不使用其他 PDF 解析器、MinerU CLI 或替代转换方式。
- 不把论文全文或大段原文复制到主代理上下文或 Agent 任务提示中。
- 不自行撰写论文笔记；写作必须委派给 `.claude/agents/note-writer.md`。
- 每篇论文使用独立的写作任务；不同论文不得交给同一个 Agent 任务处理。
- 同一论文、同一阶段只能有一个活动写作任务。
- 不让多个 Agent 同时写入同一论文目录。

## 文件与目录约束

所有路径均相对于仓库根目录；文件操作前先解析绝对路径并核对目录边界。

| 用途 | 固定路径 |
|---|---|
| PDF 输入 | `00-reference-lib/papers/<reName>.pdf` |
| MinerU Markdown 资源 | `00-reference-lib/papers/md/` |
| 已有 MinerU 转写（只读源） | `<Zotero 数据目录>/llm-for-zotero-mineru/<id>/full.md` |
| 最终笔记 | `01-assay-note/<noteTitle>/` |

最终笔记目录包含 `assets/`、`snapshot.md` 和 `dataFlow.md`。笔记只能写入 `01-assay-note/<noteTitle>/`，转写结果只能写入 `00-reference-lib/papers/md/`，原始 PDF 只能位于 `00-reference-lib/papers/`；llm-for-zotero 转写目录只读，不得修改或删除。

`noteTitle` 由论文标题生成：标题超过 5 个单词时压缩为不丢失语义的最短短语，再转为小驼峰并首字母大写。

PDF 重命名格式为 `[YYYY-MM]Original_Paper_Title.pdf`：日期取论文发表年月，空格替换为 `_`，非法字符替换为安全字符；未知日期或标题使用 `Unknown`。每个文件最多重命名一次；目标已存在时保留原文件并报告冲突，不使用 `-Force` 覆盖。

保护与写入规则：

- 不删除、覆盖或擅自移动原始 PDF、已生成 Markdown、最终笔记或 `assets/` 图片；重命名只能针对成功解析的 PDF，且不得覆盖目标。
- `note-writer` 只能写入当前任务唯一的 `output_path`；目标已存在且未获授权修改时，报告冲突并停止。
- 不同论文不得共用输出目录，同一论文的不同阶段不得并发写入。
- 不修改本 Skill 的规则、模板、脚本或环境记录，除非用户明确要求。
- 不需要解析时不创建 `00-reference-lib/papers/md/`；只清理本次明确创建且经过绝对路径核对的独立临时非 Markdown 目录。

## 论文来源与已有转写复用

论文可通过两种方式提供：

- 本地 PDF：位于 `00-reference-lib/papers/`，走「初筛 → MinerU 解析」流程。
- Zotero 文献：主代理通过 Zotero MCP 选取论文，取得条目 key、元数据和 PDF 附件路径。

llm-for-zotero 插件把 MinerU 转写缓存在 `<Zotero 数据目录>/llm-for-zotero-mineru/<id>/`，每个 `<id>` 目录含 `full.md`（写作源）、`images/` 和 `_llm_source.json`（含 `attachmentKey`、`parentItemKey`）。

复用规则：

1. 优先检查是否已有转写：在 `llm-for-zotero-mineru/` 下按 `_llm_source.json` 的 `parentItemKey`（或 `attachmentKey`）匹配论文的 Zotero key，也可按 DOI/标题 grep `content_list.json` 或 `manifest.json`。
2. 已有转写时直接复用该 `full.md` 作为写作源，跳过 MinerU 解析，不复制、不移动、不覆盖已有 Markdown。
3. 没有转写时才按「MinerU 解析与元数据」环节解析；Zotero 来源的 PDF 需先复制到 `00-reference-lib/papers/`（不移动、不覆盖原附件）。
4. Zotero 数据目录可从 `zotero_get_attachment_path` 返回的本地路径推导。
5. 转写中的图片位于同目录 `images/`；note-writer 引用这些图片时使用绝对路径（遵守 `rules-writing.md` 的「图片引用」规则），`moveMarkdownImages.py` 据此把图片复制进笔记 `assets/`，不得照抄源 Markdown 里的相对路径。

## 可用阶段

让用户选择论文和写作阶段；用户已经明确指定时，不重复询问。

| 阶段 | 模板 | 输出 | 状态 |
|---|---|---|---|
| 速览 | `templates/template-01-snapshot.md` | `snapshot.md` | 可用 |
| 流式 | `templates/template-02-dataflow.md` | `dataFlow.md` | 可用 |
| 分析 | `templates/template-03-analysis.md` | `analysis.md` | 跳过 |
| 审查 | `templates/template-04-review.md` | `review.md` | 跳过 |

“分析”和“审查”当前被补丁禁用。用户选择被禁用阶段时，明确报告“跳过”，不创建 Agent、不创建或补写对应文件，也不把跳过报告为完成。继续执行用户选择的其他可用阶段。

## 工作流

### 1. 扫描 Python 环境

在所有流程开始前，先执行本环节。

1. 读取并验证 `.py-environments-cache` 中已有的解释器记录。
2. 若记录无效，按项目/父目录中的 Conda/uv、`.venv`/`venv`、系统 Python 的顺序查找。
3. 确认前不得使用默认 Python；候选路径需通过路径、版本和 `sys.executable` 验证。
4. 确认后始终使用绝对路径运行 `scripts/check_pdf_env.py`，并更新记录。缺少依赖仅报告，不安装。

### 2. 选择论文来源与初筛

1. 确认论文来源：
   - 本地 PDF：扫描 `00-reference-lib/papers/` 中的 `.pdf` 文件；没有 PDF 且未使用 Zotero 来源时，报告并结束。
   - Zotero：主代理通过 Zotero MCP 列出或选取论文，取得条目 key、元数据和 PDF 附件路径。
2. 本地 PDF 检查文件名是否符合 `[YYYY-MM]Title_With_Underscores.pdf`，不符合时记录状态，不默认为正确；对每个 PDF 只读取开头少量内容（优先前 1 页或约 2000 字符），判断是否为论文。
3. 记录来源、路径/条目 key、文件名状态、初筛判断和无法读取的原因；非论文或初筛失败的文件不得进入后续解析。
4. 在本次任务中保存来源与初筛状态，后续不得重复初筛同一文件。

### 3. 复用已有转写

1. 对每篇待写论文，先按「论文来源与已有转写复用」检查 llm-for-zotero 缓存中是否已有 `full.md`。
2. 已有则复用其 `full.md` 作为写作源，跳过 MinerU 解析，不复制、不移动、不覆盖已有 Markdown。
3. 没有转写时，进入「MinerU 解析与元数据」环节。

### 4. MinerU 解析与元数据

1. 仅对初筛通过且没有已有转写的论文调用 MinerU MCP `parse_documents`。
2. 输出到 `00-reference-lib/papers/md/` 之下，优先为每篇论文使用独立的 `<pdf-stem>/` 资源目录；记录 Markdown 路径、资源路径和解析状态。
3. 解析失败时报告原因，不创建对应写作任务。
4. 从解析结果或可靠元数据中提取原始标题、作者、发表时间、URL、日期来源和日期类型；论文没有提供的信息标记为 `Unknown`。
5. 按“路径与命名”规则重命名成功解析的 PDF，并记录结果。
6. 在本次任务中保存解析状态，不重复解析同一文件。

### 5. 调用 Note Writer

开始任何写作任务前，主代理确认 `rules-writing.md` 和阶段模板存在，并将其绝对路径传给 `note-writer`。写作规则和模板由写作 Agent 完整读取；主代理不加载论文临时 Markdown，也不需要加载写作规则正文。

每篇论文、每个可用阶段分别创建一个 `note-writer` 任务，并传递以下字段：

```yaml
source_paths:
  - <该论文的 MinerU Markdown 路径（含复用的 llm-for-zotero full.md）>
rules_paths:
  - <paper-to-notes/rules-writing.md 的绝对路径>
template_path: <当前阶段模板的绝对路径>
output_path: <仓库根目录>/01-assay-note/<noteTitle>/<stage>.md
task_scope: <速览或流式阶段的具体阅读与写作范围>
metadata:
  title: <论文原始标题或 Unknown>
  author: <作者或 Unknown>
  time: <论文提供的发表时间或 Unknown>
  url: <论文原始 URL 或 Unknown>
```

调用要求：

- 传递路径、状态、元数据和任务范围，不传递论文全文或大段原文。
- 文件写入必须遵守“文件与目录约束”。
- 等待同一论文的写作任务结束后，才能对该论文执行图片整理或其他写入操作。
- 按 `note-writer` 的固定返回格式汇总状态，不要求它回传笔记正文。

### 6. 整理图片

所有写作任务完成后，由主代理统一运行 `scripts/moveMarkdownImages.py`，并**始终把当前论文笔记目录作为 `root` 传入**（如 `01-assay-note/<noteTitle>/`），不得省略参数、不得以仓库根目录为 root——否则脚本会递归处理根目录下所有 `.md`，误复制图片、误改其它笔记或源转写的图片引用：

- 将当前论文笔记引用的本地图片复制到对应 `assets/`。
- 更新笔记中的本地图片路径。
- 跳过远程图片并报告缺失图片。
- 只处理本次论文的笔记，不触碰其它笔记目录、`00-reference-lib/` 或 llm-for-zotero 缓存。

### 7. 写回 Zotero（可选）

用户要求把笔记写回 Zotero 时：

1. 写作任务结束后，主代理读取最终笔记文件（如 `snapshot.md`）——这是整理后的正式笔记，不是论文全文或 MinerU 转写。
2. 将笔记转为 Zotero 可渲染的简单 HTML（标题、段落、列表；`zotero_manage_note` 支持 p/strong/em/ul-li/a/code）。
3. 调用 Zotero MCP `zotero_manage_note(action='create', item_key=<论文条目 key>, note_title='Snap-shot · <论文原标题>', note_text=<转换后的内容>)`，把笔记作为子笔记挂到论文条目上。
4. 标题用「`Snap-shot · ` + 论文原标题」，而不是通用的 `Snap-shot`——笔记在文库根级或列表里要靠标题辨认对应哪篇论文，通用名无法区分。多个笔记并存时尤其如此。
5. `note_title` 会以 `<h1>` 形式写入笔记正文开头，作为列表显示名；对已创建的笔记改标题时直接 update 不可靠（h1 会被剥离、正文被重排），应改为删除后按上面格式重建。
6. 目标论文已有同名笔记时先确认是否覆盖，不擅自覆盖已有笔记。

### 8. 清理与交付

1. 汇总环境、来源与初筛、已有转写复用、MinerU、重命名、写作、图片整理和写回 Zotero 状态。
2. 确认所有已启动的写作任务均已结束。
3. 按“文件与目录约束”检查受保护目录和转写结果，不删除 `00-reference-lib/papers/md/` 或最终笔记内容。
4. 若本次创建了独立的临时非 Markdown 资源目录，按绝对路径核对后清理；否则填写“未执行”。
5. 返回以下结果：
   - Python 环境与依赖检查。
   - 论文来源与初筛结果。
   - 已有转写复用结果（复用或新解析）。
   - MinerU 解析结果。
   - PDF 重命名结果。
   - 笔记路径与写作状态。
   - 图片整理结果。
   - 临时资源清理结果（若无可清理资源，填写“未执行”）。
   - 跳过阶段与遗留问题。

## 写作阶段范围

### 速览

- 使用 `templates/template-01-snapshot.md`。
- 优先阅读标题、摘要和结论；只有这些内容不足以判断核心问题或方法时，才读取引言中的必要段落。
- 目标是判断论文解决什么问题、使用什么方法、获得什么结果，以及是否值得继续阅读。

### 流式

- 使用 `templates/template-02-dataflow.md`。
- 完整浏览论文以建立全局结构，但不要求推导全部公式或解决所有实现细节。
- 梳理章节作用、整体数据流、模块接口、关键图表、训练或验证流程、方法对比、边界条件和未解决问题。

## 跨任务并发边界

- 不同论文可以使用独立的 `note-writer` 任务并行处理。
- 每个任务只能处理一篇论文的一个阶段，并拥有唯一输出文件。
- 同一论文目录内的写作和图片整理必须串行执行。
- 主代理统一汇总结果并执行清理；写作 Agent 不直接合并其他任务的结果。
