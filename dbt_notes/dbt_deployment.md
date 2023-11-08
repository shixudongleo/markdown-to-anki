# DBT Deployment


## what is the key components for Environment level data project

1. dbt version 
2. git branch 
3. data location 

## What is a dbt cloud job

DBT deployment (level 1 ) -> DBT Jobs (level under dbt deployment)

DBT Jobs can have 
- sequence of dbt commend: dbt run / dbt test / dbt build 
- scheduled or triggered 


## What is the dbt cloud run 

DBT deployment (level 1 ) -> DBT Jobs (level under dbt deployment) -> (level under dbt job)

- run is an instantiation of DBT Job, you can see the run status in realtime
- once done, you can check the result (log) and artifacts (docs / DW tables,views)



## what is the two most common deployment architectures

One Trunk Promotion (direct)

feature branch directly to main/master branch 


Many Trunks Promotion (indirect)


1. feature branch directly to intermediate branch for more testing 
2. and then intermediate branch merge to main/master branch 
