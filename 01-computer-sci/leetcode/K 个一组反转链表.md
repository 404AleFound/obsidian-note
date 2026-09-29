---
tags:
  - leetcode
  - linked-list
---
https://leetcode.cn/problems/reverse-nodes-in-k-group/description/

# 题目

给你链表的头节点 `head` ，每 `k` 个节点一组进行翻转，请你返回修改后的链表。

`k` 是一个正整数，它的值小于或等于链表的长度。如果节点总数不是 `k` 的整数倍，那么请将最后剩余的节点保持原有顺序。

你不能只是单纯的改变节点内部的值，而是需要实际进行节点交换。

**示例 1：**

![](https://assets.leetcode.com/uploads/2020/10/03/reverse_ex1.jpg)

**输入：** `head = [1,2,3,4,5], k = 2`
**输出：**`[2,1,4,3,5]`

# 题解

```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */
class Solution {
private:
    ListNode* skipN(ListNode* head, int n) {
        for (int i = 0; i < n; i++) {
            if (!head) break;
            head = head->next;
        }
        return head;
    }
    void reverseInterval(ListNode* pre, int k) {
        ListNode* curr = pre->next;
        ListNode* next = curr->next;
        for(int i = 0; i < k - 1; i++) {
            curr->next = next->next;
            next->next = pre->next;
            pre->next = next;
            next = curr->next;
        }
    }
public:
    ListNode* reverseKGroup(ListNode* head, int k) {
        ListNode* dummyHead = new ListNode();
        dummyHead->next = head;

        ListNode* pre = dummyHead;
        while(skipN(pre, k)) {
            ListNode* newPre = pre->next;
            reverseInterval(pre, k);
            pre = newPre;
        }
        return dummyHead->next;
    }
};
```

# 分析
## 时间复杂度
## 空间复杂度