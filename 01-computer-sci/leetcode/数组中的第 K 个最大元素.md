---
tags:
  - leetcode
  - "#sorting"
---

https://leetcode.cn/problems/kth-largest-element-in-an-array/

# 题目

给定整数数组 `nums` 和整数 `k`，请返回数组中第 `k` 个最大的元素。

请注意，你需要找的是数组排序后的第 `k` 个最大的元素，而不是第 `k` 个不同的元素。

你必须设计并实现时间复杂度为 `O(n)` 的算法解决此问题。

**示例 1:**

**输入:** `[3,2,1,5,6,4], k = 2`
**输出:** `5`

---
# 题解

```cpp
class Solution {
private:
    int quickSearch(vector<int>& nums, int k, int l, int r) {
        if (l >= r) return nums[l];
        int i = l - 1;
        int j = r + 1;
        int x = nums[l];
        while (i < j) {
            do i++; while (nums[i] < x);
            do j--; while (nums[j] > x);
            if (i < j) swap (nums[i], nums[j]);
        }
        if (k <= j) {
            return quickSearch(nums, k, l, j);
        } else {
            return quickSearch(nums, k, j + 1, r);
        }
    }
public:
    int findKthLargest(vector<int>& nums, int k) {
        return quickSearch(nums, nums.size() - k, 0, nums.size() - 1);
    }
};
```

---
# 分析
## 时间复杂度
## 空间复杂度
