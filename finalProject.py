"""

Course Name: CS602

Student: Harrison Miao

Data Set: NYC Collision

# Description:

Road accidents constitute a significant proportion of the number of serious injuries reported every year especially
metro city like New York City. The objective of this project is to make New York City collision historical data
readable and interpretable to commuters or travelers so they can travel more safely within the city.

I achieve the goal by implementing the python interactive visualization library and data processing library
to create charts and widgets that organize the NYC collision data.

# TO RUN THE APP: --> open terminal --> navigate/cd to streamlit file location
--> install libraries: "pip install -r requirements.txt" --> use command: "streamlit run finalProject.py"

"""
import datetime
import time
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

SEP = 30*"*"

# Load and return the sorted data by 'DATE' in descending order
#@st.cache
def loadData():
    print(f'{SEP} File Loaded {SEP}')

    data = pd.read_csv("samples.csv")

    data.columns = data.columns.str.lower()

    print(data.columns)

    data['latitude'] = pd.to_numeric(data['latitude'])
    data['longitude'] = pd.to_numeric(data['longitude'])

    data['date'] = pd.to_datetime(data['date'])

    sortedData = data.sort_values(by='date', ascending=False)

    print(sortedData, type(sortedData))

    return sortedData

# Load date picker widget and return valid date range from user selection
def plotDatePicker(dataSource,dateTime=datetime.date(2016,6,6)):

    upperBound_date = str(dataSource.head(1)['date']).split()[1]
    upperBound = upperBound_date.split("-")

    lowerBound_date = str(dataSource.tail(1)['date']).split()[1]
    lowerBound = lowerBound_date.split("-")

    min_date = datetime.datetime(int(lowerBound[0]), int(lowerBound[1]), int(lowerBound[2]))
    max_date = datetime.date(int(upperBound[0]), int(upperBound[1]), int(upperBound[2]))

    st.sidebar.title(f"Check data between {lowerBound_date} - {upperBound_date}")
    start_date = str(st.sidebar.date_input('Start Date',value=dateTime,min_value=min_date,max_value=max_date))
    end_date = str(st.sidebar.date_input('End Date',value=dateTime,min_value=min_date,max_value=max_date))

    showTable = st.sidebar.checkbox('Show Above Table Data')

    if start_date >= lowerBound_date and start_date <= upperBound_date and start_date <= end_date and end_date <= upperBound_date:
        st.sidebar.success('You are in the date range!')
        if start_date == end_date:
            if showTable:
                st.subheader(f'\n\nStart Date : {start_date}')
                dataSource[dataSource['date'] == start_date]
        else:
            if showTable:
                st.subheader(f'\n\nStart Date : {start_date} - End Date : {end_date}')
                dataSource[(dataSource['date'] >= start_date) & (dataSource['date'] <= end_date)]
    else:
        st.sidebar.error(f'Error: Start Date must fall after or equal the "{lowerBound_date}" \n\n End Date must before or equal the "{upperBound_date}"')

def plotDropdownSelection(dataSource):

    upperBound_date = str(dataSource.head(1)['date']).split()[1]

    lowerBound_date = str(dataSource.tail(1)['date']).split()[1]

    upperYear = int(upperBound_date.split("-")[0])

    lowerYear = int(lowerBound_date.split("-")[0])

    tempList = [i for i in range(lowerYear, upperYear+1)]

    # Add selectbox in streamlit
    optionYear = st.sidebar.selectbox(
    'Please choose the year of accident collision?', tempList)
    st.sidebar.write('You selected year :', optionYear)

    # Make histogram by year
    dataSource['year'] = pd.DatetimeIndex(dataSource['date']).year

    sumList1 = ['persons injured','pedestrians injured','cyclists injured','motorists injured']
    #sumList2 = ['persons killed','pedestrians killed','cyclists killed','motorists killed']

    # High frequency area zip code and count
    pieData1 = dataSource.groupby(by=dataSource['zip code'])[sumList1].sum().sort_values(by='persons injured', ascending=False).head(1)
    pieData2 = dataSource.groupby(by=dataSource['zip code'])[sumList1].sum().sort_values(by='pedestrians injured',ascending=False).head(1)
    pieData3 = dataSource.groupby(by=dataSource['zip code'])[sumList1].sum().sort_values(by='cyclists injured',ascending=False).head(1)
    pieData4 = dataSource.groupby(by=dataSource['zip code'])[sumList1].sum().sort_values(by='motorists injured',ascending=False).head(1)

    data1Index = pieData1.index
    data2Index = pieData2.index
    data3Index = pieData3.index
    data4Index = pieData4.index

    pieGraphData1 = {'type': ['Total Persons Injured', 'Zip:'+str(data1Index[0])], 'count': [dataSource['persons injured'].sum(), pieData1.iloc[0]['persons injured']]}
    pieGraphData2 = {'type': ['Total Pedestrians Injured', 'Zip:' + str(data2Index[0])],'count': [dataSource['pedestrians injured'].sum(), pieData2.iloc[0]['pedestrians injured']]}
    pieGraphData3 = {'type': ['Total Cyclists Injured', 'Zip:'+str(data3Index[0])], 'count': [dataSource['cyclists injured'].sum(), pieData3.iloc[0]['cyclists injured']]}
    pieGraphData4 = {'type': ['Total Motorists Injured', 'Zip:' + str(data4Index[0])],'count': [dataSource['motorists injured'].sum(), pieData4.iloc[0]['motorists injured']]}

    personsInjuredPieChart = pd.DataFrame(data=pieGraphData1)
    pedestriansInjuredPieChart = pd.DataFrame(data=pieGraphData2)
    cyclistsInjuredPieChart = pd.DataFrame(data=pieGraphData3)
    motoristsInjured = pd.DataFrame(data=pieGraphData4)

    print(personsInjuredPieChart)
    print(pedestriansInjuredPieChart)
    print(cyclistsInjuredPieChart)
    print(motoristsInjured)

    chartList = [personsInjuredPieChart,pedestriansInjuredPieChart,cyclistsInjuredPieChart,motoristsInjured]

    data1 = dataSource.groupby([dataSource['year'] == optionYear])[sumList1].sum()

    # data2 = dataSource.groupby([dataSource['year'] == optionYear])[sumList2].sum()

    data1.index = ["RestYear", "Injured"]

    data1.loc['Total'] = data1.sum(axis=0)

    print(data1.to_string())

    st.subheader(f'{optionYear} Injury and Death')

    st.bar_chart(data1)

    return chartList

def plotHeatMap(dataSource):

    showHeatMap = st.sidebar.checkbox('Collision Density Map')

    if showHeatMap:
        # Set the map to center around BROOKLYN (40.5836578, -73.9865462) and add layer Stamen Terrain
        map_heatmap = folium.Map(location=[40.5836578, -73.9865462], tiles='Stamen Terrain',zoom_start=10)

        # Filter then remove null value
        heat_df = dataSource[["latitude", "longitude"]]
        heat_df = heat_df.dropna(axis=0, subset=["latitude", "longitude"])

        heat_data = [[row["latitude"], row["longitude"]] for index, row in heat_df.iterrows()]

        HeatMap(heat_data).add_to(map_heatmap)

        st.subheader("Collision Density Map")

        folium_static(map_heatmap)

def monthlyHistogram(dataSource):

    # Add one column to the dataSource for the year-monthly count calculation, format: yyyy-mm
    dataSource['year-month'] = dataSource['date'].map(lambda x: '{year}-{month}'.format(year=x.year,month=x.month,day=x.day))

    histData = dataSource.groupby(['year-month']).size()

    st.subheader('Monthly Collision')

    st.bar_chart(histData)

def loadingAnimation():

    progress_bar = st.progress(0)

    for i in range(100):
        # Update progress bar.
        progress_bar.progress(i + 1)
        time.sleep(0.005)

    progress_bar.empty()

    #st.balloons()

def plotPieChart(dataFrame):

    pie1, pie2, pie3, pie4 = st.beta_columns(4)

    tempList = ['Persons Injured','Pedestrians Injured','Cyclists Injured','Motorists Injured']

    # Add selectbox for pie chart
    optionArea = st.sidebar.selectbox(
        'Please choose the high frequency area?',tempList)

    if optionArea == "Persons Injured":

        pie1.subheader(f'High-Frequency Persons Injured {dataFrame[0].iloc[1][0]}')

        fig1 = px.pie(dataFrame[0], values='count', names='type', hover_name='type')

        fig1.update_traces(textposition='inside', textinfo='percent+label')

        pie1.write(fig1)

    elif optionArea == "Pedestrians Injured":

        pie2.subheader(f'High-Frequency Pedestrians Injured {dataFrame[1].iloc[1][0]}')

        fig2 = px.pie(dataFrame[1], values='count', names='type', hover_name='type')

        fig2.update_traces(textposition='inside', textinfo='percent+label')

        pie2.write(fig2)

    elif optionArea == "Cyclists Injured":

        pie3.subheader(f'High-Frequency Cyclists Injured {dataFrame[2].iloc[1][0]}')

        fig3 = px.pie(dataFrame[2], values='count', names='type', hover_name='type')

        fig3.update_traces(textposition='inside', textinfo='percent+label')

        pie3.write(fig3)

    elif optionArea == "Motorists Injured":

        pie4.subheader(f'High-Frequency Motorists Injured {dataFrame[3].iloc[1][0]}')

        fig4 = px.pie(dataFrame[3], values='count', names='type', hover_name='type')

        fig4.update_traces(textposition='inside', textinfo='percent+label')

        pie4.write(fig4)

def main():

    # Set page layout
    st.set_page_config(
        page_title="NYC Collision",
        layout="wide"
    )

    st.title('NYC Historical Collision')

    expander = st.beta_expander("CS 602 Summer 2021 - Final Project")
    expander.text("By Harrison Miao")

    loadingAnimation()

    # Return data
    csvData = loadData()

    time.sleep(0.1)

    # Plot graphs
    monthlyHistogram(csvData)

    plotDatePicker(csvData)

    listDataFrame = plotDropdownSelection(csvData)

    plotHeatMap(csvData)

    plotPieChart(listDataFrame)

main()

