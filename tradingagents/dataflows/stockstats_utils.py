import pandas as pd
import yfinance as yf
from stockstats import wrap
from typing import Annotated
import os
import requests
import urllib3
from .config import get_config


class StockstatsUtils:
    @staticmethod
    def get_stock_stats(
        symbol: Annotated[str, "ticker symbol for the company"],
        indicator: Annotated[
            str, "quantitative indicators based off of the stock data for the company"
        ],
        curr_date: Annotated[
            str, "curr date for retrieving stock price data, YYYY-mm-dd"
        ],
        data_dir: Annotated[
            str,
            "directory where the stock data is stored.",
        ],
        online: Annotated[
            bool,
            "whether to use online tools to fetch data or offline tools. If True, will use online tools.",
        ] = False,
    ):
        df = None
        data = None

        if not online:
            try:
                data = pd.read_csv(
                    os.path.join(
                        data_dir,
                        f"{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
                    )
                )
                df = wrap(data)
            except FileNotFoundError:
                raise Exception("Stockstats fail: Yahoo Finance data not fetched yet!")
        else:
            # Get today's date as YYYY-mm-dd to add to cache
            today_date = pd.Timestamp.today()
            curr_date = pd.to_datetime(curr_date)

            end_date = today_date
            start_date = today_date - pd.DateOffset(years=15)
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")

            # Get config and ensure cache directory exists
            config = get_config()
            os.makedirs(config["data_cache_dir"], exist_ok=True)

            data_file = os.path.join(
                config["data_cache_dir"],
                f"{symbol}-YFin-data-{start_date}-{end_date}.csv",
            )

            if os.path.exists(data_file):
                data = pd.read_csv(data_file)
                data["Date"] = pd.to_datetime(data["Date"])
            else:
                # Handle SSL certificate issues
                disable_ssl = os.getenv("DISABLE_SSL_VERIFY", "false").lower() == "true"
                
                if disable_ssl:
                    # Disable SSL warnings and verification for development
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    requests.packages.urllib3.disable_warnings()
                    
                    # Create a session with SSL verification disabled
                    session = requests.Session()
                    session.verify = False
                    
                    # Monkey patch yfinance to use our session
                    import yfinance.utils as yf_utils
                    yf_utils.get_json = lambda url, proxy=None, headers=None: session.get(url, headers=headers, proxies=proxy).json()

                try:
                    data = yf.download(
                        symbol,
                        start=start_date,
                        end=end_date,
                        multi_level_index=False,
                        progress=False,
                        auto_adjust=True,
                    )
                    
                    # Validate downloaded data
                    if data.empty:
                        raise Exception(f"No data retrieved for {symbol}")
                    
                    data = data.reset_index()
                    data.to_csv(data_file, index=False)
                    
                except Exception as e:
                    raise Exception(f"Failed to download data for {symbol}: {str(e)}")

            # Validate data before processing
            if data.empty or len(data) == 0:
                raise Exception(f"Empty dataset for {symbol}")
            
            # Ensure required columns exist (after reset_index, we should have Date column)
            required_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise Exception(f"Missing required columns for {symbol}: {missing_columns}")

            df = wrap(data)
            df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
            curr_date = curr_date.strftime("%Y-%m-%d")

        try:
            # Trigger stockstats to calculate the indicator
            df[indicator]
        except Exception as e:
            raise Exception(f"Failed to calculate indicator {indicator} for {symbol}: {str(e)}")

        # Find matching rows for the current date
        matching_rows = df[df["Date"].str.startswith(curr_date)]

        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            return indicator_value
        else:
            # Check if it's a weekend/holiday or if data is genuinely missing
            if len(df) > 0:
                latest_date = df["Date"].max()
                return f"N/A: Not a trading day (weekend or holiday). Latest data: {latest_date}"
            else:
                return "N/A: No data available for this symbol"
