---
tags:
  - leetcode
  - binary-search
---
https://leetcode.cn/problems/search-a-2d-matrix-ii/

# 题目

编写一个高效的算法来搜索 `_m_ x _n_` 矩阵 `matrix` 中的一个目标值 `target` 。该矩阵具有以下特性：

- 每行的元素从左到右升序排列。
- 每列的元素从上到下升序排列。

**示例 1：**

![](https://assets.leetcode.cn/aliyun-lc-upload/uploads/2020/11/25/searchgrid2.jpg)

**输入：** 
```
matrix = [
	[1,4,7,11,15],
	[2,5,8,12,19],
	[3,6,9,16,22],
	[10,13,14,17,24],
	[18,21,23,26,30]
	]
target = 5
```
**输出：** `true`

# 题解

## 二分查找

```cpp
class Solution {
private:
	int binarySearch(vector<int>& nums, int target) {
		int left = 0;
		int right = nums.size() - 1;
		int mid = 0;
		int ans = nums.size();
		while (left <= right) {
			mid = left + (right - left) / 2;
			if (target <= nums[mid]) {
				ans = mid;
				right = mid - 1;
			} else {
				left = mid + 1;
			}
		}
		if (ans < nums.size() && nums[ans] == target) 
			return ans;
		return -1;
	}
public:
	bool searchMatrix(vector<vector<int>>& matrix, int target) {
		int ans = 0;
		for (int i = 0; i < matrix.size(); i++) {
			ans = binarySearch(matrix[i], target);
			if (ans != -1) 
				return true;
		}
        return false;
	}
};
```

## Z 字型查找

```cpp
class Solution {
public:
	int searchMatrix(vector<vector<int>>& matrix, int target) {
		int m = matrix.size();
		int n = matrix[0].size();
		int i = 0;
		int j = n - 1;
		while (i < m && j >= 0) {
			if (matrix[i][j] == target)
				return true;
                
			if (target < matrix[i][j]) {
				j--;
			} else {
				i++;
			}
		}
		return false;
	}
};
```

# 分析

## 时间复杂度

## 空间复杂度