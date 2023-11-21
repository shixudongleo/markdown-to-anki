# maven


## Maven 的核心功能

- 依赖管理
- 项目构建: compile / test / packaging / deployment


## Maven VS IDE tool

software engineering process needs CI/CD and maven can be used to build / test / packaging / deployent during the CI/ CD process

IDE can only work for local machine, the CI/CD doens't work well with IDE.


## What is GAVP object in maven

- G: group id
- A: archifact id
- V: version
- P: packaging


## Where to look for java library's Maven dependency

e.g. Junit

1. goto https://mvnrepository.com/
2. search for Junit
3. use the version which most people use


## typical Maven project tree structure

- pom.xm
- src (main/java | main/scala | main/resources)
- test (java | resources)
- target

under main/java, main/ scala you can specify your modules like com/example/xxx (com.example.xxx)


## Maven Lifecycle commands (build commands)

- mvn clean
- mvn compile (.java to .class 编译)
- mvn test-compile
- mvn test
- mvn package (打成jar包)
- mvn install (package 的 jar包 安装到本地 maven repos)

## how to locate jar package in local maven repos

use the maven repo local path + the group id (e.g. com.example.xxx) as subfolders


## how to use self-defined java module

1. `mvn install` custom java module  A
2. in the project B that depends on custom java module A, add dependency to project B's pom.xml conf


## how to define pom.xml properties and used in the same conf file

```
<!-- define -->
<properties>
    <sprint.version>6.0.0</sprint.version>
</properties>

<!-- reference -->
<dependency>
    <version>${sprint.version}</version>
</dependency>
```


## 3 types of dependencies in Maven

1. plugins (dependencies) used by maven only for build the project source code
2. dependencies (libraries) used by Java source code
3. dependencies (modules) created by user, and use by other project (must be install to local repo to be successfully located by maven)


## key components of Maven dependency

- `<groupId> </groupId>`
- `<artifactId> </artifactId>`
- `<version> </version>`
- `<scope> </scope>`


scope used to define whether jar can be used in 3 envs:

- 编译环境
- 测试环境
- 运行环境

- compile scope can be used in all 3 envs  
- test scope can only be used in 测试环境
- provided scope 编译环境/测试环境 有效， 运行环境无效（由服务器、运行环境提供）provvided, 被服务器提供
- runtime scope
- system scope 由系统提供
- import


## Maven Dependencies install failure

1. network issue
2. the GAVP may not be correct, e.g. version is wrong
3. local maven repo is corrupted (打到maven repo对应的depedency artifact目录，删除)


## Maven build 自定义 属性

- custom build name `<finalName>xxx.jar</finalName>` in build tag
- build to include resources into final package, add resources tag inside build tag
- set custom plugins for maven build packaging


## 如何 使用Maven 快速部署到Tomcat

Maven install tomcat plugin

```
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.tomcat.maven</groupId>
        <artifactId>tomcat7-maven-plugin</artifactId>
        <version>2.2</version>
        <configuration>
          <port>8090</port>
          <path>/</path>
          <uriEncoding>UTF-8</uriEncoding>
          <server>tomcat7</server>
        </configuration>
      </plugin>
    </plugins>
  </build>
```

- use command line to start tomcat with war package `mvn tomcat7:run`
- use IntelliJ IDEA to visual run `tomcat7:run`


## Maven Dependency 传递性 和 版本冲突

A deps B, B deps C

- when project A requires B, we only need to specify dependency of B. (C is automatically installed) 简化依赖
- when project A requires B, we only need to specify version of B, the version of C is automatically checked. 保证依赖版本正确
- when project A requires B, we only need to specify dependency of B. C can be used in project A without explictly specify dependency. 依赖的传递性
    - compile scope 依赖可以传递
    - test, provided scope 不可以 依赖传递
    - `<optinal>true</optiona>` 不可以 依赖传递
    - 依赖冲突发生时， 不可以 依赖传递


## Maven Dependency 传递性 不可用的3种情况

- scope 为 非compile e.g. test / provided
- optional set to true `<optinal>true</optiona>`
- 依赖冲突发生时


what is 依赖冲突发：

```
A -> B -> 1.0.jar
A -> C -> 2.0.jar 
```

how to resolve version conflict

1. maven 自动选择
2. 路径最短优先
3. 先声明者优先 （路径相同时，在projectA中谁先声明，谁优先）
4. 手动解决冲突
    - 显示指定 dependency and version in project A
    - 使用 `<exclusions><exclusion>` 在 A中的B dependency, 那么会使用C中依赖


## Inheritance in Maven project 继承关系 （父 -> 子）

继承配置属性

- 1个父工程 可以有多个子工程
- 父工程中的配置属性 可以传给多个子工程使用
- 在父工程中统一管理项目的依赖信息 (dependency management for multiple modules)


how to use parent config

```
<packaging>pom</packaging>

<modules>
  <module>xxx_child_module</module>
</modules>

<depedencyManagement>
  <dependencies>
  </dependencies>
</depedencyManagement>
```

children config

```
<parent>
  <groupId>parent_group_id</groupId>
  <artifactId>parent_artifact_id</artifactId>
  <version>parent_version</version>
</parent>

<dependencies>
  <dependency>
     <groupId>only groupId</groupId>
    <artifactId>only artifactId</artifactId> 
  </dependency>
</dependencies>
```


手动解决冲突, 可以用于去除依赖

1. 上游依赖中，添加去除，`<optional>true</optional>`, 下游中不再默认添加此依赖
2. 在下游添加`<exclusions>`， 显示去除此依赖


## Maven project 聚合关系

- 1个父工程 可以有多个子工程
- 聚合关系是构建父工程时，多个子工程会一起被构建
- 可以统一管理项目依赖
- 优化整体项目的构建顺序

parent config

```
<modules>
  <module>child1</module>
  <module>child2</module>
</modules>
```



## what if parent module use dependencies without dependencyManagement tag

all dependencies will be inherited by child project.
even for the unnecessary ones

the `<scope>` doesn't matter, all dependencies in the parent project will pass to child projects.



## Sonatype Nexus private maven repository (私服)

1. 安装并使用 nexus 私服
2. 配置 Maven 私用 proxy哪个公共 central maven repository (或多个，并且速度快者优先)
3. 上传，部署 release/snapshot jar包 到 Maven 私服
4. 使用其他人开发的 release/snapshot jar包 （在Maven 私服中）


Todo 添加相关的 tag



## Why using Maven?

typical java web project component

- view layer / view controller
- business logic layer
- persistence layer

maven fix some issues:

- for big project, project can be divided into many projects, and dependencies managed by maven
- jar package manager by maven, (no manual download, version mangement, no manual import jar to project)

## What is Maven?

maven is an automation tool for building Java project.

- source code + resources => (using build tool) => deployable / runtime artifacts.
- similar tool: Make / Ant / Maven / Gradle

## Construction / Build process

1. clean
2. compile
3. test
4. build report/docs
5. packaging
6. install
7. deployment