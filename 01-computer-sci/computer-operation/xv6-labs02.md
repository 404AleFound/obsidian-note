# xv6-labs-02

## `system call tracking`

系统调用是操作系统内核提供的接口，提供封装好的底层功能。然而，**系统调用的函数或者地址不是直接暴露给用户的**。内核只是提供了一个统一的系统调用入口，称为 `ECALL`。`ECALL` 接收一个数字参数，当一个用户程序想要将程序执行的控制权转移到内核，它只需要执行 `ECALL` 指令，并传入一个数字。这里的数字参数代表了应用程序想要调用的系统调用。这样的设计有很多优点，最直观的是，可以在 `ECALL` 内调用系统调用前，进行参数检查或者权限检查，避免非法的调用。

首先，在 `user/user.h` 中提供一个用户的接口。

```c
// user/user.h
// ...
int sleep(int);
int uptime(void);
int trace(int); // 新的系统调用 trace 的函数签名
```

接着在 `user/usys.ps` 里为这个函数签名加入一个 `entry`。

```c
// user/usys.pl
// ...
entry("sleep");
entry("uptime");
entry("trace");
```

```c
// /usr/syscall.c
void
syscall(void)
{
	int num;
	struct proc *p = myproc();
	
	num = p->trapframe->a7;
	if (num > 0 && num < NELEM(syscalls) && syscalls[num]) {
		p->trapframe->a0 = syscall[num];
	} else {
		printf("%d %s: unknown sys call %d\n"
			p->pid, p->name, num);
		p->trapframe->a0 = -1;
	}
}
```

用户调用我们提供的系统调用接口 `int trace(int)`。该接口由 `Perl` 脚本生成的汇编代码实现：它将 `SYS_trace` 的编号放入 `a7` 寄存器中，并通过 `ecall` 指令在硬件支持下从用户态切换到内核态。随后，控制流转入系统调用的通用入口 `void syscall(void)`。该入口从 `a7` 寄存器中读出当前需要调用的系统调用编号，并通过函数指针数组 `uint64(*syscalls[])(void)` 跳转到对应的具体系统调用实现，最后将返回值放入 `a0` 寄存器。从第二步 `ecall` 返回后，汇编指令 `ret` 使用用户侧的系统调用接口得以返回。

## `Sysinfo`

