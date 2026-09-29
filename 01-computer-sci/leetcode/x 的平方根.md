---
tags:
  - leetcode
  - binary-search
---
https://leetcode.cn/problems/sqrtx/

# 题解

```cpp
class Solution {
public:
	int mySqrt(int x) {
		int left = 0; 
		int right = x;
		int mid;
		int ans;
		while (left <= right) {
			mid = left + (right - left) / 2;
			if ((long long) mid * mid <= x) {
				ans = mid;
				left = mid + 1;
			} else {
				right = mid - 1;
			}
		}
		return ans;
	}
};
```

# 分析
## 时间复杂度
## 空间复杂度