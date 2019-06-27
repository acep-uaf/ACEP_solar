"""This package contains all the tools for plotting the various graphics in Bokeh and saving them as HTML files."""

import h5py
import bokeh
import json
import pandas as pd
import numpy as np
import requests
from bokeh.plotting import figure, output_file, show, output_notebook
from bokeh.models import NumeralTickFormatter
from bokeh.palettes import Spectral4
from bokeh.io import show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CustomJS, Select
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label, Legend
from bokeh.plotting import figure
from ARCTIC import hdf5_interface
from ARCTIC import nrel_api_interface

def tilt_angle_plot_generation(location_dataframe): 
    """This function takes in a dataframe that contains latitudes and longitudes for a number of 
    locations and generates interactive Bokeh plots showing the variation of monthly production 
    with changing tilt angles."""
    #The below list is sufficiently granular to cover most situations.
    tilt_list = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]

    #Walk through each row in the location dataframe, calling PVwatts and plotting results.
    for j in range(len(location_dataframe.index)):
        print("Data for " + str(location_dataframe['location'][j]) + " is being calculated")
        nrel_long_tilt = []
        for i in range(len(tilt_list)):
            json_response, new_dataframe = nrel_api_interface.call_pvwatts(latitude = location_dataframe['latitude'][j], 
                                                                                     longitude = location_dataframe['longitude'][j], 
                                                                                     tilt = tilt_list[i], dataset = 'tmy3')
            nrel_long_tilt.append(new_dataframe)
        tilt_response_dataframe = pd.DataFrame(columns = tilt_list)
        for i, tilt in enumerate(tilt_list):
            tilt_response_dataframe[tilt] = nrel_long_tilt[i]['ac_monthly']/4

        #The below is all of the data for the plotting components.
        #This adjusts the name of the saved file, so it's specific to each location.
        output_file("{}_monthly_production_varying_tilts.html".format(location_dataframe['location'][j]))
        #Set up a month proxy
        x = np.arange(1,13)

        #Tell the plot where to look for the data. The extra specifications of y values
        #enable the plot to be interactive.
        source = ColumnDataSource(data=dict(x=x, y=tilt_response_dataframe[5],
                                            tilt_5_degrees=tilt_response_dataframe[5], tilt_10_degrees=tilt_response_dataframe[10],
                                            tilt_15_degrees=tilt_response_dataframe[15], tilt_20_degrees=tilt_response_dataframe[20],
                                            tilt_25_degrees=tilt_response_dataframe[25], tilt_30_degrees=tilt_response_dataframe[30],
                                            tilt_35_degrees=tilt_response_dataframe[35], tilt_40_degrees=tilt_response_dataframe[40],
                                            tilt_45_degrees=tilt_response_dataframe[45], tilt_50_degrees=tilt_response_dataframe[50],
                                            tilt_55_degrees=tilt_response_dataframe[55], tilt_60_degrees=tilt_response_dataframe[60],
                                            tilt_65_degrees=tilt_response_dataframe[65], tilt_70_degrees=tilt_response_dataframe[70],
                                            tilt_75_degrees=tilt_response_dataframe[75], tilt_80_degrees=tilt_response_dataframe[80],
                                            tilt_85_degrees=tilt_response_dataframe[85], tilt_90_degrees=tilt_response_dataframe[90],
                                           ))
        #Plot specifications
        plot = figure(x_axis_label='Month', y_axis_label='Normalized Monthly Production (kWh/kW)', plot_height=400)
        plot.line(x='x', y='y', source=source)
        plot.title.text = "Annual Production at Varying Tilt Angles"
        plot.title.align = "center"
        plot.title.text_font = "times"
        plot.title.text_font_style = "italic"
        plot.title.text_font_size = '15pt'
        #This line is what connects the changing dropdown menu with the data that is displayed.
        select = Select(value='foo', options=['tilt_5_degrees', 'tilt_10_degrees','tilt_15_degrees',
                                             'tilt_20_degrees','tilt_25_degrees','tilt_30_degrees',
                                             'tilt_35_degrees','tilt_40_degrees','tilt_45_degrees',
                                             'tilt_50_degrees','tilt_55_degrees','tilt_60_degrees',
                                             'tilt_65_degrees','tilt_70_degrees','tilt_75_degrees',
                                             'tilt_80_degrees','tilt_85_degrees','tilt_90_degrees'])
        #javascript that actually makes the changes possible.
        select.js_on_change('value', CustomJS(args=dict(source=source, select=select), code="""
            // make a shallow copy of the current data dict
            const new_data = Object.assign({}, source.data)

            // update the y column in the new data dict from the appropriate other column
            new_data.y = source.data[select.value]

            // set the new data on source, BokehJS will pick this up automatically
            source.data = new_data
        """))

        show(column(plot, select))


def annual_tilt_angle_plot_generation(location_dataframe):
    """This function plots the annual generation predicted by PVWatts for TMY2 and TMY3 datasets
    at a variety of tilt angles. It operates dynamically, and prints for all locations in the 
    passed location dataframe."""
    #The below list is sufficiently granular to cover most situations.
    tilt_list = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]
    
    #Walk through each row in the location dataframe, calling PVwatts and plotting results.
    for j in range(len(location_dataframe.index)):
        print("Data for " + str(location_dataframe['location'][j]) + " is being calculated")
        #If the response from PVWatts has an error, flip the zero to a one, and don't plot.
        tmy2_response = np.zeros(len(tilt_list))
        tmy3_response = np.zeros(len(tilt_list))
        annual_production_tmy2 = []
        annual_production_tmy3 = []
        #Calculate all of the tilt information for TMY3 and TMY3. 
        for i in range(len(tilt_list)):
            json_response, new_dataframe = nrel_api_interface.call_pvwatts(latitude = location_dataframe['latitude'][j], 
                                                                                     longitude = location_dataframe['longitude'][j], 
                                                                                     tilt = tilt_list[i], dataset = 'tmy3')
            if json_response['errors'] != []:
                tmy3_response[i] = 1
            else:
                annual_production_tmy3.append(new_dataframe['ac_annual'][2]/4)
            
            #repeat the above with the TMY2 dataset
            json_response, new_dataframe = nrel_api_interface.call_pvwatts(latitude = location_dataframe['latitude'][j], 
                                                                                 longitude = location_dataframe['longitude'][j], 
                                                                                 tilt = tilt_list[i], dataset = 'tmy2')
            if json_response['errors'] != []:
                tmy2_response[i] = 1
            else:    
                annual_production_tmy2.append(new_dataframe['ac_annual'][2]/4)
        
        #Save the file
        output_file("{}_annual_production_varying_tilts.html".format(location_dataframe['location'][j]))
        p = figure( x_axis_label='Tilts', y_axis_label='Annual Production (kWh)',plot_width=500, plot_height=250)

        # add a line renderer
        #Check to see if there is TMY2 or TMY3 data for this location. 
        if sum(tmy2_response) == 0:
            p.line(tilt_list, annual_production_tmy2, line_width=2, color='red', legend='TMY2')
        else:
            print("No TMY2 data was available for this location.")
        if sum(tmy3_response) == 0:    
            p.line(tilt_list, annual_production_tmy3, line_width=2, color='blue', legend='TMY3')
        else:
            print("No TMY3 data was available for this location")

        p.xaxis.ticker = [10,20,30,40,50,60,70,80,90]
        p.title.text = "Annual Production at Varying Tilts"
        p.title.align = "center"
        p.title.text_font = "times"
        p.title.text_font_style = "italic"
        p.title.text_font_size = '12pt'

        show(p)   


def annual_production_loss_plot_generation(location_dataframe):
    """This function plots the percentage loss of production for tilt angles that are not
    in alignment with the optimal tilt angle."""    
    #The below list is sufficiently granular to cover most situations.
    tilt_list = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90]
    
    #Walk through each row in the location dataframe, calling PVwatts and plotting results.
    for j in range(len(location_dataframe.index)):
        print("Data for " + str(location_dataframe['location'][j]) + " is being calculated")
        #If the response from PVWatts has an error, flip the zero to a one, and don't plot.
        tmy2_response = np.zeros(len(tilt_list))
        tmy3_response = np.zeros(len(tilt_list))
        annual_production_tmy2 = []
        annual_production_tmy3 = []
        #Calculate all of the tilt information for TMY3 and TMY3. 
        for i in range(len(tilt_list)):
            json_response, new_dataframe = nrel_api_interface.call_pvwatts(latitude = location_dataframe['latitude'][j], 
                                                                                     longitude = location_dataframe['longitude'][j], 
                                                                                     tilt = tilt_list[i], dataset = 'tmy3')
            if json_response['errors'] != []:
                tmy3_response[i] = 1
            else:
                annual_production_tmy3.append(new_dataframe['ac_annual'][2]/4)
            
            #repeat the above with the TMY2 dataset
            json_response, new_dataframe = nrel_api_interface.call_pvwatts(latitude = location_dataframe['latitude'][j], 
                                                                                 longitude = location_dataframe['longitude'][j], 
                                                                                 tilt = tilt_list[i], dataset = 'tmy2')
            if json_response['errors'] != []:
                tmy2_response[i] = 1
            else:    
                annual_production_tmy2.append(new_dataframe['ac_annual'][2]/4)
        
        if sum(tmy2_response) == 0:
            dict_tmy2 = {'Tilts':tilt_list,'Annual_production':annual_production_tmy2}
            df_tmy2 = pd.DataFrame(dict_tmy2)
            #Then find out the max production row
            max_tilt_tmy2 = int(df_tmy2[['Annual_production']].idxmax().values)
            #Then calculate the other tilts' percent loss compared with the max annual production
            lose_tmy2 = []
            for index, row in df_tmy2.iterrows():
                tilt_loss = 1- row['Annual_production']/df_tmy2['Annual_production'][max_tilt_tmy2]
                lose_tmy2.append(tilt_loss)
            df_tmy2['loss']=lose_tmy2

        else:
            print("There is no TMY2 weather station data at this location.")
            
        #Repeat for TMY3 data.
        if sum(tmy3_response) == 0:
            dict_tmy3 = {'Tilts':tilt_list,'Annual_production':annual_production_tmy3}
            df_tmy3 = pd.DataFrame(dict_tmy3)
            max_tilt_tmy3 = int(df_tmy3[['Annual_production']].idxmax().values)
            lose_tmy3 = []
            for index, row in df_tmy3.iterrows():
                tilt_loss = 1- row['Annual_production']/df_tmy3['Annual_production'][max_tilt_tmy3]
                lose_tmy3.append(tilt_loss)
            df_tmy3['loss']=lose_tmy3   

        #Save the file
        output_file("{}_annual_production_loss_tilts.html".format(location_dataframe['location'][j]))

        p = figure(x_axis_label='Tilts', y_axis_label='loss (%)',plot_width=500, plot_height=250)

        # add a line renderer
        if sum(tmy2_response) == 0:
            p.line(tilt_list, df_tmy2['loss'], line_width=2,color='red',legend="TMY2")
        if sum(tmy3_response) == 0:
            p.line(tilt_list, df_tmy3['loss'],line_width=2,color='blue',legend="TMY3")
        p.xaxis.ticker = [10,20,30,40,50,60,70,80,90]
        p.yaxis.formatter = NumeralTickFormatter(format='0 %')
        p.title.text = "Annual Production Loss with Varying Tilts"
        p.title.align = "center"
        p.title.text_font = "times"
        p.title.text_font_style = "italic"
        p.title.text_font_size = '12pt'

        show(p)    

def hdf5_to_dataframe(hdf5_filename, location_name, panel_name):
    """This function extracts data from an HDF5 file and loads it into a pandas dataframe"""
    #Load the HDF5 file data
    hdf5_file = h5py.File('{}.h5'.format(hdf5_filename), 'r')
    hdf5_location = hdf5_file.get(location_name)
    panel_location = hdf5_location.get(panel_name)
    dataframe = pd.DataFrame()
    for keys in panel_location.keys():
        dataframe[str(keys)] = panel_location[str(keys)]
    dataframe['Month'] = dataframe['Month'].astype(int)
    return dataframe

def pvwatts_tmy2(lattitude,longitude):
    # Get the data from the PV Watts --TMY2
    list_parameters = {"formt": 'JSON', "api_key": "spJFj2l5ghY5jwk7dNfVYs3JHbpR6BOGHQNO8Y9Z", "system_capacity": 18, "module_type": 0, "losses": 14.08,
                  "array_type": 0, "tilt": 50, "azimuth": 180, "lat": lattitude, "lon": longitude, "dataset": 'tmy2'}
    json_response = requests.get("https://developer.nrel.gov/api/pvwatts/v6", params = list_parameters).json()
    TMY2 = pd.DataFrame(data = json_response['outputs'])
    return TMY2

def pvwatts_tmy3(lattitude,longitude):
    # Get the data from the PV Watts --TMY3
    list_parameters = {"formt": 'JSON', "api_key": "spJFj2l5ghY5jwk7dNfVYs3JHbpR6BOGHQNO8Y9Z", "system_capacity": 18, "module_type": 0, "losses": 14.08,
                  "array_type": 0, "tilt": 50, "azimuth": 180, "lat": lattitude, "lon": longitude, "dataset": 'tmy3'}
    json_response = requests.get("https://developer.nrel.gov/api/pvwatts/v6", params = list_parameters).json()
    TMY3 = pd.DataFrame(data = json_response['outputs'])
    return TMY3

def annual_Norm(dataframe,capacity):
    '''Calculate rolling annual production'''
    lenth_list = list(range(12,len(dataframe.index)))
    annual_values = []
    month = []
    for i in range(len(lenth_list)):
        single_values = dataframe['Energy'][lenth_list[i]-12:lenth_list[i]].sum()/capacity
        #rolling_average.append(each_period)
        single_month = dataframe['Date'][lenth_list[i]]
        annual_values.append(single_values)
        month.append(single_month)
    return(annual_values,month)

def daily_to_monthly_energy(file_name, location_name, panel_name):
    solar_dataframe = hdf5_to_dataframe(file_name, location_name, panel_name)
    new_dataframe = pd.DataFrame(columns = ['Year', 'Month', 'Energy', 'Interpolate'])
    previous_month_tracker = solar_dataframe['Month'][0]
    Sum = 0
    interpolated = 0
    j = 0 
    year_array = np.array(np.NaN)
    month_array = np.array(np.NaN)
    interpolation_array = np.array(np.NaN)
    energy_array = np.array(np.NaN)
    for i in range(len(solar_dataframe.index)):
        if solar_dataframe['Month'][i] == previous_month_tracker:
            Sum = Sum + solar_dataframe['Energy'][i]
            interpolated = interpolated + solar_dataframe['Interpolate'][i]
        else:
            year_array = np.append(year_array, solar_dataframe['Year'][i])
            month_array = np.append(month_array, solar_dataframe['Month'][i])
            if interpolated > 0:
                interpolation_array = np.append(interpolation_array, 1)
            else:
                interpolation_array = np.append(interpolation_array, 0)
            energy_array = np.append(energy_array, Sum)
            Sum = 0
            interpolated = 0
            j = j + 1
            previous_month_tracker = solar_dataframe['Month'][i]
    new_dataframe['Energy'] = energy_array.astype(int)
    new_dataframe['Month'] = month_array.astype(int)
    new_dataframe['Year'] = year_array.astype(int)
    new_dataframe['Interpolate'] = interpolation_array.astype(int)
    new_dataframe = new_dataframe.drop(0).reset_index(drop=True)
    
    #new_dataframe['DC Capacity'][1] = solar_dataframe['DC Capacity'][0]
    #new_dataframe['Location'][1] = solar_dataframe['Location'][0]
    return new_dataframe

def normalized_annual_production(location_name,file_name,lattitude,longitude):
    '''read the data from 'solar_panel_data_alaska' file, 
       and generate the annual figure with median/max lines and TMY2&3
    
    input: location_name, lattitude, longitude
    output: Normalized Annual Production figure and generate a html file named "popup_"+location_name+".html"  
    '''
    my_file = h5py.File(file_name +".h5", 'r')
    location_hdf5 = my_file.get(location_name)
    location=pd.DataFrame(columns=['Date'])
    a=0
    for name in location_hdf5:
        capacity = location_hdf5[name].attrs.__getitem__("DC Capacity")
        if location_hdf5[name].keys().__contains__('Day'):
            base = daily_to_monthly_energy(file_name, location_name, name)
        else:    
            base = hdf5_to_dataframe(file_name,location_name, name )
        # read data
        


        # Change the date into a datetime format
        base['Date']= ""
        for i in range(len(base)):
            base['Date'][i] = str(base['Year'][i]) + '-' + str(base['Month'][i])    
            base['Date'] = pd.to_datetime(base['Date'])
        base.drop(['Year','Month'],axis = 1,inplace = True)

        # calculate annual value
        annual_values,month= annual_Norm(base,capacity)
        new_base = pd.DataFrame({'Date':month,'Annual':annual_values})

        location = pd.merge(location, new_base, on = ['Date'], how='outer',suffixes=(a, a+1))
        a = a+1

    location = location.sort_values(by='Date')

    xaxis=location['Date']  
    # setting x axis with Date
    
    # Get the data from the PV Watts --TMY2
    list_parameters = {"formt": 'JSON', "api_key": "spJFj2l5ghY5jwk7dNfVYs3JHbpR6BOGHQNO8Y9Z", "system_capacity": 18, "module_type": 0, "losses": 14.08,
                  "array_type": 0, "tilt": 50, "azimuth": 180, "lat": lattitude, "lon": longitude, "dataset": 'tmy2'}
    json_response = requests.get("https://developer.nrel.gov/api/pvwatts/v6", params = list_parameters).json()
    TMY2 = pd.DataFrame(data = json_response['outputs'])
    
    # Get the data from the PV Watts --TMY3
    list_parameters = {"formt": 'JSON', "api_key": "spJFj2l5ghY5jwk7dNfVYs3JHbpR6BOGHQNO8Y9Z", "system_capacity": 18, "module_type": 0, "losses": 14.08,
                  "array_type": 0, "tilt": 50, "azimuth": 180, "lat": lattitude, "lon": longitude, "dataset": 'tmy3'}
    json_response = requests.get("https://developer.nrel.gov/api/pvwatts/v6", params = list_parameters).json()
    TMY3 = pd.DataFrame(data = json_response['outputs'])
    
    if TMY2.empty== True:
        tmy3 = pvwatts_tmy3(lattitude,longitude)['ac_annual'][1]/18
    # store tmy2&3 data

        location = location.drop(['Date'], axis=1)
    # delet Date column to calculate median value and maxium value

        location['Median'] = location.median(1)
        location["Max"] = location.max(1)
    # adding median and max value into dataframe


    # plot median and max value vs. date
        output_notebook()
        p = figure(plot_width=600, plot_height=300, x_axis_type='datetime')

        output_file("popup_"+location_name+".html")

    # title style
        p.title.text='Normalized Annual Production in '+location_name
        p.title.align = 'center'
        p.title.text_font_size = "15px"
        p.title.text_font = "times"
        p.title.text_font_style = "italic"

    # add the number of panels in the figure
    #citation = Label(x=10, y=180, x_units='screen', y_units='screen',
    #                 text= str(len(location_hdf5)) + ' solar PV Arrays included in this dataset', render_mode='css')
                     #border_line_color='black', border_line_alpha=1.0,
                     #background_fill_color='white', background_fill_alpha=1.0)
    #p.add_layout(citation)

    # draw lines    
        r0 = p.line(xaxis, location['Max'], line_width=1, color='red')      #Best
        r1 = p.line(xaxis, location['Median'], line_width=1, color='blue')  #Median
        
        r4 = p.line(xaxis, tmy3*0.95, line_width=1, color='orange')         #TMY3_low
        r5 = p.line(xaxis, tmy3*1.05, line_width=1, color='orange')         #TMY3_high
    
        legend = Legend(items=[
        ("Best"   , [r0]),
        ("Median" , [r1]),

        ("TMY3_low" , [r4]),
        ("TMY3_high" , [r5]),
        ], location="center")
        p.add_layout(legend, 'right')
    
    

    # add labels
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'AC kWh produced/DC kW installed (kWh/kW)'
        p.legend.click_policy="hide"
        show(p)
    else:
        tmy2 = pvwatts_tmy2(lattitude,longitude)['ac_annual'][1]/18
        tmy3 = pvwatts_tmy3(lattitude,longitude)['ac_annual'][1]/18
    # store tmy2&3 data

        location = location.drop(['Date'], axis=1)
    # delet Date column to calculate median value and maxium value

        location['Median'] = location.median(1)
        location["Max"] = location.max(1)
    # adding median and max value into dataframe


    # plot median and max value vs. date
        output_notebook()
        p = figure(plot_width=600, plot_height=300, x_axis_type='datetime')

        output_file("popup_"+location_name+".html")

    # title style
        p.title.text='Normalized Annual Production in '+location_name
        p.title.align = 'center'
        p.title.text_font_size = "15px"
        p.title.text_font = "times"
        p.title.text_font_style = "italic"

    # add the number of panels in the figure
    #citation = Label(x=10, y=180, x_units='screen', y_units='screen',
    #                 text= str(len(location_hdf5)) + ' solar PV Arrays included in this dataset', render_mode='css')
                     #border_line_color='black', border_line_alpha=1.0,
                     #background_fill_color='white', background_fill_alpha=1.0)
    #p.add_layout(citation)

    # draw lines    
        r0 = p.line(xaxis, location['Max'], line_width=1, color='red')      #Best
        r1 = p.line(xaxis, location['Median'], line_width=1, color='blue')  #Median
        r2 = p.line(xaxis, tmy2*0.95, line_width=1, color='green')          #TMY2_low
        r3 = p.line(xaxis, tmy2*1.05, line_width=1, color='green')          #TMY2_high
        r4 = p.line(xaxis, tmy3*0.95, line_width=1, color='orange')         #TMY3_low
        r5 = p.line(xaxis, tmy3*1.05, line_width=1, color='orange')         #TMY3_high
    
        #add legend outside of figure
        legend = Legend(items=[
        ("Best"   , [r0]),
        ("Median" , [r1]),

        ("TMY2_low" , [r2]),
        ("TMY2_high" , [r3]),
        ("TMY3_low" , [r4]),
        ("TMY3_high" , [r5]),
        ], location="center")
        p.add_layout(legend, 'right')
    

    # add labels
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'AC kWh produced/DC kW installed (kWh/kW)'
        p.legend.click_policy="hide"
        show(p)
    return()

def normalized_monthly(location_name,file_name,lattitude,longitude):
    '''read the data from 'solar_panel_data_alaska' file, 
       and generate the monthly figure with  median/max lines and TMY2&3
       input: location_name, lattitude, longitude
       output: Normalized Annual Production figure and generate a html file named "monthly_"+location_name+".html" 
    
    '''
    
    location=pd.DataFrame(columns=['Month', 'Year'])
    my_file = h5py.File(file_name +".h5", 'r')
    location_hdf5 = my_file.get(location_name)

    a=0
    for name in location_hdf5:
        capacity = location_hdf5[name].attrs.__getitem__("DC Capacity")
        if location_hdf5[name].keys().__contains__('Day'):
            base = daily_to_monthly_energy(file_name, location_name, name)
            base = base.drop('Interpolate', axis=1)
        else:    
            base = hdf5_to_dataframe(file_name,location_name, name )
            base = base.drop('Interpolate', axis=1)
    # read data


        base['Energy'] = base['Energy']/capacity
        location = pd.merge(location, base, on = ['Month', 'Year'], how='outer',suffixes=(a, a+1))
        a = a+1

    # set up a dataframe to store TMY2&3 ac_monthly
    pv = pd.DataFrame()
    
    #call the function
    TMY2 = pvwatts_tmy2(lattitude,longitude)
    TMY3 = pvwatts_tmy3(lattitude,longitude)
    
    #see if TMY2 is empty
    if TMY2.empty ==True:
        
        pv['TMY3'] =pvwatts_tmy3(lattitude,longitude).ac_monthly
        pv['Month'] = [1,2,3,4,5,6,7,8,9,10,11,12]

        result = pd.merge(location, pv, on = ['Month'], how='outer' )
    #merge PVWatts data into location data


        result['Date'] = ""
    # Change the date into a datetime format
        for i in range(len(result)):
            result['Date'][i] = str(result['Year'][i]) + '-' + str(result['Month'][i])    
            result['Date'] = pd.to_datetime(result['Date'])

        result = result.sort_values(by='Date')
    # sort by date

        xaxis=result['Date']  
    # setting x axis with Date

        tmy3 = result['TMY3']/18
    # store tmy2&3 data



        result = result.drop(['Date', 'Month', 'Year', 'TMY3'], axis=1)
    # delet Date column to calculate median value and maxium value

        result['Median'] = result.median(1)
        result["Max"] = result.max(1)
    # adding median and max value into dataframe

    # plot median and max value vs. date
        output_notebook()
        p = figure(plot_width=600, plot_height=300, x_axis_type='datetime')

        output_file("monthly_"+location_name+".html") 

    # title style
        p.title.text='Normalized Monthly Production in '+location_name
        p.title.align = 'center'
        p.title.text_font_size = "15px"
        p.title.text_font = "times"
        p.title.text_font_style = "italic"

    # add the number of panels in the figure
    #citation = Label(x=10, y=180, x_units='screen', y_units='screen',
    #                 text= str(len(location_hdf5)) + ' solar PV Arrays included in this dataset', render_mode='css')
                     #border_line_color='black', border_line_alpha=1.0,
                     #background_fill_color='white', background_fill_alpha=1.0)
    #p.add_layout(citation)

        r0 = p.line(xaxis, result['Max'], line_width=1, color='red')      #Best
        r1 = p.line(xaxis, result['Median'], line_width=1, color='blue')  #Median
        
        r3 = p.line(xaxis, tmy3, line_width=1, color='orange')         #TMY3
        #add legend outside of figure
        legend = Legend(items=[
        ("Best"   , [r0]),
        ("Median" , [r1]),
        ("TMY3" , [r3]),
        ], location="center")
        p.add_layout(legend, 'right')


    # add labels
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'AC kWh produced/DC kW installed (kWh/kW)'
        p.legend.click_policy="hide"
        show(p)
        
    else:
        pv['TMY2'] = pvwatts_tmy2(lattitude,longitude).ac_monthly
        pv['TMY3'] =pvwatts_tmy3(lattitude,longitude).ac_monthly
        pv['Month'] = [1,2,3,4,5,6,7,8,9,10,11,12]

        result = pd.merge(location, pv, on = ['Month'], how='outer' )
    #merge PVWatts data into location data


        result['Date'] = ""
    # Change the date into a datetime format
        for i in range(len(result)):
            result['Date'][i] = str(result['Year'][i]) + '-' + str(result['Month'][i])    
            result['Date'] = pd.to_datetime(result['Date'])

        result = result.sort_values(by='Date')
    # sort by date

        xaxis=result['Date']  
    # setting x axis with Date
        tmy2 = result['TMY2']/18
        tmy3 = result['TMY3']/18
    # store tmy2&3 data



        result = result.drop(['Date', 'Month', 'Year', 'TMY2','TMY3'], axis=1)
    # delet Date column to calculate median value and maxium value

        result['Median'] = result.median(1)
        result["Max"] = result.max(1)
    # adding median and max value into dataframe

    # plot median and max value vs. date
        output_notebook()
        p = figure(plot_width=600, plot_height=300, x_axis_type='datetime')

        output_file("monthly_"+location_name+".html") 

    # title style
        p.title.text='Normalized Monthly Production in '+location_name
        p.title.align = 'center'
        p.title.text_font_size = "15px"
        p.title.text_font = "times"
        p.title.text_font_style = "italic"

    # add the number of panels in the figure
    #citation = Label(x=10, y=180, x_units='screen', y_units='screen',
    #                 text= str(len(location_hdf5)) + ' solar PV Arrays included in this dataset', render_mode='css')
                     #border_line_color='black', border_line_alpha=1.0,
                     #background_fill_color='white', background_fill_alpha=1.0)
    #p.add_layout(citation)

        r0 = p.line(xaxis, result['Max'], line_width=1, color='red')      #Best
        r1 = p.line(xaxis, result['Median'], line_width=1, color='blue')  #Median
        r2 = p.line(xaxis, tmy2, line_width=1, color='green')          #TMY2
        r3 = p.line(xaxis, tmy3, line_width=1, color='orange')         #TMY3
        #add legend outside of figure
        legend = Legend(items=[
        ("Best"   , [r0]),
        ("Median" , [r1]),
        ("TMY2" , [r2]),
        ("TMY3" , [r3]),
        ], location="center")
        p.add_layout(legend, 'right')


    # add labels
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'AC kWh produced/DC kW installed (kWh/kW)'
        p.legend.click_policy="hide"
        show(p)
        
def errorbar(location_name,file_name,lattitude,longitude):
    
    '''read the data from 'solar_panel_data_alaska' file, 
       and generate the error bar figure with mean and standrad deviation lines and TMY2&3
    
    input: location_name, lattitude, longitude
    output: Normalized Annual Production figure and generate a html file named "errorbar_"+location_name+".html"  
    ''' 
    
    location=pd.DataFrame(columns=['Month', 'Year'])
    my_file = h5py.File(file_name +".h5", 'r')
    location_hdf5 = my_file.get(location_name)

    a=0
    for name in location_hdf5:
        capacity = location_hdf5[name].attrs.__getitem__("DC Capacity")
        if location_hdf5[name].keys().__contains__('Day'):
            base = daily_to_monthly_energy(file_name, location_name, name)
            base = base.drop('Interpolate', axis=1)
        else:    
            base = hdf5_to_dataframe(file_name,location_name, name )
            base = base.drop('Interpolate', axis=1)
    # read data


        base['Energy'] = base['Energy']/capacity
        location = pd.merge(location, base, on = ['Month', 'Year'], how='outer',suffixes=(a, a+1))
        a = a+1

    # set up a dataframe to store TMY2&3 ac_monthly
    pv = pd.DataFrame()
    
    #call the function
    TMY2 = pvwatts_tmy2(lattitude,longitude)
    TMY3 = pvwatts_tmy3(lattitude,longitude)
    
    if TMY2.empty ==True:
        
        pv['TMY3'] =pvwatts_tmy3(lattitude,longitude).ac_monthly
        pv['Month'] = [1,2,3,4,5,6,7,8,9,10,11,12]

        result = pd.merge(location, pv, on = ['Month'], how='outer' )
    #merge PVWatts data into location data


        result['Date'] = ""
    # Change the date into a datetime format
        for i in range(len(result)):
            result['Date'][i] = str(result['Year'][i]) + '-' + str(result['Month'][i])    
            result['Date'] = pd.to_datetime(result['Date'])


        result = result.sort_values(by='Date')
    # sort by date

        xaxis=result['Date']  
    # setting x axis with Date

        tmy3 = result['TMY3']/18
    # store tmy2&3 data

        result = result.drop(['Date', 'Month', 'Year', 'TMY3'], axis=1)
    
    # delet Date column to calculate median value and maxium value

        result['Mean'] = result.mean(1)
        result["STD"] = result.std(1)
    # adding median and max value into dataframe


        xs = xaxis
        yerrs = result['STD']
        ys = result['Mean']

        output_notebook()
        output_file('errorbar_'+location_name+'.html')

    # plot the points
        p = figure(x_axis_type='datetime', width=600, height=300)

        p.title.text='The Error Bar in '+location_name+' and TMY2&3'
        p.title.align = 'center'
        p.title.text_font_size = "15px"
        p.title.text_font = "times"
        p.title.text_font_style = "italic"
 

        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'AC kWh produced/DC kW installed (kWh/kW)'



    # create the coordinates for the errorbars
        err_xs = []
        err_ys = []

        for x, y, yerr in zip(xs, ys, yerrs):
            err_xs.append((x, x))
            err_ys.append((y - yerr, y + yerr))

        p.vbar(x=xaxis, width=1, bottom=0,
               top=result['Mean'], color="firebrick")
    # plot them


        r0 = p.circle(xs, ys, color='red', size=4, line_alpha=0)      #Mean

        r1 = p.multi_line(err_xs, err_ys, color='blue')                #STD

        r3 = p.line(xaxis, tmy3, line_width=1, color='orange')         #TMY3    
        #add legend outside of figure
        legend = Legend(items=[
        ("Mean"   , [r0]),
        ("STD" , [r1]),
        ("TMY3" , [r3]),
        ], location="center")
        p.add_layout(legend, 'right')
 

        p.legend.click_policy="hide"
    # interactive control

        show(p)
    else:
        pv['TMY2'] = pvwatts_tmy2(lattitude,longitude).ac_monthly
        pv['TMY3'] =pvwatts_tmy3(lattitude,longitude).ac_monthly
        pv['Month'] = [1,2,3,4,5,6,7,8,9,10,11,12]

        result = pd.merge(location, pv, on = ['Month'], how='outer' )
    #merge PVWatts data into location data


        result['Date'] = ""
    # Change the date into a datetime format
        for i in range(len(result)):
            result['Date'][i] = str(result['Year'][i]) + '-' + str(result['Month'][i])    
            result['Date'] = pd.to_datetime(result['Date'])


        result = result.sort_values(by='Date')
    # sort by date

        xaxis=result['Date']  
    # setting x axis with Date
        tmy2 = result['TMY2']/18
        tmy3 = result['TMY3']/18
    # store tmy2&3 data

        result = result.drop(['Date', 'Month', 'Year', 'TMY2', 'TMY3'], axis=1)
    
    # delet Date column to calculate median value and maxium value

        result['Mean'] = result.mean(1)
        result["STD"] = result.std(1)
    # adding median and max value into dataframe


        xs = xaxis
        yerrs = result['STD']
        ys = result['Mean']

        output_notebook()
        output_file('errorbar_'+location_name+'.html')

    # plot the points
        p = figure(x_axis_type='datetime', width=600, height=300)

        p.title.text='The Error Bar in '+location_name+' and TMY3'
        p.title.align = 'center'
        p.title.text_font_size = "15px"
        p.title.text_font = "times"
        p.title.text_font_style = "italic"
 

        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'AC kWh produced/DC kW installed (kWh/kW)'



    # create the coordinates for the errorbars
        err_xs = []
        err_ys = []

        for x, y, yerr in zip(xs, ys, yerrs):
            err_xs.append((x, x))
            err_ys.append((y - yerr, y + yerr))

        p.vbar(x=xaxis, width=1, bottom=0,
               top=result['Mean'], color="firebrick")
    # plot them


        r0 = p.circle(xs, ys, color='red', size=4, line_alpha=0)      #Mean

        r1 = p.multi_line(err_xs, err_ys, color='blue')                #STD
        r2 = p.line(xaxis, tmy2, line_width=1, color='green')          #TMY2
        r3 = p.line(xaxis, tmy3, line_width=1, color='orange')         #TMY3    
        #add legend outside of figure
        legend = Legend(items=[
        ("Mean"   , [r0]),
        ("STD" , [r1]),
        ("TMY2" , [r2]),
        ("TMY3" , [r3]),
        ], location="center")
        p.add_layout(legend, 'right')
        p.legend.click_policy="hide"
        show(p)

