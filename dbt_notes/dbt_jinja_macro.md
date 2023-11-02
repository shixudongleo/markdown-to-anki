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

## what is dbt jinja

using templating language in DBT is provided by Jinja.
jinja has a few programming features

- variables: asignment / reference / data type: str / number / list / dict
- control flow: if branching / for loop 
- macro (function)
- white space control

## Jina templating convention of str data type 

参数（param) 是str时，当使用时，它默认是value不带引号"", 引号需要自己提供。

why: 

- 实际场景中，会有引号和无引号的需求，默认无引号，让后续处理更加灵活。
- jinja dbt 中， 使用列名时（column name) 需要使用 str类型，不然jinja会去查找与列名同名的var变量使用

## how to define and use macro 

- create macro in `macros` subfolder with `.sql` file extension
- define func name, and parameters `{% macro func_name(arg1, arg2, ...) %} {% endmacro %}`
- use parameter or variables by `{{ xxx }}`
- call macro by `{{ func(arg1, arg2, ...) }}`


## how to get dbt built-in variables

`{{ target.name }}`

key objects:

- target
- adapter 
- graph 
- this 
- model


## use dbt jinja to limit data processing in deve environment 

```
{%if target.name == 'dev' %}
  add where filter to limit 
{% endif %}
```

## be aware of code readability VS use of macro/func for DRY

SQL human readability <-----------> DRY

- SQL itself is declarative, and more readable 
- by adding more macros, you are reuse a lot more codes (DRY)
- try to find the right number of macros as max in a SQL file 
