# Creating DB Connection
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from streamlit_option_menu import option_menu
import connectorx as cx

user = 'root'
password = 'root'
host = 'localhost'
port = '3306'
database = 'traffic_violation'

@st.cache_resource
def get_engine():
    return(f"mysql://{user}:{password}@{host}:{port}/{database}")

@st.cache_data(show_spinner=True)
def data_getter(_engine, query_string):
    return cx.read_sql(engine,query_string)

engine = get_engine()

df = data_getter(engine,"select * from fact_table")
charges=data_getter(engine,"select * from charges;")
whole=pd.merge(df,charges,how="inner",on="SeqID")

st.markdown("<style>body{font-family:Times New Roman;}</style>",unsafe_allow_html=True)

with st.sidebar:
    selected=option_menu("Menu",["Home","Data","Insights"])


if selected=="Home":
    st.markdown("<h1 style='text-align:center;'>Traffic Violation Analysis</h1>",unsafe_allow_html=True)
    st.metric("Total Violations",whole.shape[0])
    st.subheader("Violations involved in Accident")
    st.dataframe(whole.query("Accident==1")["Violation Type"].value_counts())
    st.subheader("High Risk Zones")
    st.dataframe(df[df["Accident"]==1].groupby(["Latitude","Longitude"]).agg({"SeqID":"count"}).sort_values("SeqID",ascending=False).head(10).rename(columns={"SeqID":"Accident Counts"}))
    st.subheader("Most Frequently Cited Vehicle Makes")
    labels_=df[df["Accident"]==1]["Make"].value_counts().index
    values_=df[df["Accident"]==1]["Make"].value_counts().values
    fig = px.treemap(df.value_counts(), path=[labels_],values=values_, width=600, height=300)
    colors=['#fae588','#f79d65','#f9dc5c','#e8ac65','#e76f51','#ef233c','#b7094c','#2bd496','#2bd4ba','#2bbad4']
    fig.update_layout(
        treemapcolorway = colors,
        margin = dict(t=30, l=25, r=25, b=25))
    st.plotly_chart(fig)

elif selected=="Data":
    st.markdown("<h1 style='text-align:center;'>Data</h1>",unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;color:grey;'>Let's drill through the data using filters!</h4>",unsafe_allow_html=True)
    whole=whole.sort_values("Date Of Stop_x",ascending=False).head(10000)

    # Date Filter 
    date_list=whole["Date Of Stop_x"].unique().tolist()
    date_list.insert(0,"All")
    date_sel=st.selectbox("Date",date_list)
    if date_sel=="All":
        pass
    else:
        whole=whole.query(f"`Date Of Stop_x`=='{date_sel}'")

    # Location Filter 
    location_list=whole["Location"].unique().tolist()
    location_list.insert(0,"All")
    location_sel=st.selectbox("Location",location_list)
    if location_sel=="All":
        pass
    else:
        whole=whole.query(f"Location=='{location_sel}'")
    
    # VehicleType
    v_list=whole["VehicleType"].unique().tolist()
    v_list.insert(0,"All")
    v_sel=st.selectbox("Vehicle Type",v_list)
    if v_sel=="All":
        pass
    else:
        whole=whole.query(f"VehicleType=='{v_sel}'")

    # Gender
    g_list=whole["Gender"].unique().tolist()
    g_list.insert(0,"All")
    g_sel=st.selectbox("Gender",g_list)
    if g_sel=="All":
        pass
    else:
        whole=whole.query(f"Gender=='{g_sel}'")

    # Race
    race_list=whole["Race"].unique().tolist()
    race_list.insert(0,"All")
    r_sel=st.selectbox("Race",race_list)
    if r_sel=="All":
        pass
    else:
        whole=whole.query(f"Race=='{r_sel}'")  

    # Violation Type 
    violation_list=whole["Violation Type"].unique().tolist()
    violation_list.insert(0,"All")
    vio_sel=st.selectbox("Violation Category",violation_list)
    if vio_sel=="All":
        pass
    else:
        whole=whole.query(f"`Violation Type`=='{vio_sel}'")
              
    # Dataframe
    col_list=["Date Of Stop_x","Time Of Stop_x"]
    col_list.extend(df.iloc[:,3:].columns.tolist())
    col_list.extend(charges.iloc[:,4:].columns.tolist())
    whole=whole.loc[:,col_list]
    st.dataframe(whole,hide_index=True)
    st.write(whole.shape)

elif selected=="Insights":
    i_list=["The Driving Licsense State with more Accidents",
            "Laws related to Incidents",
            "Number of Accidents from 2012 to 2025",
            "Alcoholic Driver's City",
            "Driver City with more Accident"]
    
    i_sel=st.selectbox("Insigths",i_list)

    if i_sel==i_list[0]:
        plt.figure(figsize=(10,8))
        ax=sns.countplot(df[df["Accident"]==1]["DL State"],order=df[df["Accident"]==1]["DL State"].value_counts().head(10).index,palette="Blues_r")
        for con in ax.containers:
            ax.bar_label(container=con)
        st.pyplot(plt)
        plt.clf()
    elif i_sel==i_list[1]:
        plt.figure(figsize=(10,8))
        filter_list=df.columns[8:18].tolist()
        filter_list.insert(0,"All")
        selected_col=st.selectbox("Incidents",filter_list)
        if selected_col!="All":
            whole=whole.query(f"`{selected_col}`==1")
        else:
            pass
        ax=sns.countplot(whole["Charge"],order=whole["Charge"].value_counts().head(10).index)
        for con in ax.containers:
            ax.bar_label(container=con)
        st.pyplot(plt)
        plt.clf()
    elif i_sel==i_list[2]:
        plt.figure(figsize=(10,8))
        df["Year"]=df["Date Of Stop"].dt.year
        sns.lineplot(x=df[df["Accident"]==1]["Year"].value_counts().index,y=df[df["Accident"]==1]["Year"].value_counts().values)
        st.pyplot(plt)
        plt.clf()
    elif i_sel==i_list[3]:
        plt.figure(figsize=(10,8))
        ax=sns.countplot(df[df["Alcohol"]==1]["Driver City"],order=df[df["Alcohol"]==1]["Driver City"].value_counts().head(10).index,palette="Blues_r")
        for con in ax.containers:
            ax.bar_label(container=con)
        st.pyplot(plt)
        plt.clf()
    elif i_sel==i_list[4]:
        # State Filter 
        state_list=df["Driver State"].unique().tolist()
        state_list.insert(0,"ALL")
        state=st.selectbox("Driver State",state_list)
        if state!="ALL":
            where_str=f"`Driver State`=='{state}'"
            temp=df.query(where_str)
        else:
            temp=df

        # Gender Filter
        gender_list=df["Gender"].unique().tolist()
        gender_list.insert(0,"All")
        gender_sel=st.selectbox("Gender",gender_list)
        if gender_sel!="All":
            where_str=f"Gender=='{gender_sel}'"
            temp=temp.query(where_str)
        else:
            pass

        # Race Filter
        race_list=df["Race"].unique().tolist()
        race_list.insert(0,"All")
        race_sel=st.selectbox("Race",race_list)
        if race_sel!="All":
            where_str=f"Race=='{race_sel}'"
            temp=temp.query(where_str)
        else:
            pass

        plt.figure(figsize=(10,8))
        ax=sns.countplot(temp[temp["Accident"]==1]["Driver City"],order=temp[temp["Accident"]==1]["Driver City"].value_counts().head(10).index,palette="Blues_r")
        for con in ax.containers:
            ax.bar_label(container=con)
        plt.title("Driver City with more Accident")
        st.pyplot(plt)
        plt.clf()