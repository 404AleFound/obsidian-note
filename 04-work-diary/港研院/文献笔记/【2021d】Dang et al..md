---
tags:
  - "#classification"
  - "#dataset"
---
**Deep learning-based sewer defect classification for highly imbalanced dataset**

---

# 内容学习

![[Pasted image 20261001174640.png]]

>[!note] 数据不平衡 + agent 自动生成报告
>这篇文章在算法层面只是做了常规的分类任务，没啥可学习的地方，但是其在自动报告生成和不平衡数据集处理方面值得深度学习。
>自动报告生成：
>- 这个可以学习一下，看看能不能利用 llm 制作一个简历级别的 agent 项目
>
>不平衡数据处理：
>- XGBoost 和 lightGBM

本篇文章重点就在将数据集类别不平衡的问题，即在管道检测数据集中，异常的数据占比较少，导致网络可能会倾向于保守地预测为“正常”，这种问题也叫 IDP（Imbalanced Data Problem），常见的解决类别不平衡的方法为：
- 重采样方法（resampling）
- 代价敏感学习（cost-sensitive learning）
- 集成学习（ensemble learning）



# 写作学习

![[Pasted image 20261001183826.png]]
>[!note]
>这图的结构挺不错的，可以学习一下，随后可以移植到自己的论文中。

*Sewer images that contain defect region(s) are minor compared to non-defect images during the data collection process, which was previously described.* 

>[!note]
>与之前描述的数据收集过程中的非缺陷图像相比，包含缺陷区域的下水道图像较小。因此，以前的下水道缺陷检测框架通常会受到 IDP（Imbalanced data problem） 的影响（在数据收集过程中，包含缺陷区域的下水道图像与非缺陷图像相比较小，如前所述。


