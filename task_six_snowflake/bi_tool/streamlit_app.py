import streamlit as st
from snowflake.snowpark.context import get_active_session

st.title("✈️ Airline Performance Dashboard")
session = get_active_session()

df = session.table("AIRLINE_DWH.ANALYTICS.FLIGHT_ANALYTICS_MART").to_pandas()

st.bar_chart(data=df, x="AIRPORT_NAME", y="TOTAL_FLIGHTS")
st.dataframe(df)
