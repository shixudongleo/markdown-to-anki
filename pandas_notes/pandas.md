# Pandas

## pandas dataframe construction

- construct from dict (each key is the column name)
- construct from list of dict (list of rows, each row is a dict)
- construct from numpy
- empty rows with column `pd.DataFrame({'col_name': []})`

```
```

## pandas str procession

- `Series.str.xxx` has quite some easy to use methods

`s.str.contains / lower / upper / capitalize / split(with expand=True/False) /`


## DataFrame Manipulation

1. rename columns

- by rename all cols in order `df.columns = ['col1', 'col2', ...]`
- by rename some cols with mapping `new_df = df.rename(columns={mapping dict}) # or inplace=True)`

- index can be rename as well `new_df = df.rename(index={index name mapping dict})`


2. update cell, df.loc[s1, s2] = new val df.iloc[i, j] = new_val

3. add new column / update whole column / update part of the column with boolean index

```
# add new column 
df['new_col'] = series_obj

# update exisitng columns 
df['col'] = series_obj

# add new column with partial values 
df.iloc[idx, 'new_col'] = series_obj
```

4. str split and expand to multiple columns `df.str_col.str.split(';', expand=True)`

5. add new row `df.append(row_as_dict, ignore_index=True)` if not index provided

6. drop row / col

```
df.drop(columns=[col, col2], inplace=True)

df.drop(index= boolena index, inplace=True)
```

7. transformation with functional API: map/ applymap/ apply /replace

    - apply: apply function / lambda function to elementwise in column
    - applymap: apply function to dataframe cell
    - map: apply case when with a dictionary (if a value not exist in the map dict, return NaN)
    - replace: similar to map, case when with dictionary, (if a value not exist in the case when dict, don't do anything)

8. unique values
   - drop_duplicates reutrn DataFrame
   - unique return ndarray

Tips:

-  axis=0, row process / axis=1, col process


## DataFrame Select Columns & Rows by single key


1. 1D key/keys is for columns select  by default e.g. `df[key]   df[key_array]`
2. special case1: boolean array, return row of True rows  e.g. `df[bool_idx]`
3. special case2: slice of integer(integer index), return row of slice rows `df[0:5]`


## DataFrame select / subsetting by 2D keys

advanced key select with 2D keys

1. iloc integer location for selection with integer
2. loc index based selection  (label based selection)
3. ix can mix lable + integer keys


`df.loc[s1, s2] df.iloc[s1, s2]`

loc: s1 s2 must be index (row index/boolean_index or column index)

iloc: s1 s2 must be integer or integer array, slice

Tips:

- single value select in s1, s2 may return Series, instead of DataFrame object, suggest to use ['col'] instead of 'col' to return DataFrame for better Closure. e.g. `df[s1, ['col']] VS df[s1, 'col']`


## boolean index

1. `df.col ==, >= != value`
2. `df.col.isin([val1, val2])`
3. `df.col_str.str.contains('pattern') # option , regex=True/False`


boolean index operators: `| & ~`, multiple conditions must be with `(cond1) op (cond2)`


## Iterate rows and columns

```
# 1. iterate column by column 
for col, col_series in df.items():
    col
    col_series 
```

```
# 2. iterate row by row 
for index, row in df.iterrows():
    index 
    row

```

## DataFrame Sorting

```
# 1. sort index
df.set_index('xxx', inplace=Ture)
df.sort_index(acending=True/False)


# 2. sort by column
df.sort_values(by='col', ascending=True/False) 
df.sort_values(by=['col', 'col'], ascending=[True, False]) 
```

## dataframe stats

compute non NA rows count

```
df.count()
series.count()
```

column value distribution / counts

```
# count(*) group by colx 
df.colx.value_counts()
df.colx.value_counts(normalize=True)
```

column stats

```
df.colx.median / min / max / mean / std 
df.describe()
```

select distinct col_xxx

```
df.colx.unique() # return ndarray / array 

# use drop_duplicates if you want to return DataFrame
```


## DataFrame na value cleanning

1. data cleaning related to NaN
drop rows nan

```
df.dropna(axis='index', how='any'/ 'all')
df.dropna(axis='index', how='any'/ 'all', subset=['col1', 'col2'])

df.dropna(axis='columns', how='any'/ 'all')
```

2. find isna boolean index

```
df.isna()  # df.isnull() is alias for isna
df.colx.isna()
```

3. fill na default values

specific value to NaN and NaN to value

```
df.replace('None', np.nan, in_place=True)

df.fillna('0')
```

4. 数据类型处理

```
df.colx.astype(float/int/str)
```


## DataFrame groupby

groupby: DataFrame -> DataFrameGroupBy -> (agg) DataFrame

DataFrame groupby 之后， 再聚合，会在回到 DataFrame

```
# groupby 
df.groupby('single_col')
df.groupby(['col1', col2'])

# 取某个group
df.groupby(['col1', col2']).get_group(val) -> DataFrame

# 聚合函数（单个、多个聚合）
df.groupby().agg_func() -> Series e.g. min/ max / count / median / nunique ...

df.groupby().agg('mean') -> Series
df.groupby().agg(['mean']) -> DataFrame
df.groupby().agg(['mean', 'median']) -> DataFrame # apply multiple agg function 

# 自定义组聚合函数
df.groupby().get_group('group_value') # get records of a specific group 
df.groupby()['colx'].apply(lambda x: n  to 1 transformation in a group) # series -> scalar 

df.groupby()['colx', coly].agg(['min']) # apply min function to each group at each column, Series -> scalar
df.groupby()['colx', coly].apply(lambda x: n Datafrmae -> scalar) # apply to each group reduce to final result, DataFrame -> Scalar

# 保留 groupy key中为NA的记录
df.groupby(['col', 'col2'], dropna=False)
```


groupby functions list: https://pandas.pydata.org/docs/reference/groupby.html

## combine DataFrames horizontally (join)

horizontal combine (SQL Join)
merge > join (功能更强)

```
# join 默认使用index为join key
df1.set_index('key')
df2.set_index('key')
df1.join(df2, how='inner/left/right/outer', lsuffix='', rsuffix='')

# merge 
pd.merge(A, B, how='inner/left/right/outer', on =['key1', 'key2']) # A, B column names are same
pd.merge(A, B, how='inner/left/right/outer', left_on='lkey', right_on='rkey') # A, B column names are different


# merge options suffixes=('_x', '_y')
pd.merge(A, B, how='inner/left/right/outer', on =['key1', 'key2'], suffixes=('_left', '_right'))

# merge options indicator=True/False, for debug
pd.merge(A, B, how='inner/left/right/outer', on =['key1', 'key2'], indicator=True)


# merge left join with B is a single column key, you need to make B 2 columns so NA will appear
pd.merge(A, B, how='left', on='key')
```


## combine DataFrame vertically (concat / stack vertically)


concat > append (功能更强)

```
# concat
pd.concat([A, B], ignore_index=True, sort=False, join='inner/outer')

# ignore_index, 会重置index 
# join = inner 保留共有的列， outer: 保留所有列，缺失设置空


# append (deprecated and removed)

df1.append(df2)
df1.append([df2, df3])
```

## merge / concat examples

```
import numpy as np
import pandas as pd

movies = pd.DataFrame({
    'movie_id': [1, 2, 3, 5, 7],
    'title': ['t1', 't2', 't3', 't5', 't7'],
    'description': ['d1', 'd2', 'd3', 'd5', 'd7']
})

ratings = pd.DataFrame({
    'user_id': [1, 2, 7, 9, 11, 15],
    'movie_id': [1, 2, 4, 5, 6, 7],
    'title': ['t1', 't2', 't3', 't4', 't5', 't6'],
    'rating': [5, 4, 3, 2, 3, 1],
    'time': ['t1', 't2', 't4', 't4', 't1', 't3']
})

# merge
pd.merge(ratings, movies, how='left', on=['movie_id'], indicator=True)
pd.merge(ratings, movies, how='left', on=['movie_id'], suffixes=('', '_right'))

# join
ratings.join(movies, how='left', rsuffix='_right')

# concat
pd.concat([movies, ratings], ignore_index=True, sort=True)
```

## Dataframe SQL-like window fucntion

- add row_number
- rank
- window aggregation (7d moving avg)


dense rank

```
# dense rank across all 
row_rank = scores['score'].rank(method='dense', ascending=False).astype(int)

# dense rank within group
group_row_rank = scores.groupby('xx')['score'].rank(method='dense', ascending=False).astype(int)

```

reference:

- https://towardsdatascience.com/sql-window-functions-in-python-pandas-data-science-dc7c7a63cbb4
- https://stackoverflow.com/questions/17775935/sql-like-window-functions-in-pandas-row-numbering-in-python-pandas-dataframe



## Snippet1: Pandas connect to SQL with SqlAlchemy

load data with SQLAlchemy and process with pandas DataFrame API

`pd.read_sql()`

`df.to_sql()`
