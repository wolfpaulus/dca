"""
    Streamlit UI for the Automatic Investing project.
    Author: Wolf Paulus
"""
import streamlit as st
from log import logger
from calc import download_data, json_to_dataframe, analyze


def ui(default_ticker: str) -> None:
    """
    Streamlit UI for the Automatic Investing project.
    :param default_ticker: str
    :return: None
    """
    st.set_page_config(
        page_title="Automatic Investing",
        page_icon=":money_with_wings:"
    )
    st.title("Automatic Investing: A Path to Wealth Building Over Time")
    st.subheader("Comparing Investing Strategies over a 5 year term")
    ticker = st.text_input(
        "Enter a Ticker Symbol (e.g. for Cloudflare, Inc., enter NET, for Apple Inc., enter AAPL, etc.)",
        default_ticker,
        autocomplete="off").upper()
    st.write(
        """
        Automatic investing is a strategy for steadily building wealth,
        often implemented through Dollar Cost Averaging (DCA).
        This approach involves investing a fixed dollar amount at regular intervals,
        allowing investors to buy more shares when prices are low and fewer shares
        when prices are high.
        Alternatively, investors can opt to buy a fixed quantity of shares at regular
        intervals. Here we simulate both strategies using five years of
        historical stock market data, provided by Yahoo Finance.
        """
    )
    ok, data = download_data(ticker)
    if not ok:
        st.error(f"{data} : {ticker}", icon="💣")
    else:
        df = analyze(json_to_dataframe(data))
        st.caption(f"If you had bought share of {ticker} every week ...")
        st.dataframe(df[:])
        st.caption("Money invested and investment value over time:")
        st.line_chart(
            df, x="date", y=[
                "Invested FQ", "Value FQ", "Invested DCA", "Value DCA"])
        row = df.iloc[-1]
        try:
            with open("src/result.md", "r") as f:
                # injecting the result into the markdown file
                md = f.read()
                st.markdown(
                    md.format(
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
                )
        except OSError as err:
            logger.error(f"Error: {err}")
            st.error(f"Error: {err}")
        st.divider()
        st.write(
            """
            This program is for educational purposes only and does not constitute investment advice.\n
            Version 1.3.2 © 2024 [Wolf Paulus](https://wolfpaulus.com). All Rights Reserved.
            """
        )


if __name__ == "__main__":
    ui(default_ticker="NET")
