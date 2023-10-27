# DBT Test 

## what command involved test

`deb test` and `dbt build`

## Testing strategy 

- testing on schedule: automatic / on schedule / testing should be fast / reliable / informative (leading you to what to focus) / be focus (know what to fix, isolated)

- take action: when test failed, you should know what to fix 


## what to test about your data 

1. something true about your data: unique / not null / accepted_value / relationship
2. business logic / edge case about data: singular test 
3. table row relationship (avoid fanout (cartesian product))
4. testing freshness of source 


## when to test 

in development:

- manual 

in deployment:

- automated


in PR to Master Branch 

- CI `dbt build --select state:modified+`
- build the models changed


in QA branch to Master branch

- CI `dbt build`
- pass -> merget to master / failed to fix 


## DBT Test command 

- `dbt test`
- `dbt --select model_name_s_tests` # including generic / singular tests related to a model
- `dbt --select folder1.folder2.*` # including all tests related to models in subfolder
- `dbt test --select test_type:generic/singular`
- `dbt test --select source:*` # all tests related a sources


- `dbt test --select selector1,selector2` # use comma for intersection
- `dbt --select package.*`


## DBT Test Commands - best practice 

`dbt build --fail-fast`

![Best Practice](dbt_test_best_practice.png)

## DBT Test - store test failures 

`dbt test --store-failures` 

for efficient troubleshooting
when the test failed, the result will be saved on a test schema table in the data warehouse. 


## DBT generic test 

- location: `dbt_project/tests/generic/xxx.sql`
- function signiture 

```
{% test generic_test_name(model, column_name) %}

{% endtest %}
```


## DBT override default generic test 

you can override default generic test simply by defining your own generic test logic with same name

![dbt_test_override_generic_test](dbt_test_override_generic_test.png)


## What is a singular test 

- A singular test is a SQL SELECT statement that makes an assertion in reference to a specific model and its specific columns. 
- Singular tests are sql files that live in the tests folder and use the ref function to call a specific model. 


## how to enable and disable singular test 

`{{ config(enabled = False/ True) }}`



## how to use test provided by 3rd party libraries

- dbt_utils 
- dbt_expectations
- audit_helper (only for development)


1. install the package: packages.yml + `dbt dpes`
2. use the package docs to add tests to the model yml according to the documentation

caveats: 

- check the tests is applied to model or column
- tests key as list or embeded object (key-value)


## DBT Test Config 

like dbt model has configurations, dbt test also has configuration

**where to put the dbt test confgi**

1. inside generic / singular test  `{{ config() }}` block
2. in yml file tests block 

    ```
    columns: 
        - name: customer_id
        description: primary key
        tests:
            - unique
            - not_null
            config:
                severity: error
                error_if: ">100"
    ```
3. in `dbt_projects.yml` for project level configs

    ```
    models:
        jaffle_shop:
        ...

    tests:
    jaffle_shop:
        +severity: warn
        +store_failures: true
    ```

## DBT Test - Key Configs

1. `severity` and threshold
2. `where`: filter and reduce the amount of data to test against (allows you to filter down to a subset of rows that you want to test)
3. `limit`: limit the number of fail reocrd returned 
4. `store-failures` / `schema` (store the failed test in schema)

```
    tests:
      - xxx_test:
          config:
            severity:
            where: 
            limit: 10 
            store_failure: true/ false
            schema: test_failures
```


## dbt_utils notes

dbt_utils is a one-stop-shop for several key functions and tests that you’ll use every day in your project.

Here are some useful tests in dbt_utils:

- expression_is_true 
- cardinality_equality
- unique_where
- not_null_where
- not_null_proportion 
- unique_combination_of_columns


## dbt_expectations notes

dbt_expectations contains a large number of tests that you may not find native to dbt or dbt_utils. If you are familiar with Python’s great_expectations, this package might be for you! 
Here are some useful tests in  dbt_expectations:

- expect_column_values_to_be_between
- expect_row_values_to_have_data_for_every_n_datepart
- expect_column_values_to_be_within_n_moving_stdevs
- expect_column_median_to_be_between
- expect_column_values_to_match_regex_list
- Expect_column_values_to_be_increasing


## audit_helper

This package is utilized when you are making significant changes to your models, and you want to be sure the updates do not change the resulting data. The audit helper functions will only be run in the IDE, rather than a test performed in deployment. 
Here are some useful tools in audit_helper:

- compare_relations
- compare_queries
- compare_column_values
- compare_relation_columns
- compare_all_columns
- compare_column_values_verbose