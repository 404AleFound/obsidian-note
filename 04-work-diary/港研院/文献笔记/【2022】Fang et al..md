---
tags:
  - "#segmentation"
  - "#3D-construction"
  - "#mask-r-cnn"
  - "#spilt-attention"
---
**Sewer defect instance segmentation, localization, and 3D reconstruction for sewer floating capsule robots**

---

# 内容学习

>[!note] 速览
>Fang等（2022）研究如何利用低成本的漂浮胶囊机器人，实现下水道缺陷的精细检测、设备定位与三维重建。为此，作者构建了一个综合视觉框架：以改进的 Mask R-CNN 进行裂缝、断裂和变形的实例分割，将 ResNeSt 的分裂注意力骨干网络、Balanced L1 损失和面向实例分割的复制粘贴式数据增强结合起来；同时使用 ORB 特征、视觉里程计、结构光束法平差（SfM）和多视图立体方法完成定位及三维模型重建。


![[Pasted image 20261003102113.png]]

![[Pasted image 20261003102317.png]]
>[!note]
>在算法层面该论文主要对骨干网络进行了修改，将传统的 Mask-R-CNN 的骨干网络替换为包含 spilt attention 的 resNet 架构。


# 写作学习

![[Pasted image 20261003102530.png]]

>[!note] 
>这个图片可以学习绘制，同时这个框架图就是论文最后一章可以写的系统级别的方案架构。

