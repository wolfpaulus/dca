"""
    Using Pandas to compare Investing Strategies
    Wolf Paulus
"""
from datetime import date
from json import dump
from pandas import DataFrame, to_datetime, to_datetime
from log import logger
from requests import get


def download_data(ticker: str) -> tuple[bool, dict | str]:
    """
    Download historic data for a given stock ticker symbol from Nasdaq.com.
    Details about it: https://www.nasdaq.com/market-activity/quotes/historical

    Args:
        ticker: str - Stock ticker symbol, e.g., 'AAPL' for Apple Inc.

    Returns:
        bool - True if the data was downloaded successfully, False otherwise.
        dict | str - dictionary, 1st item contains the header, or an error message.
    """
    ticker = ticker.upper()
    today = date.today()
    start = str(today.replace(year=today.year - 5))
    base_url = "https://api.nasdaq.com"
    path = f"/api/quote/{ticker}/historical?assetclass=stocks&fromdate={start}&limit=9999"
    try:
        logger.debug(f"Downloading data for ticker: {ticker}")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0"
        }
        response = get(base_url + path, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                return True, data
            else:
                logger.warning(str(data.get("status")))
                return False, str(data.get("status"))
        else:
            logger.warning(f"{response.geterror()} {response.getcode()}")
            return False, f"{response.geterror()} {response.getcode()}"
    except Exception as e:
        logger.error(f"This error occurred: {e} : {ticker}")
        return False, f"An error occurred: {e}"


def json_to_dataframe(data: dict) -> DataFrame:
    """
    Converts a dict to a DataFrame, also removing not needed columns.
    Original columns:  date, close, volume, open, high, low
    Remaining columns: date, close
    Args:
        data: dict, important info at data/tradesTable/rows

    Returns:
        DataFrame - The DataFrame.
    """
    r = data.get("data", {}).get("tradesTable", {}).get("rows", [])
    return DataFrame(r).drop(["volume", "open", "high", "low"], axis="columns")


def analyze(df: DataFrame) -> DataFrame:
    """
    Analyze the stock data to simulate two investment strategies:
    - Fixed share number (1 share per week)
    - Fixed weekly amount

    Args:
        df: DataFrame - The stock data.

    Returns:
        DataFrame - The processed DataFrame with additional columns:
        Shares_FS, Paid_FS, Value_FS, Shares_FA, Paid_FA, Value_FA
    """
    # Reverse the dataframe since, we are receiving it newest 1st
    # Insert a 'Weekday' column, to find the first trading day of each week
    # Remove '$' symbol from closing price and convert to float
    df = df.iloc[::-1]
    df["Weekday"] = to_datetime(df["date"]).dt.weekday
    df = df[(df.shift(1).Weekday > df.Weekday)]
    df["date"] = to_datetime(df["date"]).dt.strftime('%Y-%m-%d')
    df["close"] = df["close"].replace("\\$", "", regex=True).astype(float)
    # Strategy: Fixed share number (1 share per week)
    # Shares FQ: Shares bought with a fixed quantity
    # Invested FQ: Money invested with a fixed quantity
    # Value FQ: Value of the investment with a fixed quantity
    df["Shares FQ"] = 1
    df["Shares FQ"] = df["Shares FQ"].cumsum()
    df["Invested FQ"] = df["close"].cumsum()
    df["Value FQ"] = df["Shares FQ"] * df["close"]

    # Strategy: Fixed weekly amount
    # Shares DCA: Shares bought with a fixed weekly amount
    # Invested DCA: Money invested with a fixed weekly amount
    # Value DCA: Value of the investment with a fixed weekly amount
    wa = df.iloc[-1]["Invested FQ"] / df.iloc[-1]["Shares FQ"]  # Weekly amount
    df["Shares DCA"] = (wa / df["close"]).cumsum()
    df["Invested DCA"] = wa
    df["Invested DCA"] = df["Invested DCA"].cumsum()
    df["Value DCA"] = df["Shares DCA"] * df["close"]

    # Clean up the DataFrame
    df = df.drop(["Weekday"], axis="columns")
    df = df.reset_index(drop=True)
    return df


if __name__ == "__main__":
    ticker = "NET"
    ok, data = download_data(ticker)
    with open("tests/net.json", "w") as f:
        dump(data, f)
    if ok:
        df = analyze(json_to_dataframe(data))
        row = df.iloc[-1]
        print(df)
        with open("src/result.md", "r") as f:
            # injecting the result into the markdown file
            md = f.read()
            x = md.format(
                ticker=ticker,
                sq_shares=row["Shares FQ"],
                sq_invested=row["Invested FQ"],
                sq_value=row["Value FQ"],
                sq_gain=row["Value FQ"] - row["Invested FQ"],
                sq_annual=(row["Value FQ"] - row["Invested FQ"])
                / row["Invested FQ"]
                * 100
                / 5,
                wa=row["Invested FQ"] / row["Shares FQ"],
                dca_shares=row["Shares DCA"],
                dca_invested=row["Invested DCA"],
                dca_value=row["Value DCA"],
                dca_gain=row["Value DCA"] - row["Invested DCA"],
                dca_annual=(row["Value DCA"] - row["Invested DCA"])
                / row["Invested DCA"]
                * 100
                / 5,
            )
            print(x)
    else:
        print(f"No data downloaded, {data}")
