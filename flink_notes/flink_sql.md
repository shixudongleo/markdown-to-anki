# Flink SQL


## Flink SQL Over 窗口

Over 要求

- order by must be 时间， 升序 ASC
- range definition 有两类，时间区间、行数区间。 `range between` VS `rows between`



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

- order by 必须是时间, ASC or DESC
- row_number = 1

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
```


## Flink SQL dimension table looup joion

lookup 外部 实时查找外部系统:

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


## Flink SQL Order by / Limit

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



## Flink docs

- https://javadoc.io/doc/org.apache.flink/flink-streaming-java/1.17.0/index.html
- https://nightlies.apache.org/flink/flink-docs-release-1.17/



