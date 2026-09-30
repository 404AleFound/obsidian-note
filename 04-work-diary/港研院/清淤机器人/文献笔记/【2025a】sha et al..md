---
tags:
  - defect-detection
  - lightweighting
---
**A lightweight cross-scale feature fusion model based on YOLOv8 for defect detection in sewer pipeline**

---

Although the above methods have made some progress, there are still several **limitations.** **First,** sewer pipe images often exhibit complex backgrounds and diverse defect types. Common defects such as cracks and deposits typically have blurred boundaries and are easily confused with the background, leading to the loss of critical semantic information during feature extraction.**Second,** although some models have improved detection accuracy, their complex network architectures and excessive parameter counts make them unsuitable for deployment on resource-constrained embedded devices.**Third,** existing approaches suffer from inadequate multi-scale feature fusion and limited cross-layer semantic expression, which restricts the model’s ability to accurately detect objects at different scales and with ambiguous boundaries.To address these challenges, ...