# iOS 触摸事件原理

## Run Looper 获取事件

## UI 触摸、UI 事件、UI 响应者
### UITouch

一个手指一次触摸屏幕，就对应生成一个UITouch对象。多个手指同时触摸，生成多个 UITouch 对象。

多个手指先后触摸，系统会根据触摸的位置判断是否更新同一个UITouch对象。
- 若两个手指一前一后触摸同一个位置（即双击），那么第一次触摸时生成一个UITouch对象，第二次触摸更新这个UITouch对象（UITouch对象的 **tap count** 属性值从1变成2）
- 若两个手指一前一后触摸的位置不同，将会生成两个UITouch对象，两者之间没有联系。

每个UITouch对象记录了触摸的一些信息，包括触摸时间、位置、阶段、所处的视图、窗口等信息。
### UIEvent

触摸的目的是生成触摸事件供响应者响应，一个触摸事件对应一个UIEvent对象，其中的 **type** 属性标识了事件的类型（UI 事件不只有触摸事件）。

UIEvent 对象中包含了触发该事件的触摸对象的集合，因为一个触摸事件可能是由多个手指同时触摸产生的。触摸对象集合通过 **allTouches** 属性获取。
### UIResponder

每个响应者都是一个UIResponder对象，即所有派生自UIResponder的对象，本身都具备响应事件的能力。因此以下类的实例都是响应者：
- UIView
- UIViewController
- UIApplication
- AppDelegate

响应者之所以能响应事件，因为其提供了4个处理触摸事件的方法：

```objectivec
// 手指触碰屏幕，触摸开始
- (void)touchesBegan:(NSSet<UITouch *> *)touches withEvent:(nullable UIEvent *)event;
// 手指在屏幕上移动
- (void)touchesMoved:(NSSet<UITouch *> *)touches withEvent:(nullable UIEvent *)event;
// 手指离开屏幕，触摸结束
- (void)touchesEnded:(NSSet<UITouch *> *)touches withEvent:(nullable UIEvent *)event;
// 触摸结束前，某个系统事件中断了触摸，例如电话呼入
- (void)touchesCancelled:(NSSet<UITouch *> *)touches withEvent:(nullable UIEvent *)event;
```


## Hit-Testing

## 事件的响应

经历 Hit-Testing 后，UIApplication 已经知道事件的最佳响应者了，接下来：
- 将事件传递给最佳响应者响应
- 事件沿着响应链传递

# 相关实现调研

>[!note]
>场景：被动嗅探用户在所有 UIWindow 上的触摸事件，识别 CLICK / LONG_CLICK / DOUBLE_CLICK / SCROLL / PINCH，喂给上层做画质 / 性能决策，不影响业务交互。

## 方案1：神策 SensorsAnalytics


# 方案确定

通过 swizzling 拉入原始的触摸事件，手写手势识别器，将 ScreenActionEvent 提供给上层。

## swizzle 替换 sendEvent 方法

## 手写 gesture detector 方法
### 单指识别器

### 双指识别器
