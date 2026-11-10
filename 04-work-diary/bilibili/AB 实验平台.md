# dashboard 查询 SQL

### 常规 AB 实验对照查询

```sql
SELECT
if(if(modulo(javaHash(upper(hex(MD5(concat(buvid, 'dd_enable_basic_state_screen_action'))))), 1000) >= 0,
    modulo(javaHash(upper(hex(MD5(concat(buvid, 'dd_enable_basic_state_screen_action'))))), 1000),
    modulo(javaHash(upper(hex(MD5(concat(buvid, 'dd_enable_basic_state_screen_action'))))), 1000) + 1000) < 500, 1, 0) as group_id,

uniq(if(first_video_time>0,asset_item_session,null)) as all_vv,   -- 总vv数
uniq(if(first_video_time>0,buvid,null)) as all_uv,    -- 总uv数
all_vv/all_uv as avg_vv,    -- 人均播放vv数
sum(if(first_video_time>0,asset_item_time_of_session,null)) / all_vv/1000 as avg_vv_play_time,    -- 平均vv播放时长(秒）
sum(if(first_video_time>0,asset_item_time_of_session,null)) / all_uv/1000 as avg_uv_play_time,    -- 人均播放总时长(秒）

quantileExact(0.9)(ijk_cpu_rate) as ijkcpu_90,
quantileExact(0.9)(ijk_mem) as ijkmem_90,
quantileExact(0.9)(main_cpu_rate) as maincpu_90,
quantileExact(0.9)(main_mem) as mainmem_90,
avg(ijk_mem) as ijkmem_avg,
avg(main_mem) as manmem_avg

--FROM bilibili_ijk_monitor.ads_mobile_ijk_neuron_tracker_pcdn_rt  --p2p事件的表
FROM bilibili_ijk_monitor.ads_mobile_ijk_neuron_tracker_rt         --stop事件的表
WHERE
  $timeFilter
  AND $to - $from <= $TimeRange
  AND app_id = $app_id
  AND platform = $platform
  AND toString(version_code) like '$version_code'
  AND toString(network) like toString($network)
  AND toString(mode) like toString($mode)
  AND toString(iformat) like toString('$iformat')
  AND toString(video_port) like toString('$video_port')
  AND toString(dash_cur_qn) like toString('$dash_cur_qn')
  AND toString(item_play) like toString('$item_play')
  -- AND toString(vcodec) like $vcodec
  AND toString(playback_rate) like '$playback_rate'
  AND toString(first_render_mode) like toString('$first_render_mode')
  AND force_report=0
  AND asset_item_time_of_session < 18000000
  -- AND position(video_url, '.m3u8')>0 --过滤hls直播
  -- AND version_code%100=10
  -- AND event_id in ('main.ijk.p2p_status.tracker')    --p2p事件（需和上面的表配套使用）
  AND event_id in ('main.ijk.asset_item_stop.tracker')   --stop事件（需和上面的表配套使用）
  AND province not in ('香港', '澳门', '台湾') and country in ('中国')

GROUP BY group_id
```

### AB 实验时程查询

```sql
SELECT
    toStartOfInterval(time_iso, INTERVAL $intervalTime) as t,
    (quantileExactIf(0.9)(main_mem, grp) - quantileExactIf(0.9)(main_mem, not grp)) as main_mem_p90_delta
FROM
(
    SELECT
        time_iso,
        main_mem,
        if(modulo(javaHash(upper(hex(MD5(concat(buvid, 'dd_enable_basic_state_screen_action'))))), 1000) >= 0, modulo(javaHash(upper(hex(MD5(concat(buvid, 'dd_enable_basic_state_screen_action'))))), 1000), modulo(javaHash(upper(hex(MD5(concat(buvid, 'dd_enable_basic_state_screen_action'))))), 1000) + 1000) < 500 as grp
    FROM bilibili_ijk_monitor.ads_mobile_ijk_neuron_tracker_rt

    WHERE
        $timeFilter
        AND $to - $from <= $TimeRange
        AND app_id = $app_id
        AND platform = $platform
        AND toString(version_code) like '$version_code'
        AND toString(network) like toString($network)
        AND toString(mode) like toString($mode)
        AND toString(iformat) like toString('$iformat')
        AND toString(video_port) like toString('$video_port')
        AND toString(dash_cur_qn) like toString('$dash_cur_qn')
        AND toString(item_play) like toString('$item_play')
        AND toString(playback_rate) like '$playback_rate'
        AND toString(first_render_mode) like toString('$first_render_mode')
        AND force_report = 0
        AND asset_item_time_of_session < 18000000
        AND event_id in ('main.ijk.asset_item_stop.tracker')
        AND province not in ('香港','澳门','台湾')
        AND country in ('中国')
)
GROUP BY t

ORDER BY t

```


## DQL 常用语法

```sql
SELECT  
	字段列表  
FROM  
	表名字段  
WHERE  
	条件列表  
GROUP BY  
	分组字段列表  
HAVING  
	分组后的条件列表  
ORDER BY  
	排序字段列表  
LIMIT  
	分页参数
```

DQL 的执行顺序如下：
```sql
FROM -> WHERE -> GROUP BY -> SELECT -> ORDER BY -> LIMIT
```

相关类型的查询如下：
```sql
-- 条件查询：
SELECT 字段列表 FROM 表名 WHERE 条件列表;

-- 聚合查询：
SELECT 聚合函数(字段列表) FROM 表名;

-- 分组查询：
SELECT 字段列表 FROM 表名 [WHERE 条件] GROUP BY 分组字段名 [HAVING 分组后的过滤条件];

-- 排序查询：
SELECT 字段列表 FROM 表名 ORDER BY 字段1 排序方式1, 字段2 排序方式2;

-- 分页查询：
SELECT 字段列表 FROM 表名 LIMIT 起始索引, 查询记录数;
```

## 查询字段列表

```sql
if(if(modulo(javaHash(upper(hex(MD5(concat(buvid, 'dd_enable_basic_state_screen_action'))))), 1000) >= 0,
    modulo(javaHash(upper(hex(MD5(concat(buvid, 'dd_enable_basic_state_screen_action'))))), 1000),
    modulo(javaHash(upper(hex(MD5(concat(buvid, 'dd_enable_basic_state_screen_action'))))), 1000) + 1000) < 500, 1, 0) as group_id,

uniq(if(first_video_time>0,asset_item_session,null)) as all_vv,   -- 总vv数
uniq(if(first_video_time>0,buvid,null)) as all_uv,    -- 总uv数
all_vv/all_uv as avg_vv,    -- 人均播放vv数
sum(if(first_video_time>0,asset_item_time_of_session,null)) / all_vv/1000 as avg_vv_play_time,    -- 平均vv播放时长(秒）
sum(if(first_video_time>0,asset_item_time_of_session,null)) / all_uv/1000 as avg_uv_play_time,    -- 人均播放总时长(秒）

quantileExact(0.9)(ijk_cpu_rate) as ijkcpu_90,
quantileExact(0.9)(ijk_mem) as ijkmem_90,
quantileExact(0.9)(main_cpu_rate) as maincpu_90,
quantileExact(0.9)(main_mem) as mainmem_90
```

SELECT 子句里除了 group_id 是**分组维度**，其他全部都是**聚合表达式**——它们的作用是把每个分组（group_id=0 和 group_id=1）下的成千上万行数据，**压缩成一行汇总指标**。

### 分组纬度

![](images/Pasted%20image%2020260629143707.png)

```txt
 0 <= HASH(UPPER(MD5(concat(buvid,"dd_enable_basic_state_screen_action")))) % 1000 <= 499 
```

在 DD 中，设置了哈希分桶的相关配置。用户被均匀地哈希到 0～999 这 1000 个桶中，前 500 个桶的用户进入实验组，分发 True 值；后 500 个桶被分配进入对照组，分发 False 值。

>[!note]
>**哈希分桶**是一种通过哈希函数将数据均匀分配到固定数量"桶"中的技术，用一个确定性函数把无限的输入空间压缩到有限的桶。
>
>数学形式：`bucket(x) = hash(x) mod N`。其中，x 是输入（这里为 buvid + 盐值），N 为桶数，结果为 `[0, N-1]` 之间的数字。
>
>不同实验用不同盐 ：同一用户在不同实验里独立分组 ，可以避免实验间污染。**没有盐的分桶在 AB 场景里是错的。**

在 sql 查询中，为了保证 Hash 值的非负性，需要对计算出来负的哈希值加上桶数。

>[!note]
>javaHash 返回有符号 int → % 1000 可能负数 → 必须修正成 [0, 999]。这是 SQL 里那一坨 if(mod >= 0, mod, mod + 1000) 的由来。


### 聚合方法
上述查询中，使用了三类聚合函数以计算对应的查询指标。

| 类型   | 函数                      | 作用               |
| ---- | ----------------------- | ---------------- |
| 去重计数 | `uniq(x)`               | 计算 x 的不用的个数      |
| 求和   | `sum(x)`                | 把所有 x 的值相加       |
| 分位数  | `quantileExact(0.9)(x)` | 精确计算 x 的前 90% 的值 |

常见的音视频指标如下：

| 指标  | 全称                  | 含义     | 颗粒度      |
| --- | ------------------- | ------ | -------- |
| VV  | Video View          | 视频播放次数 | 一次播放     |
| PV  | Page View           | 页面访问次数 | 一次页面打开   |
| UV  | Unique Visitor      | 去重访客次数 | 一个用户     |
| DAU | Daily Active User   | 日活跃用户数 | 一天内一个用户  |
| MAU | Monthly Active User | 月活跃用户数 | 一个月内一个用户 |
first_video_time > 0 是为了**只算真正起播的会话**——如果用户点开视频但首帧都没出来就关掉，不算一次有效播放。
## 条件字段列表
