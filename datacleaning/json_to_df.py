import pandas as pd
import polars as pl

import os

## Create an environment variable that links to a databse location ##
## Database of choice: Postgresql ##
postgresql_path = os.environ['POSTGRES_URI_LOCATION']

oftw_pledges_df = pl.read_json('/Users/jragh/Documents/oftw/datacleaning/one-for-the-world-pledges.json')

oftw_payments_df = pl.read_json('/Users/jragh/Documents/oftw/datacleaning/one-for-the-world-payments.json')

print(oftw_pledges_df.head(25))

print(oftw_payments_df.head(25))

print(postgresql_path)


## Test Import into Postgresql database ## 
## Pledges Data Raw ##
oftw_pledges_df.write_database(
    table_name="oftw_pledges_raw",
    connection=postgresql_path,
    engine="adbc",
    if_table_exists='replace'
)

## Payments Data Raw ##
oftw_payments_df.write_database(
    table_name='oftw_payments_raw',
    connection=postgresql_path,
    engine='adbc',
    if_table_exists='replace'
)
