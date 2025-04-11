import pandas_datareader.data as web
import datetime
import pandas as pd

import polars as pl

import os

import traceback


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

        final_pandas_currency = pd.concat(currency_total, ignore_index=True)

        #### Polars Conversion, Write to postgres database ####
        polars_final_currency = pl.from_dataframe(final_pandas_currency)

        #### Setting up Currency Short for join onto other tables ####
        currency_short = {

            'DEXUSUK': 'GBP',
            'DEXCAUS': 'CAD',
            'DEXUSAL': 'AUD',
            'DEXUSEU': 'EUR',
            'DEXSIUS': 'SGD',
            'DEXSZUS': 'CHF'

        }

        polars_final_currency = polars_final_currency.with_columns(pl.col('CURRENCY').replace_strict(currency_short).alias('CURRENCY SHORT'))

        #### Conversion Rates Dictionary ####
        # conversion_rates = {
        #     'USD': 1.0,
        #     'GBP': polars_final_currency['CURRENCY RATE'],
        #     'CAD': 1/polars_final_currency['CURRENCY RATE'],  # Inverting for division
        #     'AUD': polars_final_currency['CURRENCY RATE'],
        #     'EUR': polars_final_currency['CURRENCY RATE'],
        #     'SGD': 1/polars_final_currency['CURRENCY RATE'],  # Inverting for division
        #     'CHF': 1/polars_final_currency['CURRENCY RATE']   # Inverting for division
        # }

        ## polars_final_currency = polars_final_currency.with_columns(pl.col('CURRENCY SHORT').replace(conversion_rates).alias("CURRENCY RATE FINAL"))

        polars_final_currency.write_database(table_name='oftw_currency_conversion',
                                             connection=postgres_uri,
                                             engine='adbc',
                                             if_table_exists='replace')

    except Exception as e:
        print("Error fetching data:", traceback.format_exc())

get_historical_exchange_rates("2014-03-01", "2025-03-01")