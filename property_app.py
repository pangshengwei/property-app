import pandas as pd
import streamlit as st
import altair as alt
from utils import *

df = pd.read_csv('ura_private_condo_2016_2021_all_districts.csv')
df['top_date'] = df.Tenure.apply(lambda x: get_top_date(x))
df['floor'] = df['Floor Level'].apply(lambda x: get_floor(x))
df['year'] = df['Date of Sale'].apply(lambda x: get_year(x))
cols = {'Area (Sqft)': 'sqft', 'Unit Price ($psf)': 'psf', 'Price ($)': 'price', 'Postal District': 'district', 'Project Name': 'name'}
df = df.rename(columns=cols)[df['Price ($)'].notnull()].reset_index(drop=True)

### APP UI ###
st.header('Aggregated Property Transactions')
"""
This chart provides a high level overview of property prices across 2016-2021.
It is first filtered by your criteria before grouped by year. For example, you can search
for how all properties in districts 9 and 10 performed. 
"""
top_date = st.sidebar.slider("Top Date", 1950, 2021, 2000, 1)
floor = st.sidebar.slider("Floor", 0, 50, 1)
area = st.sidebar.slider("Area", 0, 2000, 1)
psf = st.sidebar.slider("PSF", 0, 3000, 1)
districts = st.multiselect("Choose districts", list(df.index), [20])
appreciated = st.sidebar.slider("Min Appreciation", -100, 200, 0)
num_transactions = st.sidebar.slider("Number of Transaction", 0, 1000, 0)
filtered_df = df[(df.floor >= floor) & (df.top_date >= top_date) & (df.sqft >= area) & (df.psf >= psf) & df.district.isin(districts)]
prices = filtered_df.groupby('year').median().price.reset_index()
chart = alt.Chart(prices).mark_line().encode(
            alt.X('year', scale=alt.Scale(zero=False), axis=alt.Axis(format="d")),
            alt.Y('price', scale=alt.Scale(zero=False)),
        )
p1, p2, n = prices.price[0], prices.price[5], len(filtered_df)
appreciation = round((p2 - p1) / p1, 3) * 100
st.write(chart)
st.write(pd.DataFrame([{'Num Transactions': n, '2016 Price:': p1, '2021 Price': p2, 'Appreciation': round(appreciation, 3)}]))

st.header('List Of Condos By Filters')
"""
This list shows all properties that have met your your criteria, sorted by their appreciation.
"""
values = []
stats = {'district': 'mean', 'top_date': 'mean', 'floor': 'mean', 'psf': 'mean', 'No. of Units': 'count', 'price': 'mean'}
grouped = filtered_df.groupby(['name', 'year']).agg(stats)
for name in filtered_df.name.unique():
    p1 = grouped.loc[name].iloc[0].price
    p2 = grouped.loc[name].iloc[-1].price
    app = (p2 - p1) / p1 * 100
    n = grouped.loc[name]['No. of Units'].sum()
    floor = grouped.loc[name].floor.mean()
    psf = grouped.loc[name].psf.mean()
    d = grouped.loc[name].district.mean()
    values.append({'name': name, 'appreciation': app, 'num_transactions': n, 'avg_psf': psf, 'district': d})

agg = pd.DataFrame(values)
agg = agg[(agg.appreciation > appreciated) & (agg.num_transactions > num_transactions)]
agg = agg.sort_values('appreciation', ascending=False).reset_index(drop=True)
st.write(agg)

st.header('Condo Price Comparer')
names = st.multiselect("Choose project names", list(df.name.unique()), ['SKY VUE'])
for name in names:
    st.write(name)
    project = df[(df.name == name) & (df.floor >= floor) & (df.top_date >= top_date) & (df.sqft >= area) & (df.psf >= psf)]
    prices = project.groupby('year').median().price.reset_index()
    chart = alt.Chart(prices).mark_line().encode(
        alt.X('year', scale=alt.Scale(zero=False), axis=alt.Axis(format="d")),
        alt.Y('price', scale=alt.Scale(zero=False)),
    )
    st.write(chart)

"""
Features
- 1) Single aggregate chart, filtered by - district, TOP, floor, 
- 2) Multi-chart, multi-select project name and same filters applied
- 3) Search condos that have appreciated or depreciated > x %
- 3) Deploy it 
- 4) Repeat (1) and (2) for HDB
- 5) 

# filter certain transactions
- 2) Let users plot multiple properties side by side for comparison, with equal filters applied
- 3) Show (1) and (2) by geo-map 
"""