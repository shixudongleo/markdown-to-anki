# DBT qanalabs


## DBT Exposure 

Exposures make it possible to define and describe a downstream use of your dbt project, such as in a dashboard, application, or data science pipeline. By defining exposures, you can then:

- run, test, and list resources that feed into your exposure
- populate a dedicated page in the auto-generated documentation site 

hwo to define `exposure`

1. add `.yml` file and follow `exposure` yml format (very similar to source)
2. how to run / test exposure related resources `--select exposures:exposure_name`

Reference: https://docs.getdbt.com/docs/build/exposures


## DBT Metrics 


When a metric is created in dbt, it takes all the information in a table and simplifies it into a single number that gives you a quick understanding of the data. If the resulting number does not match the expected value, the most likely reason is that the table being used to calculate the metric does not contain accurate data. 

metric consistency

 https://docs.getdbt.com/docs/build/metrics
 https://docs.getdbt.com/docs/build/about-metricflow?version=1.6
 https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl?version=1.6



 ## DBT metrics.calculate by dbt-metrics package 

 Add the dbt_metrics package installation config to your packages.yml file, run dbt deps to install the package, and then run the metrics.calculate macro with the defined metrics


## DBT compile resolve issue / DBT Cloud as well

If you find that your dbt project is not compiling to the values you have set, deleting the target/partial_parse.msgpack file in your project can help. 

## Incremental model unique_key violation 

If the unique_key is not truly unique in the data, the incremental model run will fail with a unique key violation error. 


## how to do legacy SQL migration 

- SQL dialect
- sotred precedures & functions 
- data warehouse

https://docs.getdbt.com/guides/migration/tools/refactoring-legacy-sql


## dbt snapshot model with hard delete

config snapshot with `invalid_hard_delete=True`


## dbt model vs snapshot schema location 

In dbt, the main difference between the way snapshots and models are stored is that snapshots are stored in the same target_schema for everyone, while models are stored in a separate schema for each user to maintain separate development and production environments. The reason for this difference is that snapshots are meant to be run regularly, and it's best to reference the production version of the snapshot, even when developing models, to ensure consistency and make it easier to build models. 


Store snapshots in a separate schema and set different privileges for them compared to other models. This will make it clear to end users that snapshots are special tables that should be treated differently from other models, and help prevent accidental deletion or changes to snapshots.

https://docs.getdbt.com/docs/build/snapshots


## dbt snapshot best practices 

- Use the timestamp strategy where possible

This strategy handles column additions and deletions better than the check strategy.
Ensure your unique key is really unique

- The unique key is used by dbt to match rows up, 

so it's extremely important to make sure this key is actually unique! If you're snapshotting a source, I'd recommend adding a uniqueness test to your source (example).

- Use a target_schema that is separate to your analytics schema

Snapshots cannot be rebuilt. As such, it's a good idea to put snapshots in a separate schema so end users know they are special. From there, you may want to set different privileges on your snapshots compared to your models, and even run them as a different user (or role, depending on your warehouse) to make it very difficult to drop a snapshot unless you really want to.


## You are working on a data warehouse and want to build dependencies between two models that have the same name. In order to achieve this, which of the following options should you use?

. The Ref Function Only Takes One Argument — The Model Name (I.E. The Filename). As A Result, These Model Names Need To Be Unique, Even If They Are In Distinct Folders. Often, This Question Comes Up Because Users Want To Give Two Models The Same Name In Their Warehouse, Splitting Them Across Separate Schemas (E.G. Stripe.Users And App.Users), To Achieve This The Best Way Is To Use Custom Schemas And Custom Aliases.

- stripe.user
- app.user


## hook for custom SQL 


Maria is a data engineer working with dbt for a client. She has identified a need to execute custom SQL specific to the client's data platform that is not provided by dbt's built-in functionality. What feature should Maria use to accomplish this?

TODO why?

https://docs.getdbt.com/docs/build/hooks-operations


## snapshot used for aggregation data tracking 

Q: A data analytics company wants to keep track of changes in their sales data, specifically in the orders table. They want to see how the total order value and the number of items per order have changed over time. Which of the following statements about using snapshots in dbt is correct?

A: To use snapshots, the company needs to write a select statement that retrieves the desired data and wrap it in a snapshot block in a .sql file located in the "snapshots" directory.



## DBT hooks execution order 

https://docs.getdbt.com/docs/build/hooks-operations

## DBT adapter 

These SQL-speaking platforms are collectively referred to as data platforms. dbt connects with data platforms by using a dedicated adapter plugin for each. Plugins are built as Python modules that dbt Core discovers if they are installed on your system. Read What are Adapters for more info.



## DBT core how to locate the connection 

- `dbt_project.yml` has profile key 
- `profiles.yml` includes are available connections details



## DBT Snapshot table name 

, the analyst wants to capture changes to the "name" table, so the correct command would be `dbt snapshot --select name_snapshot`, assuming the snapshot is named "name_snapshot" in their project. 


## DBT version2 

extensible / and good for add new features in the future
https://docs.getdbt.com/faqs/Project/why-version-2


## DBT best practice 

Dbt Recommends Using A Simple Select Statement At The End To Allow For Easy Troubleshooting 