# DBT Notes

## `env_var` what is environment variables in DBT

The `env_var` function can be used to incorporate Environment Variables from the system into your dbt project. 

1. `env_var` function can be used in your `profiles.yml` file, the `dbt_project.yml` file, the `sources.yml` file, your `schema.yml` files, and in `model .sql` files. Essentially `env_var` is available anywhere dbt processes jinja code.
2. use jinja to reference the environment variables `"{{ env_var('DBT_USER') }}"`, `'{{ env_var('DBT_USER') }}'`
3. if value type is required, e.g. int, use jinja filter to cast data type `"{{ env_var('DBT_USER') | int }}"`
4. pass `env_var` default value: `"{{ env_var('DBT_MATERIALIZATION', 'view') }}"`


docs: https://docs.getdbt.com/reference/dbt-jinja-functions/env_var

## special environment variables in DBT 

Secret 

1. prefix with `DBT_ENV_SECRET_`
2. reference value with `{{ env_var('DBT_ENV_SECRET_xxx) }}`
3. key features of secret env variable in dbt 
    - allowed only in `profiles.yml` `packages.yml`
    - disallowed in `dbt_projects.yml`, model sql to avoid ingest secret values to data warehouse
    - log output of secret is replace with `*****`


Custom Metadata

1. prefix with `DBT_ENV_CUSTOM_ENV_`
2. reference values with `{{ dbt_metadata_envs }}`
3. examples

```
$ DBT_ENV_CUSTOM_ENV_MY_FAVORITE_COLOR=indigo DBT_ENV_CUSTOM_ENV_MY_FAVORITE_NUMBER=6 dbt compile

-- {{ dbt_metadata_envs }}
-- {'MY_FAVORITE_COLOR': 'indigo', 'DBT_ENV_CUSTOM_ENV_MY_FAVORITE_NUMBER': '6'}
```


## `var` what is Variables in DBT

dbt provides a mechanism, variables, to provide data to models for compilation. 
Variables can be used to configure `timezones,` avoid `hardcoding table names` or otherwise provide data to models to configure how they are compiled.

`Variables` can be passed from your `dbt_project.yml` file into models during compilation.

1. define variables in `dbt_project.yml`
2. reference var with `{{ var('var_name') }}` in models 
3. default value: The `var("event_type", "activation")` function takes an optional second argument as default
4. examples 

```
# dbt_project.yml
name: my_dbt_project
version: 1.0.0
vars:
  event_type: activation

-- use variable defined in dbt_project.yml
select * from events where event_type = '{{ var("event_type", "xxx") }}'ß
```

docs: https://docs.getdbt.com/reference/dbt-jinja-functions/var


## Variables precedence 

where variables can be defined 

1. command line option `--vars json_str`
2. in `dbt_project.yml`, `vars` block 
3. package's `dbt_project.yml`, `vars` block
4. default value, 2nd argument of `var` function


The order of precedence for variable declaration is as follows (highest priority first):

1. The variables defined on the command line with --vars.
2. The package-scoped variable declaration in the `root dbt_project.yml` file
3. The global variable declaration in the `root dbt_project.yml` file
4. If this node is defined in a package: variable declarations in that package's dbt_project.yml file
5. The variable's default argument (if one is provided)



