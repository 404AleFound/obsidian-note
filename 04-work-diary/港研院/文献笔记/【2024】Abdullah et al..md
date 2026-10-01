---
tags:
  - segmentation
  - attention
  - "#transformer"
---
**CaveSeg: Deep Semantic Segmentation and Scene Parsing for Autonomous Underwater Cave Exploration**

---
>[!note]
>这篇文章主要干了三件事情：建立水下洞穴语义分割数据集，设计轻量化语义分割模型，进行水下探险相关任务的实验。

![[Screenshot 2026-09-30 at 22.09.54.png]]

上图为划分的数据集，可以模仿。在这部分需要说明：
- 数据集来源
- 标签类型
- 打标方式
- 类别分布
- （可加）泛化挑战

>[!note]
>迁移过来，对于淤泥识别的数据集构建也可以构建泛化挑战：有/无流数据集、成像条件恶化数据集。同时也要说明数据集类别的分布。

从算法角度看，本论文的特征提取骨干网络采用基于纯注意力机制的 swin transformer，同时进行了特征融合与金字塔池化（PPM）用于特征融合。