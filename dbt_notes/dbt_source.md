# DBT Source

## What is a source in dbt 

source is the raw data used for data warehouse modeling 

DBT source can do:
- documentation for raw tables (yml files) Table / column description 
- use `source(src_name, table_name)` to easily reference raw tables (single place of change when raw table rename)
- closely related to **EL** paradigm

## example source yml 

```
version: 2 
sources:
    - name xxx (schema)
      database: db_name
      tables:
        - name: orders
        - name: customers
```

templating for source table is: `db_name`.`source_name`.`table_name`

## what is source freshness 

Use record latest update to check whether ingestion time is close to record last update time. 
(typically ingestion is done everyday)

```
sources:
    - name: xxx
      freshness:
         warn_after: {count: 12, period: hour}
         error_after: {count: 24, period: hour} 
      loaded_at_filed: column_name_of_record_update
```

## How to rename source schema (DB reanme)

`{{ source('xxx_alias', 'table_name') }}`

1. source_name update to alias 
2. schema as the original schema name 

```
sources:
  - name: xxx_alias '
    database: db_name
    schema: original_schema_name
    tables:
      - table1
      - table2
```


## How to rename source table (table rename)

`{{ source('db_name', 'xxx_alias)}}`

1. source table name update to the alias
2. source tables identifier as the original table name

```
sources:
  - name: dbt_name
    tables:
      - name: table_alias
        identifier: table_original names
```