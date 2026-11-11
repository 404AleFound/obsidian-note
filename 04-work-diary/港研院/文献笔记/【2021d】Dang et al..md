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

**重采样方法**

重采样是通过过采样或欠采样直接重构数据集，从而影响数据的分布，改变模型的性能。但是对于 CCTV 图片来说，其帧与帧之间的图片相似度较高，采用过采样增加异常样本可能导致模型过拟合，而采用降采样减少正常样本可能导致多数类的分布发生重大变化，因此本论文没有采用重采样方法。

**代价敏感学习**

代价敏感学习是指提高对将错误案例判对的代价，从而使得模型重视少数的错误类，其主要通过修正损失函数来影响模型：

普通的损失函数可以粗略表示为：

$$
L = \sum_{i}l(y_i, \hat{y}_i)
$$

代价敏感学习则对不同类别的损失加上权重：

$$
L = \sum_i\omega_i{(y_i, \hat{y}_i)}
$$
少数类的权重通常更大，因此少数类被判错的时候，对模型参数更新的影响更大。

**集成学习**

论文中主要介绍了两种集成学习方法：Bagging 和 Boosting。

Bagging 的基本做法是：
- 从原始训练集随机采抽样；
- 每次抽样时允许重复；
- 生成多个子训练集；
- 分别训练多个模型；
- 最后综合它们的预测；

这种方法主要增加模型之间的差异，降低单一模型预测的不稳定性。

Boosting 是逐步训练模型：
- 先训练一个模型；
- 找出它们分类错误的样本；
- 后续模型更加关注这些错误；
- 多个模型依次叠加；
- 得到最终的分类器；

# 写作学习

*Sewer images that contain defect region(s) are minor compared to non-defect images during the data collection process, which was previously described.* 

>[!note]
>与之前描述的数据收集过程中的非缺陷图像相比，包含缺陷区域的下水道图像较小。因此，以前的下水道缺陷检测框架通常会受到 IDP（Imbalanced data problem） 的影响（在数据收集过程中，包含缺陷区域的下水道图像与非缺陷图像相比较小，如前所述。


