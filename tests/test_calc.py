"""
Test the data module.
Author: Wolf Paulus (wolf@paulus.com)
"""

from calc import csv_to_dataframe, analyze
from pandas import to_datetime
import pytest


@pytest.fixture()
def csv():
    with open("tests/net.cvs", "r") as f:
        data_string = f.read()
    return data_string


def test_data(csv):
    assert len(csv)


def test_cvs_to_dataframe(csv):
    """
        converting a staticly stored csv file and pooking around a little
    """
    df = csv_to_dataframe(csv)
    assert len(df)
    assert df["Date"].dtype == "object"
    assert df["Adj Close"].dtype == "float64"
    assert len(df.columns) == 2
    rows = len(df)
    lines = csv.count("\n")
    assert rows == lines


def test_analyze(csv):
    df = analyze(csv_to_dataframe(csv))
    # was there a trade happening every week?
    # distance between days should be less than 13
    df["d1"] = to_datetime(df["Date"])
    df["d0"] = df["d1"].shift(1)
    df["delta"] = df["d1"] - df["d0"]
    print(df["delta"].max().days)
    assert df["delta"].max().days < 13
