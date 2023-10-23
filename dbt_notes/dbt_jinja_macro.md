# DBT Jinja & Macros


## 1. what is packages

packages have predefined models, macros for you to import and use in the project


## 2. how to install packages

- use predefined package name
- use github repo link and branch name
- use local project folder (local package development)


## 3. union-tables-by-prefix-macro 什么时候使用
对于分库 分表的场景，可以把他们自动 union all 起来


## 4. how to test a macros?

`$dbt run-operation --args {JOSN}`

## 5. `run_query` macro returns a Table object that follows agate API

https://docs.getdbt.com/reference/dbt-jinja-functions/run_query

## 6. common dbt jinja function or objects 

**objects** 

- target 
- graph 

**functions**
- log 
- run_query


## 7. common jinjia syntax used in dbt 

blocks:

- branching: if / elif  / else 
- loop: for 
- customized macro 

executing block
- `{{ }}`
- `{% do xxx %}`

others:
- built-in funciton (e.g. str functions)
- whitespace control (trailing / heading whitespace)