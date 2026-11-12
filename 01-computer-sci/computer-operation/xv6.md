# `start.c`

# `riscv.h`

`kernel/riscv.h` 主要是给 xv6 内核提供一组操作 RISC-V 处理器的工具和定义，主要完成如下三件事情：
- 访问处理器寄存器。
- 控制中断和异常处理。
- 支持虚拟内存管理。

可以将 `riscv.h` 堪称 xv6 内核与 RISC-V 硬件之间的工具箱，其提供操作硬件的基础方法，具体在什么时候使用，由内核的其他代码决定。

## 寄存器

xv6 运行在 RISC-V 处理器上，相关的寄存器如下：

### 通用寄存器

|寄存器|ABI 名称|描述|Saver|
|---|---|---|---|
|x0|zero|零值|-|
|x1|ra|返回地址|Caller|
|x2|sp|堆栈指针|Callee|
|x3|gp|全局指针|-|
|x4|tp|线程指针|-|
|x5|t0|临时/备用链接寄存器|Caller|
|x6-x7|t1-t2|临时寄存器|Caller|
|x8|s0/fp|保存寄存器/帧指针|Callee|
|x9|s1/gp|保存寄存器/全局指针|Callee|
|x10-x11|a0-a1|函数参数/返回值|Caller|
|x12-x17|a2-a7|函数参数|Caller|
|x18-x27|s2-s11|保存寄存器|Callee|
|x28-x31|t3-t6|临时寄存器|Caller
### 浮点寄存器

| 寄存器     | ABI 名称   | 描述          | Saver  |
| ------- | -------- | ----------- | ------ |
| f0-f7   | ft0-ft7  | 浮点 临时存储     | Caller |
| f8-f9   | fs0-fs1  | 浮点 保存的寄存器   | Callee |
| f10-f11 | fa0-fa1  | 浮点 函数参数/返回值 | Caller |
| f12-f17 | fa2-fa7  | 浮点 函数参数     | Caller |
| f18-f27 | fs2-fs11 | 浮点 保存的寄存器   | Callee |
| f28-f31 | ft8-ft11 | 浮点 临时存储     | Caller |
### 控制和状态寄存器

控制与状态寄存器（control and status registers）简称 CSR。



## 处理器状态与特权级

机器模式状态

## 中断与异常

## 虚拟内存与页表

## 计数器
