import h5py
import hdf5_interface
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label, Legend
import requests
from bokeh.palettes import Spectral4

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

