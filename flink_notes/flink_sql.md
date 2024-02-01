# Apache Flink

Tuple2 is commonly used

[尚硅谷大数据Flink1.17实战教程](https://www.bilibili.com/video/BV1eg4y1V7AN/)



## Flink SQL - Dynamic Table: the underlying data

流表(dynamic table) VS 静态表, 分别区别于流处理和批处理。

- DataStream to Dynamic Table
- Dynamic Table to DataStream (Table to Stream Conversion)
- 3 types of streams: append-only stream/ changelog stream (retract stream / upsert stream).
- changelog operations need to be encoded to reflect state change in dynamic table: insert / update / delete.

Flink Table 转 Datastream 是支持 append-only stream / retract stream (delete + insert) !! upsert stream not supported.

Flink table interact with external databases, depends on external data system support, may support upsert stream. (e.g. Kafka + Upsert)


examples:

- append-only stream: web log traffic in append-only stream / filtering based on web log traffic is also append-only stream /
group by window is append-only as each window output single record
- group by non-winows is retract / upsert stream: as there is update on existing rows

https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/table/concepts/dynamic_tables/

## Flink SQL - Streaming Time Attributes

time semantics:

- event time: capture event generation time, allowing for consistent results despite out-of-order or late events.
- processing time
- watermark: current progress of processing: it also needs regular indications of how far along in event time the processing has progressed so far (via so-called **watermarks**).

Time attributes properties:

1. what: Time attributes behave like regular timestamps, and are accessible for calculations.

2. how: Time attributes can be part of every **table schema**. They are defined when creating a table from a `CREATE TABLE DDL` or a `DataStream`.

3. As long as a time attribute is not modified, and is simply forwarded from one part of a query to another, it remains a valid time attribute

Event time & watermark DDL

```
<watermark_definition>:
  WATERMARK FOR rowtime_column_name AS watermark_strategy_expression

CREATE TABLE user_actions (
  user_name STRING,
  data STRING,
  user_action_time TIMESTAMP(3),
  -- declare user_action_time as event time attribute and use 5 seconds delayed watermark strategy
  WATERMARK FOR user_action_time AS user_action_time - INTERVAL '5' SECOND
) WITH (
  ...
);
```


Processing Time DDL

```
CREATE TABLE user_actions (
  user_name STRING,
  data STRING,
  user_action_time AS PROCTIME() -- declare an additional field as a processing time attribute
) WITH (
  ...
);
```

https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/table/concepts/time_attributes/


## Flink SQL Windowing TVF (table-value function)

通过时间语意，把数据按窗口分组， 一个数据，可以落入多个组

- Apache Flink provides 3 built-in windowing TVFs: TUMBLE, HOP and CUMULATE.
- The return value of windowing TVF is a new relation that includes all columns of original relation as well as additional 3 columns named “window_start”, “window_end”, “window_time” to indicate the assigned window.
- The value of `window_time` always equal to `window_end` - 1ms.

TUMBLE, HOP, CUMULATE syntax

- TUMPLE(TABLE table_naem, DESCRIPTOR(ts_col), window_size_in_interval)
- HOP(TABLE table_naem, DESCRIPTOR(ts_col), window_offset_in_interval, window_size_in_interval)
- CUMULATE(TABLE table_naem, DESCRIPTOR(ts_col), window_size_breakdown_in_interval, window_size_total_in_interval)

```
SELECT * 
FROM TABLE(
   TUMBLE(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '10' INUTES)
);
```

You can think CUMULATE function as applying TUMBLE windowing with max window size first, and split each tumbling windows into several windows with same window start and window ends of step-size difference.


once you did windowing, further windowing related computation will be available:

- window aggregation
- window TOPN
- window join
- window deduplication

## Flink SQL - Window Aggregation

pattern1

先定义窗口 衍生表，(window_start/window_end/window_time) 属性可以直接使用。

```
select 
from <window_vtf_table>
group by window_start, window_end, ...
```

pattern2 - deprecated /legacy

group by 时， 使用 `TUMBLE/ HOP/ SESSION` 窗口，窗口开时，结束时间 可以用
`TUMBLE_START/_END, HOP_START/_END, SESSION_START/_END` 获取

```
select 
    TUMBLE_START/TUMBLE_END(time_attr, interval) 
from normal_table
group by xxx, TUMBLE(time_attr, interval) 
```

## Flink SQL - window TopN

example1: Window Top-N follows after Windowing TVF

1. 先windowing TVF (切分窗口)
2. 再rank row_number() based on partition by window_start/ window_end
3. 过滤 row_number 前x (e.g. row_rank <= 3)

```
SELECT *
FROM (
    SELECT bidtime, price, item, supplier_id, window_start, window_end
    , ROW_NUMBER() OVER (PARTITION BY window_start, window_end ORDER BY price DESC) as rownum
    FROM TABLE(
               TUMBLE(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '10' MINUTES)
        )
  ) WHERE rownum <= 3;
```


example2: Window Top-N follows after Window Aggregation

1. 先用 window TVF + aggregation  (切分窗口并聚合)
2. 再rank row_number() based on partition by window_start/ window_end
3. 过滤 row_number 前x (e.g. row_rank <= 3)

```
SELECT *
FROM (
    SELECT *
        , ROW_NUMBER() OVER (PARTITION BY window_start, window_end ORDER BY price DESC) as rownum
    FROM (
      SELECT window_start, window_end, supplier_id, SUM(price) as price, COUNT(*) as cnt
      FROM TABLE(
        TUMBLE(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '10' MINUTES))
      GROUP BY window_start, window_end, supplier_id
    )
) WHERE rownum <= 3;
```


## Flink SQL window deduplication

limitation: Window Deduplication requires order key must be event time attribute

1. 先windowing TVF (切分窗口)
2. 再rank row_number() based on partition by window_start/ window_end order by event time ASC|DESC (frist / last row)
3. 过滤 row_number 前x (e.g. row_rank =1)

```
SELECT *
FROM (
    SELECT bidtime, price, item, supplier_id, window_start, window_end
    , ROW_NUMBER() OVER (PARTITION BY window_start, window_end ORDER BY bidtime DESC) AS rownum -- order by must be event time
    FROM TABLE(
               TUMBLE(TABLE Bid, DESCRIPTOR(bidtime), INTERVAL '10' MINUTES))
) WHERE rownum <= 1;
```


## Flink SQL window join

limitations:

1. Currently, The window join requires the join on condition contains window starts equality of input tables and window ends equality of input tables.

2. the windowing TVFs must be the same of left and right inputs e.g. (TUMBLE - TUMBLE / HOP - HOP etc)

```
SELECT L.num as L_Num, L.id as L_Id, R.num as R_Num, R.id as R_Id,
COALESCE(L.window_start, R.window_start) as window_start,
COALESCE(L.window_end, R.window_end) as window_end
FROM (
    SELECT * FROM TABLE(TUMBLE(TABLE LeftTable, DESCRIPTOR(row_time), INTERVAL '5' MINUTES))
) L
FULL JOIN (
    SELECT * FROM TABLE(TUMBLE(TABLE RightTable, DESCRIPTOR(row_time), INTERVAL '5' MINUTES))
) R
ON L.num = R.num AND L.window_start = R.window_start AND L.window_end = R.window_end;
```

## Flink SQL - Group Aggregation

For streaming queries, it is important to understand that Flink runs continuous queries that never terminate.

example:

```
SELECT COUNT(*)
FROM Orders
GROUP BY order_id

SELECT COUNT(DISTINCT order_id) FROM Orders
```

main challenges:

1. the underlying state may infinitely growing (requires to set TTL)
2. the result may be not accurate due to TTL


## Flink SQL Over 窗口

typical use cases:

- provide aggregation stats per row
- TopN of groups
- Deduplicate

Over 要求

- order by must be 时间， 升序 ASC (TopN is different as limited state is required row_rank <= x, Deduplicagte is also with limited state row_rank =1)
- range definition 有两类，时间区间、行数区间。 `range between` VS `rows between`
- range definition: Flink only supports `CURRENT ROW` as the upper boundary.
- 对于 同一个窗口的多个聚合函数，可以定义 window 然后复用。


Range definition

- range definition special value: `CURRENT ROW`
- 时间区间，只有`range between xxx preceding and current row` 没有 `following` keyword
- 行数区间, 只有`rows between n preceding and current row` 没有 `following` keyword

example

```
SELECT 
    id, 
    et, 
    vc,
count(vc) OVER w AS cnt,
sum(vc) OVER w AS sumVC
FROM ws
WINDOW w AS (
    PARTITION BY id
    ORDER BY et
    RANGE BETWEEN INTERVAL '10' SECOND PRECEDING AND CURRENT ROW
)

SELECT 
    id, 
    et, 
    vc,
    avg(vc) OVER (
     PARTITION BY id
     ORDER BY et
     ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
) AS avgVC
FROM ws
```

Window alias for reuse

```
SELECT 
    id, 
    et, 
    vc,
avg(vc) OVER w AS avgVC,
count(vc) OVER w AS cnt
FROM ws
-- very smilar to CET with xxx as 
WINDOW w AS (
    PARTITION BY id
    ORDER BY et
    ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
)
```


## Flink SQL TopN with Over

idea: 用row_number() 去给分组 组内排序， 然后对结果过滤 row_number的前几团

example

```
SELECT id, et, vc, rownum
FROM
    (
        SELECT
            id,
            et,
            vc,
            ROW_NUMBER() OVER ( PARTITION BY id ORDER BY vc desc ) AS row_rank
        FROM
            ws
    )
WHERE row_rank <= 3
```

## Flink SQL Deduplication with Over

idea: 用Over 设置想要去重的 分组(parttition by)， order by 时间升序（第一条）、降序(最新一条)
然后 row_number() 取 row_number = 1

deduplicate 要求

- order by 必须是时间, ASC or DESC (it must be a time attribute. Currently Flink supports processing time attribute and event time attribute.)
- row_number = 1 (rownum = 1 is required for Flink to recognize this query is deduplication.)

example

```
SELECT id, et, vc, rownum
FROM
    (
        SELECT
            id,
            et,
            vc,
            ROW_NUMBER() OVER ( PARTITION BY id,vc ORDER BY et ) AS row_rank
        FROM
            ws
    )
WHERE row_rank = 1;
```

注意升序不会需要更新， 目标：取第一条， 后面同样值来的时候，不需要更新。

WebUI 可以区分 top1 和 deduplciate 算子，通常deduplicate会更高效： `Deduplicate` VS `OverAggregate`


## Flink SQL Join (inner / left / right / full outer join)


- inner join: 等待 left / right data ready for output
- left join: left data arrival, output [L, R] if paired, or [L, null] not paried, 右流真实到达后，需要回撤和更新 (-D/ +I)
- right join: 与 left join 相似
- full outer join: either one of left / right data arrive, output [L,R] if paired, or [L, null], [null, R], 左、右流真实到达后，需要回撤和更新 (-D/ +I)

Join 注意事项

- inner / left / right / full outer join 都需要管理 状态去等待迟到的数据，注意TTL 以免状态无限大，系统死机
- `table.exec.state.ttl=1000` 需要tuning TTL 值，太大：状态太大， 太小：数据没有关联上就停止更新了

limitations

- only equi-joins are supported, i.e., joins that have at least one conjunctive condition with an equality predicate. (join 条件至少有一个equality condition)

## Flink SQL interval join


syntax: cross join 后， 用where 条件控制 interval

- ltime = rtime
- ltime >= rtime - delta1 and ltime <= rtime + delta2
- ltime between rtime - delta1  and rtime + delta2

```
select 
from A, B
where A.id = B.id 
and B >= 下界
and B <= 上界

-- example
SELECT *
FROM Orders o, Shipments s
WHERE o.id = s.order_id
AND o.order_time BETWEEN s.ship_time - INTERVAL '4' HOUR AND s.ship_time
```

limitations:

- interval join requires at least one equi-join predicate and a join condition that bounds the time on both sides.
- interval join only supports append-only tables with time attributes


## Flink SQL dimension table lookup join

lookup 外部 实时查找外部系统: A lookup join is typically used to enrich a table with data that is queried from an external system.

- external MySQL database
- Hbase

基于流处理时间， 查询时的外表状态是什么就是什么


syntax

```
select 
from streamA as a 
join dim_table FOR SYSTEM_TIME AS OF streamA.proc_time as b 
on a.xxx = b.xxx
```

limitation:

-  lookup join also requires a mandatory equality join predicate
- The join requires one table to have a `processing time/proc_time` attribute and the other table to be backed by a lookup source connector.


## Flink SQL - Temporal Join

Flink talbe join a Versioned table

- versioned table in flink is like a SCD type 2 (zipper table)
- this enable the join with dimension information based on valid time (start /end of row validity, correct version)


example

```
SELECT 
     order_id,
     price,
     orders.currency,
     conversion_rate,
     order_time
FROM orders
LEFT JOIN currency_rates FOR SYSTEM_TIME AS OF orders.order_time (proc_time / event time)
ON orders.currency = currency_rates.currency;
```

behavior:

- temporal join with event_time is deterministic, it doesn't change even the dim table changes, as only one correct version is used.
- temporal join doesn't define a time window, old records are not store in the state, as time progress, old records are not relevant anymore.

## Flink SQL Order by / Limit

When running in streaming mode, the primary sort order of a table must be ascending on a time attribute. （there is no this limitation in batch mode）

Order By 子句中必须要有时间属性字段，并且必须写在最前面且为升序。 (start with time column ascending order)


Limit int_x 限制返回行数

order by, limit 流处理作用不到， 更多是在批里面用


## Flink SQL - SQL Hint

用于快速修改 connector With 中的 options

syntax: 表后加 `/*+ xxx_config */`

```
select * from ws1/*+ OPTIONS('rows-per-second'='10')*/;
```


## FLink SQL - Set Operations

去重 VS 不去重(带 all)

- union / union all
- intersect / intersect all
- except / except all

in 子查询只有一列， 不可以是多元tuple, 并且 In 子查询也会涉及到大状态问题，要注意设置 State 的 TTL。

```
SELECT id, vc
FROM ws
WHERE id IN (
SELECT id FROM ws1
)
```

## Flink SQL - Built-in Functions

Doc: Flink home -> Table API / SQL -> Functions

- scalar function VS aggregation function
- temporal function: normal VS _LTZ functions to deal with local time zone s


`show functions` list all available functions


## Flink SQL - extra module for extended functionality

- core module
- hive module, so that hive functions can be used (在Flink 中使用Hive的functions)

注意: 不同modules 有同名function, 优先使用 core module 中的function

```
load module module_name_xxx;

unload module module_name_xxx;

-- module ordering is important
use modules module1, module2; 

show modules
show full modules
```


## Flink SQL Connector - Kafka

Flink SQL client 使用Kafka Connector

1. install flink-sql kafka connector jar lib
2. 重新启动Flink 集群，(冷加载)

Flink SQL  Kafka connector 使用

1. 创建表去连接外部Kafka系统，（参数使用with指定）
2. 读表: 就是对kafka 数据源的使用
3. 写表: 就是对Kafka 数据源 插入数据

syntax

- metadata (`VIRTUAL` for read-only metadata)/ 同名，不同名
- connector options

```
CREATE TABLE t1( 
  `event_time` TIMESTAMP(3) METADATA FROM 'timestamp',
  --列名和元数据名一致可以省略 FROM 'xxxx', VIRTUAL表示只读
  `partition` BIGINT METADATA VIRTUAL,
  `offset` BIGINT METADATA VIRTUAL,
id int, 
ts bigint , 
vc int )
WITH (
  'connector' = 'kafka',
  'properties.bootstrap.servers' = 'hadoop103:9092',
  'properties.group.id' = 'atguigu',
-- 'earliest-offset', 'latest-offset', 'group-offsets', 'timestamp' and 'specific-offsets'
  'scan.startup.mode' = 'earliest-offset',
  -- fixed为flink实现的分区器，一个并行度只写往kafka一个分区
'sink.partitioner' = 'fixed',
  'topic' = 'ws1',
  'format' = 'json'
) 

```

## Flink SQL Connector - File

```
CREATE TABLE t3( id int, ts bigint , vc int )
WITH (
  'connector' = 'filesystem',
  'path' = 'hdfs://hadoop102:8020/data/t3',
  'format' = 'csv'
)
```

## Flink SQL Connector - MySQL

创建 Flink MySQL connector table DDL

- 中定义了主键，使用upsert 模式
- 没有定义主键，使用append 模式 (insert), 主键冲突时会失败，无法插入

exactly once 有两种方式实现

- ACID Transaction
- idempotent with upsert (Flink MySQL connector upsert mode)


```
CREATE TABLE t4
(
    id                      INT,
    ts                   BIGINT,
vc                     INT,
PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector'='jdbc',
    'url' = 'jdbc:mysql://hadoop102:3306/test?useUnicode=true&characterEncoding=UTF-8',
    'username' = 'root',
    'password' = '000000',
    'connection.max-retry-timeout' = '60s',
    'table-name' = 'ws2',
    'sink.buffer-flush.max-rows' = '500',
    'sink.buffer-flush.interval' = '5s',
    'sink.max-retries' = '3',
    'sink.parallelism' = '1'
);

```

## Flink SQL Savepoint

savepoint (checkpoint) 用于存放数据及恢复


save

```
SET state.savepoionts.dir='path to savepoint path';
SET state.checkpoints.dir='path to checkpoint path';

stop job 'xxx_job' with savepoint;
```

recovery

```
SET execution.savepoint.path='path to savepoint path';

insert xxx

-- avoid next job with savepoint to start
RESET execution.savepoint.path;
```

## Flink SQL - Catalog

metadata of data store: one level above databases / tables

e.g.

- hive metastore
- JDBC catalog
- aws glue catalog
- memory catalog (临时的)


JDBC Catalog

1. readonly for metadata, use to fetch MySQL tables for flink to read from / write to
2. can't create new table metadata on MySQL catalog.
3. 交叉使用 MySQL 表和 Flink 表 e.g. join

```
create catalog catalog_xxx with (
    'type' = 'jdbc',
    'default-database' = 'test',
    'username' = 'root',
    'password' = '000000',
    'base-url' = 'jdbc:mysql://hadoop102:3306'
);

use catalog catalog_xxx;
```

Hive Catalog

1. 打通 Hive / Flnik 表
2. Hive metastore 需要作为独立服务运行
3. Flink 创建表（连接表），metadata会 persist 到 hive metastore
4. hive 可以看到 flink 创建的连接表，但是查询会报错


## FlinkSQL VS Table API

1. FlinkSQL 可以在 sql-client CLI 中使用，如何在程序中使用 FlinkSQL 语法 -> 使用Table API
2. Table API

```
tableEnv.executeSql(" create table / insert into / ...")

tableEnv.sqlQuery("sql string")

tableEnv.createTemporaryView("v_name", tableObject)
```

用法很像SparkSQL 在程序中的使用

Tips:

- 所有 使用 DataStream API 需要显示调用 `env.execute()` 去运行主程序
- 如果 仅使用 Table API 可以不调用 `env.execute()`去运行主程序
- 如果 混用 DataStream API 可以使用 `env.execute()` 或者  `tableEnv.sqlQuery("xxx").execute()` 二选一


## Flink Table API 和 DataStream API 的转换

通过转换: 能够灵活的使用两边的接口


```
tableEnv.fromDataStream(data_stream_obj)

tableEnv.toDatastream(table_obj, Class) // 追加流
tableEnv.toChangelogStream(table_obj) // 更新流
```

支持类型: Tuple / Row / Pojo / primitive data type



## Flink SQL sql-client key operations

refer to doc: https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/table/sqlclient/

- `SET / RESET` variables, e.g. `pipeline.name`

Flink 壮态管理都需要考虑TTL


## Flink SQL Hints

SQL hints can be used with SQL statements to alter **execution plans**.

- change planner behavior: manual change skew handling
- config operator resources: parallelism

Dynamic Table Options:

- template: `table_name /*+ OPTIONS(key=val [, key=val]*) */`
- CSV file source `/*+ OPTIONS('csv.ignore-parse-errors'='true') */`
- Kafka source `/*+ OPTIONS('scan.startup.mode'='earliest-offset') */`


- state TTL: `'table.exec.state.ttl' = 'time in ms'`

Query Hints

follows the syntax of Query Hints in Apache Calcite:

- template: `SELECT /*+ hint [, hint ] */ ...`
- broadcast join / shuffle_hash join / shuffle merge join: `SEELCT /*+ BROADCAST(t1) */`
- LOOKUP function behavior sync or async `LOOKUP('table'='Customers', 'async'='false')`


## Flink Configurations

Flink dynamic table conf: https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/table/config/#table-options

Flink sql client conf: https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/table/config/#sql-client-options


Flink SQL hints: https://nightlies.apache.org/flink/flink-docs-master/docs/dev/table/sql/queries/hints/

https://calcite.apache.org/docs/reference.html#sql-hints


## Flink docs

- https://javadoc.io/doc/org.apache.flink/flink-streaming-java/1.17.0/index.html
- https://nightlies.apache.org/flink/flink-docs-release-1.17/
- [Table to Stream Conversion](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/table/concepts/dynamic_tables/)
- [Flink SQL](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/table/sql/queries/overview/)
- [Flink Table Options](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/table/config/#table-options)
- [Flink SQL Client Options](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/table/config/#sql-client-options)
