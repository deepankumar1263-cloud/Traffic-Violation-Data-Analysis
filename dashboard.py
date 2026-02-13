# Creating DB Connection
from sqlalchemy import create_engine
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

user = 'root'
password = 'root'
host = 'localhost'
port = '3306'
database = 'traffic_violation'

@st.cache_resource
def get_engine():
    return create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

@st.cache_data(show_spinner=True)
def data_getter(_engine, query_string):
    return pd.read_sql(query_string, con=_engine)

# @st.cache_data(show_spinner=True)
# def comb_data(df1,df2,on_column):
#     df=pd.merge(df1,df2,how="inner",on=on_column)
#     return(df)

engine = get_engine()

df = data_getter(engine,"fact_table")
charges=data_getter(engine,"charges")


# Designing the dashboard
st.set_page_config(
page_title = "My-Dashboard",      
page_icon = "Active",          
layout = "wide",       
)
st.markdown("<h1 style='text-align:center;'>Traffic Violation Dashboard</h1>",unsafe_allow_html=True)
col1,col2,col3=st.columns(3)

with col1:
    # Fig 1
    plt.figure(figsize=(10,6))
    ax=sns.countplot(df[df["Accident"]==1]["DL State"],order=df[df["Accident"]==1]["DL State"].value_counts().head(10).index,palette="Blues_r")
    for con in ax.containers:
        ax.bar_label(container=con)
    plt.title("The Driving Licsense State with more Accidents")
    st.pyplot(plt)
    plt.clf()

    # Fig 2
    plt.figure(figsize=(10,8))
    ay=sns.countplot(df[df["Accident"]==1]["VehicleType"],order=df[df["Accident"]==1]["VehicleType"].value_counts().head(10).index,palette="Blues_r")
    for con in ax.containers:
        ay.bar_label(container=con)
    plt.title("Vehicle Type with more Accidents")
    st.pyplot(plt)
    plt.clf()

    # Fig 3
    plt.figure(figsize=(10,6))
    df["weekday"]=df["Date Of Stop"].dt.weekday
    sns.lineplot(x=df[df["Accident"]==1]["weekday"].value_counts().index,y=df[df["Accident"]==1]["weekday"].value_counts().values)
    plt.title("Number of Accidents in Weekdays")
    st.pyplot(plt)
    plt.clf()

    # Fig 4
    labels_=df[df["Accident"]==1]["Make"].value_counts().head(10).index
    values_=df[df["Accident"]==1]["Make"].value_counts().head(10).values
    fig = px.treemap(df.value_counts(), path=[labels_],values=values_, width=600, height=300,
                 title="Top 10 Make of car with Highest Accidents")
    colors=['#fae588','#f79d65','#f9dc5c','#e8ac65','#e76f51','#ef233c','#b7094c','#2bd496','#2bd4ba','#2bbad4']
    fig.update_layout(
        treemapcolorway = colors,
        margin = dict(t=30, l=25, r=25, b=25))
    st.plotly_chart(fig)

    # Fig 5
    plt.figure(figsize=(10,8))
    filter_list=df.columns[8:18].tolist()
    filter_list.insert(0,"All")
    selected_col=st.selectbox("Incidents",filter_list)
    temp=pd.merge(charges,df,how="inner",on="SeqID")
    if selected_col!="All":
        temp=temp.query(f"`{selected_col}`==1")
    else:
        pass
    ax=sns.countplot(temp["Charge"],order=temp["Charge"].value_counts().head(10).index)
    for con in ax.containers:
        ax.bar_label(container=con)
    plt.title(f"Laws related to {selected_col} Incident")
    st.pyplot(plt)
    plt.clf()

with col2:
    # Fig 6
    fig = px.imshow(df.iloc[:,8:18].corr(),height=700,width=600,title="Correlation b/w Binary Variables")
    st.plotly_chart(fig)

    # DF 1
    st.dataframe(df[df["Accident"]==1].groupby(["Latitude","Longitude"]).agg({"SeqID":"count"}).sort_values("SeqID",ascending=False).head(10).rename(columns={"SeqID":"Accident Counts"}))

with col3:
    # Fig 7
    state_list=df["Driver State"].unique().tolist()
    state_list.insert(0,"ALL")

    state=st.selectbox("Driver State",state_list)
    if state!="ALL":
        where_str=f"`Driver State`=='{state}'"
        temp=df.query(where_str)
    else:
        temp=df

    plt.figure(figsize=(10,6))
    ax=sns.countplot(temp[temp["Accident"]==1]["Driver City"],order=temp[temp["Accident"]==1]["Driver City"].value_counts().head(10).index,palette="Blues_r")
    for con in ax.containers:
        ax.bar_label(container=con)
    plt.title("Driver City with more Accident")
    st.pyplot(plt)
    plt.clf()

    # Fig 8
    plt.figure(figsize=(10,6))
    df["Year"]=df["Date Of Stop"].dt.year
    sns.lineplot(x=df[df["Accident"]==1]["Year"].value_counts().index,y=df[df["Accident"]==1]["Year"].value_counts().values)
    plt.title("Number of Accidents from 2012 to 2025")
    st.pyplot(plt)
    plt.clf()

    # Fig 9
    plt.figure(figsize=(10,8))
    ax=sns.countplot(df[df["Alcohol"]==1]["Driver City"],order=df[df["Alcohol"]==1]["Driver City"].value_counts().head(10).index,palette="Blues_r")
    for con in ax.containers:
        ax.bar_label(container=con)
    plt.title("Alcoholic Driver's City")
    st.pyplot(plt)
    plt.clf()

    # Fig 10
    plt.figure(figsize=(10,8))
    ax=sns.countplot(df[df["Accident"]==1]["Arrest Type"],order=df[df["Accident"]==1]["Arrest Type"].value_counts().head(10).index,palette="Blues_r")
    for con in ax.containers:
        ax.bar_label(container=con)
    plt.title("Arrest Type with more Accidents")
    st.pyplot(plt)
    plt.clf()

    # Fig 11
    temp=df.groupby(["Gender","Race"]).agg({"Accident":"count"})
    temp.reset_index(inplace=True)
    fig = px.sunburst(temp, path=['Gender', 'Race'], values='Accident',height=400,width=500,title="Contribution of Gender and Race in Accidents")
    fig.update_layout(margin = dict(t=30, l=25, r=25, b=25))
    st.plotly_chart(fig)