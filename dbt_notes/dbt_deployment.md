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


- Developer branch off of the main branch.
- After developing, they open a pull / merge request.
- This kicks off a CI job that builds and tests the dbt code in a temporary PR schema.
- After code review and CI checks pass, the code can merged into main.

![dbt_deployment_trunk1](dbt_deployment_trunk1.png)



Many Trunks Promotion (indirect)


1. feature branch directly to intermediate branch for more testing 
2. and then intermediate branch merge to main/master branch 

- Developer branch off of the qa branch
- After developing, they open a pull / merge request against the qa branch
- This kicks off a CI job that builds and tests the dbt code in a temporary PR schema.
- After code review and CI checks pass, the code can merged into qa.
- The core owner then manages the merging of code from qa to the main branch through another CI process.

![dbt_deployment_trunk2](dbt_deployment_trunk2.png)


Pros and Cons 

- Trunk1 is the recommended approach for most use-cases as it allows changes to code to be quickly moved to production, with confidence that they can be trusted.
- Trunk2 might slow down the time for getting new features into production.

https://www.getdbt.com/blog/adopting-ci-cd-with-dbt-cloud/