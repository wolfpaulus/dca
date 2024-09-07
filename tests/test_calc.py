"""
Test the data module.
Author: Wolf Paulus (wolf@paulus.com)
"""

from calc import json_to_dataframe, analyze
from json import load
from pandas import to_datetime
import pytest


@pytest.fixture()
def data():
    with open("tests/net.json", "r") as f:
        data_dict = load(f)
    return data_dict


def test_data(data):
    assert len(data)


def test_json_to_dataframe(data):
    """
        converting a staticly stored csv file and pooking around a little
    """
    df = json_to_dataframe(data)
    assert len(df)
    assert len(df.columns) == 2
    records = data.get("data").get("totalRecords")
    assert records == len(df.index)


def test_analyze(data):
    df = analyze(json_to_dataframe(data))
    assert df["date"].dtype == "object"
    assert df["close"].dtype == "float64"
    # was there a trade happening every week?
    # distance between days should be less than 13
    df["d1"] = to_datetime(df["date"])
    df["d0"] = df["d1"].shift(1)
    df["delta"] = df["d1"] - df["d0"]
    print(df["delta"].max().days)
    assert df["delta"].max().days < 13
    assert df["delta"].min().days > 2
