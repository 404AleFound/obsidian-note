# Android 触摸事件原理

 触摸事件的传递路径是从 `Activity` 到 `Window`，再到 `View`。具体来说，当一个触摸事件产生时，首先会传递给 `Activity` 的 `dispatchTouchEvent` 方法，然后由 `Activity` 将事件传递给 `Window`，最后由 `Window` 将事件传递给顶层的 `View`。在 `View` 层级结构中，事件会从上到下（父 `View` 到子 `View`）进行传递，直到有一个 `View` 能够处理这个事件为止。

# 相关实现调研

在 Android 中获取全应用的触摸事件的方法，一般有如下几种：
- 方案1：`Window.Callback`，在 `Activity` 的 `Window` 顶层代理 `dispatchTouchEvent`
- 方案2：遍历 `View` 树批量挂 `OnTouchListener`，每个 `View` 套 `listener`，实现全局采集
- 方案3：透明 `Overlay` 层，用 `WindowManager` 加一层透明 `View`，事件先经它再透传
- 方案4：`AccessibilityService`，注册系统级无障碍服务,跨 App 全局监听

## 方案一：`Window.Callback`

每个 `Activity` 的 `Window` 内部都有一个 `Window.Callback` 接口实现——默认就是 `Activity` 自己。系统所有触摸事件分发链上,都会先经过 `Window.Callback.dispatchTouchEvent(event)` 这个入口。

替换这个 callback，用 Kotlin 接口委托语法包一层：
 
```kotlin
val original = window.callback
	window.callback = object : Window.Callback by original {
		override fun dispatchTouchEvent(e: MotionEvent): Boolean {
		emit(e) // 转发一下
		return original.dispatchTouchEvent(e)// 原样转交,不影响业务
      }                                                               
  }  
```

**优点**
- 覆盖面广：全 App 所有 Activity 内的触摸事件主流场景全收。
- 轻量化：每个 Activity 只多一层 wrapper，事件多走一层方法调用。
- 已有实现：bilibili OpLog 也走这条路，模块路径 `andruid/common/oplog/oplog`

**缺点**
- 多 SDK 同时 `hook` 时撤钩可能破坏链。

## 方案二：遍历 `View` 

事件在 `Window.Callback` 下发后，会沿 `View` 树向下分发到命中的 `View`。通过递归遍历整棵 View 树自动挂载，实现全局监听。每个 `View` 有 `setOnTouchListener` 接口接收触摸事件：

```kotlin
fun hookAll(view: View) {
	view.setOnTouchListener { v, e ->
		emit(e)
		false  // 关键:return false 不消费,让事件继续走 onTouchEvent
	}
    if (view is ViewGroup) {
	    for (i in 0 until view.childCount) hookAll(view.getChildAt(i))
	}
}
hookAll(activity.window.decorView)  // 从根 View 开始递归
```

**优点**
- 概念直观：每个 `View` 各自管理,不需要理解 `Window` 机制
- 细粒度可控：理论上能精确到每个 `View` 决定 `hook` 与否，适合"只关心特定区域触摸"的场景

**缺点**
- 粒度过细：需要手动给每一个 `View` 单独设置接口接触触摸事件，有点繁琐。
- 性能开销：每次触摸事件都要在命中链路上多走 N 层 `lambda` 调用，`RecyclerView` 滚动场景压力明显。
- 对于一些没有挂载手势识别的 `View` 无法进行识别。

## 方案三：透明 `Overlay` 层

通过 `WindowManager.addView` 在 `Activity` 上方再加一层全屏透明 `View`，设置 `setOnTouchListener` 收事件后 `return false` 让事件透传给底下。相当于将方案一的装勾子事件，替换为装透明 `Overlay` 层。

```kotlin
val overlay = View(activity).apply {
	setOnTouchListener { _, event ->
		emit(event)
		false
	}
}
val params = WindowManager.LayoutParams(
	MATCH_PARENT, MATCH_PARENT,
	TYPE_APPLICATION_PANEL,
	FLAG_NOT_FOCUSABLE or FLAG_NOT_TOUCH_MODAL,
	PixelFormat.TRANSLUCENT,
)
windowManager.addView(overlay, params)
```

**优点**
- 不动业务 callback 链，避免了多 SDK 同时 `hook` 时撤钩可能破坏链的风险。

**缺点**
- 跨 Window 分发干扰系统事件机制,引发嵌套滚动失效、手势识别错判等体验类 bug。
- 跟纯采集需求不匹配：Overlay 的优势在"既要事件又要画 UI"，采集场景中代价远大于收益。
- 跨 Activity 全局需特权：TYPE_APPLICATION_OVERLAY 需 SYSTEM_ALERT_WINDOW  
  权限，Android 6.0+ 要用户手动到设置授权。

## 方案四：`AccessibilityService`

继承系统 `AccessibilityService`,在 `manifest` 注册并配置接收触摸事件能力。开启后,所有 App、所有 `Window`、所有 `Surface` 内的触摸事件都会通过系统级回调送到你的服务里。

**可行性：**
- 权限给的太大了，显然不可行。


# 总结

使用 android 自带的手势识别器进行手势事件的产生与合并。

