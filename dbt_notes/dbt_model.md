# DBT Model

## What is a model in dbt? 

a select statement is a relation model in dbt. (python dataframe for python model)

## what commands are related to dbt model?

```
dbt compile
dbt run 
dbt built 
```

what are the difference among them.

## what is modularity in dbt?

- modularity is a structural way to organise data warehouse objects. it is highly related to reusability. 
- modularity allows to build data artifacts in logical steps.


## What are the key concepts for dbt model (Conventions)

- source 
- staging (`stg_/ ods`): stored as view for simple transformation 
- dim / fact tables
- data mart 

## dbt project structure

folder structure under modle folder

```
models
  - source_yml (include source schema/ docs / freshness)
  - staging SQL + yml (materialized as view)
  - data domain 1(yml / SQL)
    - dim
    - fact (dwd)
  - data domain 2
```

## what is the default materialization in dbt 

view is the default materialization


