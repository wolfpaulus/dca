"""
Test the app module.
Author: Wolf Paulus (wolf@paulus.com)
"""

from unittest import TestCase
from streamlit.testing.v1 import AppTest


class Test(TestCase):
    """
    Find out more about how to test streamlit apps:
    https://docs.streamlit.io/library/api-reference/app-testing
    """

    def test_ui_title_and_header(self):
        at = AppTest.from_file("./src/app.py")
        at.run()

        assert at.title[0].value.startswith("Automatic Investing")
        assert at.subheader[0].value.startswith(
            "Comparing Investing Strategys")
        assert not at.exception
