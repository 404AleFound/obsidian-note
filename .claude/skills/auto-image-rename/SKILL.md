---
name: auto-image-rename
description: |
  根据图片的内容对图片文件进行重命名，同时修改 .md 文件中对应图片引用。
  Use When：用户说 "auto-image-rename"、"重新命名图片"、"根据图片内容重命名图片"、"rename images"、"批量重命名图片" 等类似的话时。
  该技能会自动检测当前模型是否支持视觉（VLM），如果不支持会使用备用策略。
metadata:
  version: 2.0
  author: Ale
---

# auto-image-rename

## OVERVIEW

1. 该技能能够根据 .md 文件中的图片内容对图片进行重新命名，并且修改 .md 文件中对应的引用。
2. 用户可以通过简单的指令触发该技能，系统会自动完成图片重命名和引用更新的过程。
3. 已经重命名过的图片会被记录，不会重复处理。
4. 如果当前模型不支持视觉分析，会自动切换到基于上下文的命名策略。
5. 一般来说，图片资源位于 .md 文件所在目录的子目录中，图片文件夹的名称一般为 "images" 或 "assets" 等，因此查找图片时，优先查找这些文件夹。

---

## IMPORTANT FILES

- **Tracking file**: `.claude/skills/auto-image-rename/.processed-images.json`
  - 记录已处理过的图片，避免重复重命名
  - 每次处理前读取，每次处理后更新

---

## STEPS

### STEP 1: DETECT VISION CAPABILITY

1. 读取一张测试图片（任意从后续要处理的 .md 文件中找到的图片）
2. 如果能获取到图片的详细内容描述，则 `vision_available = true`
3. 如果无法获取图片内容（返回空或无法描述），则 `vision_available = false`
4. 输出检测结果：
   - `VISION: ENABLED` — 将基于图片内容命名
   - `VISION: DISABLED` — 将基于 Markdown 上下文命名

---

### STEP 2: ANALYZE INPUT & FIND .MD FILES

1. 根据用户输入确定需要处理的 .md 文件路径（单个、多个或文件夹）。
2. 不要处理 `./calude/` 文件夹下的文件
3. 收集所有目标 `.md` 文件并输出列表。

**Output format:**

```
找到以下 Markdown 文件：
- path/to/file1.md
- path/to/file2.md
```

---

### STEP 3: FILTER FILES & LOAD TRACKING DATA

1. 读取跟踪文件 `.claude/skills/auto-image-rename/.processed-images.json`（如不存在则创建一个空 JSON `{}`）。
2. 检查每个 `.md` 文件是否包含图片引用。跳过无图片引用的文件。
3. 将包含图片引用的文件标记为 **待处理**。

**Output format:**

```
待处理文件（含图片引用）：
- path/to/file1.md  ✓
- path/to/file2.md  ✗ (无图片引用，跳过)
```

---

### STEP 4: EXTRACT IMAGE REFERENCES

1. 从每个待处理的 `.md` 文件中提取所有图片引用路径。
2. 记录每个图片的路径和所属 `.md` 文件。
3. 对比跟踪文件，将已处理过的图片标记为 **已命名**，其余为 **待命名**。

**Output format:**

```
图片提取结果：
| Markdown 文件 | 图片路径 | 状态 |
|--------------|----------|------|
| file1.md | images/abc.jpg | 待命名 |
| file1.md | images/def.png | 已命名 (跳过) |
```

---

### STEP 5: RENAME IMAGES

#### If `vision_available = true`:

1. 读取每张**待命名**图片的内容。
2. 根据图片内容生成一个简洁、描述性的英文文件名（使用小写字母，单词间用连字符 `-` 分隔）。
3. 重命名图片文件。
4. 记录新旧文件名映射。

#### If `vision_available = false`:

1. 读取图片所在的 `.md` 文件，提取图片周围的文本上下文（图片前后各 2-3 行）。
2. 根据上下文语义生成一个简洁的英文文件名（使用小写字母，单词间用连字符 `-` 分隔）。
3. 重命名图片文件。
4. 记录新旧文件名映射。

**Output format:**

```
重命名结果：
| 原文件名 | 新文件名 | 策略 |
|----------|----------|------|
| images/abc.jpg | images/diagram-workflow.jpg | 视觉分析 |
| images/def.png | images/chart-sales-q3.png | 上下文分析 |
```

---

### STEP 6: UPDATE .MD FILE REFERENCES

1. 依次更新每个 `.md` 文件中的图片引用路径，仅修改图片文件名部分，保持其他部分不变。
2. 记录每个文件的更新情况。

**Output format:**

```
引用更新结果：
| Markdown 文件 | 更新数量 | 状态 |
|--------------|----------|------|
| file1.md | 2/2 | 成功 |
| file2.md | 1/2 | 失败 (文件未找到) |
```

---

### STEP 7: SAVE TRACKING DATA

1. 将本次处理的所有图片（包括新命名的和跳过的）更新到 `.claude/skills/auto-image-rename/.processed-images.json`。
2. 格式示例：

```json
{
  "images/diagram-workflow.jpg": {
    "original_name": "images/abc.jpg",
    "timestamp": "2026-05-17T12:00:00Z"
  }
}
```

**Output:**

```
跟踪数据已保存。本次处理完成：
- 新命名图片：X 张
- 跳过（已命名）：Y 张
- 更新引用：Z 个文件
```

---

## DEVELPMENT HISTORY

version 2.0：
  - 新增已命名图片跳过机制，避免重复处理
  - 新增 VLM 检测，自动切换命名策略
  - 优化输出格式，使用表格替代冗长文本
  - 重构步骤结构，逻辑更清晰
  - 待开发：
    - 添加测试案例
    - 添加检测指标：处理图片数量，消耗token，消耗时间等
    - 添加正则匹配，对于常见的非内容命名情况检测，例如包含 paste 字符串、包含长数字序列等
    - 添加图片命名优化功能，添加命名名称长度控制，尽可能简短明了


version 1.0：
  - 实现 SKILL 的基本功能，支持单文件、多文件、文件夹内的图片重命名
