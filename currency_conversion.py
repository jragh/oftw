import pandas_datareader.data as web
import datetime
import pandas as pd

import polars as pl

import os


def get_historical_exchange_rates(start_date="2020-01-01", end_date=None):

    postgres_uri = os.getenv('POSTGRES_URI_LOCATION')
    
    ### Fetch historical GBP to USD exchange rates from FRED.
    if end_date is None:
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")

    ### Will bring in the conversions between the different currencies converting back to USD ###
    try:

        currency_total = []

        for currency in ['DEXUSUK', 'DEXCAUS', 'DEXUSAL', 'DEXUSEU', 'DEXSIUS', 'DEXSZUS']:
            df = web.DataReader(currency, "fred", start_date, end_date)

            # Create a new DataFrame with all dates in the range
            date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')

            df_filled = df.reindex(date_range).bfill()
            df_filled.reset_index(inplace=True)
            df_filled.rename(columns={'index': 'DATE'}, inplace=True)
            df_filled.rename(columns={currency: 'CURRENCY RATE'}, inplace=True)

            df_filled['CURRENCY'] = currency

            currency_total.append(df_filled)

            # conversion_rates = {
                
            #     'USD': 1.0,
            #     'GBP': polars_df_filled['DEXUSUK'],
            #     'CAD': 1/polars_df_filled['DEXCAUS'],  # Inverting for division
            #     'AUD': polars_df_filled['DEXUSAL'],
            #     'EUR': polars_df_filled['DEXUSEU'],
            #     'SGD': 1/polars_df_filled['DEXSIUS'],  # Inverting for division
            #     'CHF': 1/polars_df_filled['DEXSZUS']   # Inverting for division

            # }

            # polars_df_filled = polars_df_filled.with_columns()

        final_pandas_currency = pd.concat(currency_total, ignore_index=True)

        #### Polars Conversion, Write to postgres database ####
        polars_final_currency = pl.from_dataframe(final_pandas_currency)

        polars_final_currency.write_database(table_name='oftw_currency_conversion',
                                             connection=postgres_uri,
                                             engine='adbc',
                                             if_table_exists='replace')

    except Exception as e:
        print("Error fetching data:", e)

get_historical_exchange_rates("2014-03-01", "2025-02-28")