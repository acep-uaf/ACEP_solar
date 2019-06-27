import numpy as np
import pandas as pd
import h5py
import hdf5_interface
import requests
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

def table(file_name,location_name, latitude, longitude):
    
    
    '''
    input: file_name,location_name, latitude, longitude
    oytput: HTML language with location,#of installation,average_capacity,
                                     average_annual,TMY2_acannual,TMY3_acannual.
                                     
    You can get the general information of solar system in one location of Alaska.
    Those supply information is for the table in popup figure and secondary webpage.
    '''
    my_file = h5py.File(file_name+'.h5', 'r')
    result = pd.DataFrame(columns = ['Parameter','Value'])
    result['Parameter'] = ['Location','The Number of Installation','Average DC Capacity(kW)',
                         'Normalized Average Annual Production(kWh)','TMY2 Annual Production(kWh)',
                           'TMY3 Annual Production(kWh)']

    result.loc[0,'Value'] = location_name
    location_hdf5 = my_file.get(location_name)
    location=pd.DataFrame(columns=['Date'])
    a = []
    ca = []
    no=0
    for name in location_hdf5:
        no = no+1
        capacity = location_hdf5[name].attrs.__getitem__("DC Capacity")
        ca.append(capacity)
        if location_hdf5[name].keys().__contains__('Day'):
            base = daily_to_monthly_energy(file_name, location_name, name)
        else:    
            base = hdf5_to_dataframe(file_name,location_name, name )
                    # read data
        base = base.drop(['Year', 'Interpolate'], axis=1)    
        average = base.groupby('Month').mean()
        summation = np.sum(average,axis=0)/capacity
        a.append(float(summation))
    result.loc[2,'Value'] = np.mean(ca)    
    result.loc[3,'Value'] = np.mean(a)
    result.loc[1,'Value'] = no

            # to test if each loation has TMY2 data
    tmy2=pvwatts_tmy2(latitude,longitude)   
    if tmy2.empty == 1:
        pass
    else:
        result.loc[4,'Value'] = tmy2['ac_annual'][0]/18
    result.loc[5,'Value'] = pvwatts_tmy3(latitude,longitude)['ac_annual'][0]/18

    return result.to_html(justify = 'center',index=False).replace('\n','')