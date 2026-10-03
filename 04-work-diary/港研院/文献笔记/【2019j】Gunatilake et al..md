---
tags:
---
**Real-Time 3D Profiling with RGB-D Mapping in Pipelines Using  Stereo Camera Vision and Structured IR Laser Ring**

---

# 内容学习

>[!note]
>该论文研究如何在管道机器人行进过程中，实时、准确地重建管道内壁的三维形貌，并识别结构缺陷。作者提出一种结合双目红外相机、360°结构化红外激光环和RGB相机的系统：利用激光环获取管壁轮廓，通过双目视觉计算深度，再将点云与RGB图像融合，借助轮式里程计和ROS实时生成带颜色信息的RGB-D管道地图及椭圆度偏差热图。

![[Pasted image 20261003110633.png]]


# 写作学习

*A. 3D profiling technologies  Several technologies such as LIDAR, Time-of-flight (TOF) cameras, structured 3D cameras, and structured laser ring profiling were evaluated to identify their performance in generating an accurate 3D map of a pipeline. Among those technologies, LIDAR was less preferred for the proposed application due to low resolution in range measurements (less than 1cm accuracy), and the need of slow operation for increased resolution requirements, which is not ideal for continuous pipe scanning. Although most of the existing 3D cameras are inherent with TOF camera technology, it is less effective due to low grid resolution of the projected pattern. Further, when the surface is reflective the sensing of the projected pattern becomes non trivial and it can result in a considerable noise. Structured light 3D cameras such as Intel Reaslsense and Microsoft Kinect motion sensor project low resolution IR patterns and therefore they are not sensitive to smaller structural variations of the sensed surface. Since this application demands millimeter (mm) level of accuracy to detect defects on the surface, structured laser ring projection technique with the use of stereo camera vision stands as a strong choice. This enables to capture accurate structural information from the laser pattern while traversing the robot inside the pipelines. Further research work was conducted in this project to enhance the accuracy and obtain the natural colour patterns of the surface by using a stereo IR camera, a RGB camera and IR laser pattern. Using an IR laser improves the performance of extracting the colour parameters from RGB camera by filtering out the IR light.*

>[!note]
> A. 3D 分析技术对激光雷达、飞行时间 (TOF) 相机、结构化 3D 相机和结构化激光环分析等多种技术进行了评估，以确定它们在生成准确的管道 3D 地图方面的性能。在这些技术中，LIDAR 不太适合所提出的应用，因为距离测量分辨率低（精度小于 1 厘米），并且需要缓慢运行才能提高分辨率要求，这对于连续管道扫描来说并不理想。尽管大多数现有的 3D 相机都采用了 TOF 相机技术，但由于投影图案的网格分辨率较低，其效果较差。此外，当表面具有反射性时，投影图案的感测变得非常重要，并且可能导致相当大的噪声。结构光 3D 相机（例如 Intel Reaslsense 和 Microsoft Kinect 运动传感器）投射低分辨率红外图案，因此它们对感测表面的较小结构变化不敏感。由于该应用需要毫米 (mm) 级的精度来检测表面缺陷，因此使用立体相机视觉的结构化激光环形投影技术是一个不错的选择。这使得机器人在管道内移动时能够从激光图案中捕获准确的结构信息。该项目进行了进一步的研究工作，通过使用立体红外相机、RGB 相机和红外激光图案来提高精度并获得表面的自然颜色图案。使用红外激光器可滤除红外光，从而提高从 RGB 相机中提取颜色参数的性能。
