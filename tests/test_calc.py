"""
Test the data module.
Author: Wolf Paulus (wolf@paulus.com)
"""
from unittest import TestCase
from calc import csv_to_dataframe, analyze
from os.path import exists, join
from os import remove


class Test(TestCase):
    def test_cvs_to_dataframe(self):
        """
            converting a staticly stored csv file and pooking around a little
        """
        with open("tests/net.cvs", "r") as f:
            csv = f.read()
        df = csv_to_dataframe(csv)
        assert len(df)
        assert df["Date"].dtype == "object"
        assert df["Adj Close"].dtype == "float64"
        assert len(df.columns) == 2
        rows = len(df)
        lines = csv.count("\n")
        assert rows == lines

    def test_analyze(self):
        assert 1 == 2
