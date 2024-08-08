"""
    Using Pandas to compare Investing Strategies
    Wolf Paulus
"""
from urllib.request import Request, urlopen
from datetime import datetime, timedelta
from calendar import timegm
from io import StringIO
from pandas import read_csv, DataFrame, to_datetime
from log import logger


def download_data(ticker: str) -> tuple[bool, str]:
    """
    Download historic data for a given stock ticker symbol from Yahoo Finance.
    Details about Yahoo Finance data: https://help.yahoo.com/kb/SLN2311.html

    Args:
        ticker: str - Stock ticker symbol, e.g., 'AAPL' for Apple Inc.

    Returns:
        bool - True if the data was downloaded successfully, False otherwise.
        str - comma-separated values (CSV) string with the stock data, or an error message.
    """
    ticker = ticker.upper()
    today = datetime.now()
    epoch_from = timegm((today - timedelta(days=5 * 365)).timetuple())
    epoch_to = timegm(today.timetuple())
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={
        epoch_from}&period2={epoch_to}&interval=1d&events=history&includeAdjustedClose=true"

    try:
        logger.debug(f"Downloading data for ticker: {ticker}")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0",
        }
        req = Request(url, headers=headers)
        with urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                return True, response.read().decode("utf-8")
            else:
                logger.warn(f"{response.geterror()} {response.getcode()}")
                return False, f"{response.geterror()} {response.getcode()}"
    except Exception as e:
        logger.error(f"This error occurred: {e}")
        return False, f"An error occurred: {e}"


def csv_to_dataframe(csv: str) -> DataFrame:
    """
    Convert a CSV string to a DataFrame, also removing not needed columns.
    Args:
        csv: str - The CSV string.

    Returns:
        DataFrame - The DataFrame.
    """
    return read_csv(StringIO(csv)).drop(
        ["Open", "High", "Low", "Close", "Volume"], axis="columns"
    )


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
    # Insert a 'Weekday' column, to find the first trading day of each week
    df["Weekday"] = to_datetime(df["Date"]).dt.weekday
    df = df[(df.shift(1).Weekday > df.Weekday)]

    # Strategy: Fixed share number (1 share per week)
    df["Shares FQ"] = 1
    df["Shares FQ"] = df["Shares FQ"].cumsum()
    df["Invested FQ"] = df["Adj Close"].cumsum()
    df["Value FQ"] = df["Shares FQ"] * df["Adj Close"]

    # Strategy: Fixed weekly amount
    wa = df.iloc[-1]["Invested FQ"] / df.iloc[-1]["Shares FQ"]  # Weekly amount

    df["Shares DCA"] = (wa / df["Adj Close"]).cumsum()
    df["Invested DCA"] = wa
    df["Invested DCA"] = df["Invested DCA"].cumsum()
    df["Value DCA"] = df["Shares DCA"] * df["Adj Close"]

    # Clean up the DataFrame
    df = df.drop(["Weekday"], axis="columns")
    df = df.reset_index(drop=True)
    return df


if __name__ == "__main__":
    ticker = "AAPL"
    ok, data = download_data(ticker)
    with open("tests/net.cvs", "w") as f:
        f.write(data)
    if ok:
        df = analyze(csv_to_dataframe(data))
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
