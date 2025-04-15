import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Accra Rental Trends", layout="wide")

st.title("📊 Accra Rental Trends Dashboard")

df = pd.read_csv("data/processed/clean_rentals.csv")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Price Distribution")
    fig1 = px.histogram(df, x="price", nbins=50)
    st.plotly_chart(fig1)

with col2:
    st.subheader("Price by Neighborhood")
    fig2 = px.box(df, x="location", y="price")
    st.plotly_chart(fig2)

st.subheader("Average Rent by Bedrooms")
avg_price = df.groupby("bedrooms")["price"].mean().reset_index()
fig3 = px.bar(avg_price, x="bedrooms", y="price", title="Avg Price per Bedroom Count")
st.plotly_chart(fig3)
