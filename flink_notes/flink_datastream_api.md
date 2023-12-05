# Flink DataStream API



## Flink DataStream API overview

![flink_datastream_api_overview](flink_datastream_api_overview.png)

get execution environment (config if any) -> setup data source -> transformation logic -> setup sink -> call env.execute() to start job


## Flink DataStream API Get Execution Environment

flink has two types of execution environment

1. local (mini mock cluster)
2. remote cluster


local or remote: getExecutionEnvironment 可配置参数或使用默认参数

```
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
```


Remote 定制执行环境，上传jar包运行

`env = StreamExecutionEnvironment.createRemoteEnvironment(host, port, jarFilePath);`

```
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

public class Main {
    public static void main(String[] args) throws Exception {
        String host = "localhost";
        int port = 6123;
        String jarFilePath = "/path/to/your/jarfile.jar";

        StreamExecutionEnvironment env = StreamExecutionEnvironment.createRemoteEnvironment(host, port, jarFilePath);

        // Your Flink job code here...

        env.execute("Flink Streaming Job");
    }
}
```

## Flink environment Batch VS Streaming mode

flink 支持流批一体，可以通过 指定运行模式切换

```
// in program 
env.setRuntimeMode(RuntimeExecutionMode.BATCH);
env.setRuntimeMode(RuntimeExecutionMode.STREAMING);

# CLI config
bin/flink run -Dexecution.runtime-mode=BATCH ...
```



## Flink DataStream API execute VS executeAsync()

- `env.execute()` 是 block执行的。 因为流不会停止
- `env.executeAsync()` 是非阻塞的，如果希望写在同一个文件中的，多个 `execute` 异步执行


## Flink Source Overview

- flink 早期版本 `addSource()`
- flink 1.12 流批一体 新版本 `fromSource(source object)`

flink source 主要有

- from sequence / element
- from file source
- from socket source
- data generator
- Kafka


## Flink DataStream API - Source

template for flink source

```
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

// 1. create different sources here: file / datagen / socket / kafka 

// 2. put source to formSource interface
DataStreamSource<String> source = env.fromSource(xx_source, WatermarkStrategy.noWatermarks(), "source name");

source.print();
env.execute();
```

1. from java collection

```
DataStreamSource<Integer> source =  env.fromElements(1,2,3);
DataStreamSource<Integer> source =  env.fromCollection(Arrays.asList(1,2,3));
```


2. from file as stream, dependency `flink-connector-files`

```
// FileSource API
FileSource<String> fileSource = FileSource.forRecordStreamFormat(
        new TextLineInputFormat(),
        new Path("input/words.txt")
).build();
```

3. from network socket (unbounded)

```
// socket IP and port
DataStreamSource<String> source = env.socketTextStream("localhost", 7777);
```

4. from data generator for mock data, dependency `flink-connector-datagen`

```
// DataGeneratorSource API 
// 1. DataGeneratorFunction
// 2. Long max count 数量，如10  / 10000
// 3. Rate limit 
// 4. TYPES.xxx 返回类型

DataGeneratorSource<String> dataGeneratorSource = new DataGeneratorSource<>(xxx)
DataStreamSource<String> source = env.fromSource(dataGeneratorSource, WatermarkStrategy.noWatermarks(), "DateGen");
source.print();
```

5. from Kafka dependency `flink-connector-kafka`

```
// KafkaSource API 
KafkaSource<String> kafkaSource = KafkaSource.<String>builder()
    .setBootstrapServers("hadoop102:9092")
    .setTopics("topic_1")
    .setGroupId("atguigu")
    .setStartingOffsets(OffsetsInitializer.latest())
    .setValueOnlyDeserializer(new SimpleStringSchema()) 
    .build();

```


## Flink DataStream API - Source Data Types

Flink 类型系统: 实现了 序列化，反序列化 及比较器

```
import org.apache.flink.api.common.typeinfo;

TypeInformation

Types.xxx 会构造返回 TypeInformation 类型
```


当返回类型，推断不准确时，如 lambda function, 可以显示指定类型

```
DataStreamOperator.returns(TypeInformation)
e.g. SingleOutputStreamOperator.returns(Types.TUPLE(Types.STRING, Types.INT))
```


Flink support POJO 类型要求

1. public class
2. has default constructor (no arguments)
3. attributes are public accesible (public attributes / public getter,setter)
4. attributes are serializable


Flink支持的数据类型

- 基本类型: 所有Java基本类型及其包装类
- 数组类型
- 复合数据类型: java TUPLE, flink TUPLE, scala TUPLE, Tuple0~Tuple25，不支持空字段, ROW, POJO
- other: List / Map / Option / Either




## Flink Data Stream API - Transformation

- map: 一进一出
- flter: 根据 true/false 条件过滤
- flatMap:  一进多出

```
source.map(value -> value.getId()) // lambda
source.map(new MapFunction() { override map interface } ) // implement logic in MapFunction 

source.filter()

source.flatMap()
```




## Flink DataStream API - Sink

- flink 早期版本 `addSink()`
- flink 新版本 `sinkTo(sink object)`

connector 有些支持 source / sink, 需要确认
https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/datastream/overview/


## Docs

- https://javadoc.io/doc/org.apache.flink/flink-streaming-java/1.17.0/index.html
- https://nightlies.apache.org/flink/flink-docs-release-1.17/


## Java data structure used in Flink


`java.util.Collection`

`java.util.Arrays`

`java.TUPLE`

