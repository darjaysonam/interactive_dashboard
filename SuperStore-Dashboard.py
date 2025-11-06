import streamlit as st 
import plotly.express as px
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import os
import sys
st.write("Python executable path:", sys.executable)
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="RetailDash", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: DrukMart-Store EDA")

st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

#uploading data
f1 = st.file_uploader(":file_folder: Upload a file", type = (["csv", "txt", "xlsx", "xls"]))
if f1 is not None:
    filename=f1.name
    st.write(filename)
    df=pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    os.chdir(r"C:\Users\Darjay\RetailStore-Dashboard")
    df=pd.read_csv("superstore_dataset2011-2015.csv", encoding = "ISO-8859-1" )

#Convert order data properly as it contains different date format (day first)
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')

#Getting the min and max date
startDate = df['Order Date'].min()
endDate = df['Order Date'].max()

col1, col2 = st.columns((2))
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

#Create SideFilter Pane, Filtering data based on region, location etc
st.sidebar.header("Choose your filter: ")
#Create for Region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region: # if we didnt select any region, we store all data of df into df2 
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)] # If we select any specific region, that info will be stored into "region". 
#Create for State
state = st.sidebar.multiselect("Pick your State", df2['State'].unique())
if not state: # if not selected, we carryforward df2 info into 'df3'
    df3 = df2.copy() 
else:
    df3 =df[df['State'].isin(state)]
#Create for City
city = st.sidebar.multiselect("Pick your City", df3['City'].unique())

#Filter the data based on region, state and city

if not region and not state and not city:
    filtered_df = df
elif not region and not state:
    filtered_df = df[df['City'].isin(city)]
elif not region and not city:
    filtered_df = df[df['State'].isin(state)]
elif not state and not city:
    filtered_df = df[df['Region'].isin(region)]
elif region and state:
    filtered_df = df3[df['Region'].isin(region) & df3['State'].isin(state)]
elif region and city:
    filtered_df = df3[df['Region'].isin(region) & df3['City'].isin(city)]
elif state and city:
    filtered_df = df3[df['State'].isin(state) & df3['City'].isin(city)]

#Showing sum of the sales groupby category
category_df = filtered_df.groupby(by = ['Category'], as_index=False)['Sales'].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = 'Category', y = 'Sales', text=['${:,.2f}'.format(x) for x in category_df['Sales']], 
                 template = 'seaborn')
    st.plotly_chart(fig, use_container_width =True, height = 200)
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = 'Sales', names = 'Region', hole = 0.5)
    fig.update_traces(text = filtered_df['Region'], textposition = 'outside')
    st.plotly_chart(fig, use_container_width = True)

#Creating downloadable category sales and regionwise sales CSV data
col1, col2 = st.columns(2)
with col1:
    with st.expander('Category_ViewData'):
        #st.write(category_df.style.background_gradient(cmap='Blues')) >>>>> this code just dont seem to work, no idea!!
        st.dataframe(category_df.style.set_properties(**{'background-color': 'lightblue'}))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data', data=csv, file_name= "Category.csv", mime = 'text/csv', 
                            help = 'Click to download the data as a CSV file')
with col2:
    with st.expander('Region_ViewData'):
        region = filtered_df.groupby(by = ['Region'], as_index=False)['Sales'].sum()
        #st.write(region.style.background_gradient(cmap='Oranges'))>>>>> this code just dont seem to work, no idea!!
        st.dataframe(region.style.set_properties(**{'background-color': 'lightgreen'}))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data', data=csv, file_name= "Region.csv", mime = 'text/csv', 
                            help = 'Click to download the data as a CSV file')

#Time Series Analysis of Sales Data
filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M')
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y : %b'))['Sales'].sum()).reset_index()
fig2 = px.line(linechart, x = 'month_year', y = 'Sales', labels = {'Sales': 'Amount'},height =500, width =1000, template='gridon')
st.plotly_chart(fig2, use_container_width=True)

#To create a downloadable csv file of the timeseries sales data
col1, col2 = st.columns(2)
with col1:
    with st.expander('TimeSeries Sales_ViewData'):
        #st.write(category_df.style.background_gradient(cmap='Blues')) >>>>> this code just dont seem to work, no idea!!
        st.dataframe(linechart.T.style.set_properties(**{'background-color': 'lightyellow'}))
        csv = linechart.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data', data=csv, file_name= "time_series_data.csv", mime = 'text/csv', 
                            help = 'Click to download the data as a CSV file')

#Create a tree based on region, category and sub-category
st.subheader('Hierarchical view of Sales using TreeMap')
fig3 = px.treemap(filtered_df, path = ['Region', 'Category', 'Sub-Category'], values = 'Sales', hover_data = ['Sales'], 
                color = 'Sub-Category')
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

#Segment wise and category wise sales
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values = 'Sales', names = "Segment", template = 'plotly_dark')
    fig.update_traces(text = filtered_df['Segment'], textposition = 'inside')
    st.plotly_chart(fig, use_container_width=True)
with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values = 'Sales', names = "Category", template = 'gridon')
    fig.update_traces(text = filtered_df['Category'], textposition = 'inside')
    st.plotly_chart(fig, use_container_width=True)

#To show specific columns data into a Tabular format
import plotly.figure_factory as ff 
st.subheader(':point_right: Monthwise Sub-category Sales Summary')
with st.expander("Summary_Table"):
    df_sample = df[0:5][['Region', 'State', 'City', 'Category', 'Sales', 'Profit', 'Quantity']]
    fig = ff.create_table(df_sample, colorscale = 'Cividis')
    st.plotly_chart(fig, use_container_width=True)

    #Month wise sub-category Table
    st.markdown('Monthwise sub-Category Table')
    filtered_df['month'] = filtered_df['Order Date'].dt.month_name()
    sub_category_Year= pd.pivot_table(data=filtered_df, values='Sales', index = ['Sub-Category'], columns = 'month')
    #st.write(category_df.style.background_gradient(cmap='Blues')) >>>>> this code just dont seem to work, no idea!!
    st.dataframe(sub_category_Year.style.set_properties(**{'background-color': 'lightblue'}))

# Create scatter plot for Sales vs Profit
data1 = px.scatter(
    filtered_df,
    x='Sales',
    y='Profit',
    size='Quantity',
    color='Category',  # optional
    hover_data=['Sub-Category']  # optional
)
data1.update_layout(
    title=dict(
        text="Relationship between Sales & Profit using Scatter Plot",
        font=dict(size=20)
    ),
    xaxis=dict(
        title=dict(text='Sales', font=dict(size=19))
    ),
    yaxis=dict(
        title=dict(text='Profit', font=dict(size=19))
    ),
    template='plotly_white'
)
st.plotly_chart(data1, use_container_width=True)

#To download an entire specific data sets
#with st.expander("view Data"):
    #st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap='Oranges')) >>>>> this code just dont seem to work, no idea!!

with st.expander("View Data"):
    try:
        st.dataframe(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap='Oranges'))
    except ImportError:
        st.warning("Matplotlib is missing — showing plain table instead.")
        st.dataframe(filtered_df.iloc[:500, 1:20:2])

#Somebody wants to download the entire DataSet
csv=df.to_csv(index = False).encode('utf-8')
st.download_button('Download Original DataSet from Here', data=csv, file_name='DataSet.csv', mime='text/csv')