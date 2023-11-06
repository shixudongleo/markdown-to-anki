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




## Custom Schema 

default behavior or model build in `target.schema`. 
In dbt projects with lots of models, it may be useful to instead build some models in schemas other than your target schema – this can help logically group models together. (e.g. snapshot is configured in annother separate schema)


dbt will generate the schema name for a model by concatenating the custom schema to the target schema, 
as in: `<target_schema>_<custom_schema>`

example

| target_schema   |      custom_schema      |  final_schema |
|----------|:-------------:|------:|
| analytics |  None | analytics |
| analytics |    marketing   |   analytics_marketing |
| analytics | core |    analytics_core |


why concat `target.schema` + custom schema?

if not, only use custom schema without `target.schema`. the schema that your development models are built in would be the same schema that your production models are built in! Instead, concatenating the custom schema to the target schema helps create distinct schema names, reducing naming conflicts.



https://docs.getdbt.com/docs/build/custom-schemas


## How to configure custom schema

1. use the `config` block to set `schema` attributes (for single model)
2. use `dbt_project.yml` (for models under a subfolder)

```
models:
  my_project:
    marketing:
      +schema: marketing
    orders:
      +schema: order
```

## advanced: how to change custom schema generation process?

dbt uses a default macro called `generate_schema_name`, override the function to achieve different behavior

```
{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}

        {{ default_schema }}

    {%- else -%}

        {{ default_schema }}_{{ custom_schema_name | trim }}

    {%- endif -%}

{%- endmacro %}
```
