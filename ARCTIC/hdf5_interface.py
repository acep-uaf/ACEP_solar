"""These functions enable the interaction with an HDF5 file for storing solar data."""

import os
import h5py
import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

def create_hdf5_file(hdf5_filename):
    """Function to initialize the hdf5 file type on your computer"""
    #Initialize the file with the name that is passed
    #the 'w-' command throws an error if a duplicate filename is passed
    solar_data_storage = h5py.File('{}.h5'.format(hdf5_filename), 'w-')
    solar_data_storage.close()

def add_to_hdf5_file(hdf5_filename, data_filename, panel_name, interpolate = False, polynomial_order = 5):
    """This function assumes a specific layout in a pandas dataframe for a single solar panel,
    and takes that data and adds it into an hdf5 file with the name that is passed."""
    #Have a quick conversion that converts all the text inputs to lowercase.

    #Check to see if the HDF5 file exists, otherwise pass info on how to create it.
    if os.path.exists('{}.h5'.format(hdf5_filename)):
        hdf5_file = h5py.File('{}.h5'.format(hdf5_filename), 'r+')
    else:
        raise ValueError("The passed HDF5 filename does not exist."
                        "Run the `create_hdf5_file` function to create it")

    #First, make a call to load the data from the excel file into a dataframe.
    solar_dataframe = extract_file_to_dataframe(data_filename)

    location_finder = 0
    #Check to see if the location already exists in the HDF5 Structure:
    for names in hdf5_file.keys():
        if names == solar_dataframe['Location'][0]:
            print("This location already exists. Navigating there now.")
            hdf5_location_group = hdf5_file.get(solar_dataframe['Location'][0])
            location_finder = 1
    #If the location didn't already exist, this will create it in the HDF5 structure.
    if location_finder == 0:
        hdf5_location_group = hdf5_file.create_group(str(solar_dataframe['Location'][0]))

    #Check to be sure that the panel doesn't already exist. If it does, raise an error.
    for names in hdf5_location_group.keys():
        if names == panel_name:
            print("You've already entered this panel's data!")
            print("You should use the `update_panel_data` function instead.")
            hdf5_file.close()
            raise ValueError("This panel already exists in the HDF5 structure")
    #If it doesn't exist, then make a group for it to place all the datasets within
    panel_data = hdf5_location_group.create_group(panel_name)
    
    #Check if interpolation is needed. If so, call the interpolation function.
    if interpolate == True:
        solar_dataframe = interpolate_missing_data(solar_dataframe, polynomial_order)

    #GOOD OPPORTUNITY FOR A TEST - NEED TO BE SURE ALL ARE THE SAME LENGTH
    #Make numpy arrays for energy and year values.
    energy_array = solar_dataframe.loc[:,'Energy'].values
    year_array = solar_dataframe.loc[:,'Year'].values
    interpolation_array = solar_dataframe.loc[:, 'Interpolate'].values
    #Check if data is broken down by daily production
    if 'day' in solar_dataframe.columns:
        day_array = solar_dataframe.loc[:,'Day'].values
        panel_data_day = panel_data.create_dataset("Day", data = day_array)
    #Convert month names from strings to int values
    month_list = month_string_to_int(solar_dataframe)
    #load all of the data into the HDF5 file.
    panel_data_energy = panel_data.create_dataset("Energy", data = energy_array)
    panel_data_month = panel_data.create_dataset("Month", data = month_list)
    panel_data_year = panel_data.create_dataset("Year", data = year_array)
    panel_data_interpolation = panel_data.create_dataset("Interpolate", 
                                                         data = interpolation_array)

    #Finally, we'll update the attributes of the panel with its DC Capacity
    panel_data.attrs.create('DC Capacity', solar_dataframe['DC Capacity'][0])

    #Then close the HDF5 file to make sure no accidental writings occur.
    hdf5_file.close()

def update_existing_panel_entry(hdf5_filename, data_filename, panel_name, interpolate = False, polynomial_order = 5):
    """This function updates panel entries in the HDF5 file with new data"""
    #First, check to see if that panel data already exists, otherwise raise errors
    if os.path.exists('{}.h5'.format(hdf5_filename)):
        hdf5_file = h5py.File('{}.h5'.format(hdf5_filename), 'r+')
    else:
        raise ValueError("The passed HDF5 filename does not exist."
                        "Run the `create_hdf5_file` function to create it")

    #Next, load the dataframe to check the location
    solar_dataframe = extract_file_to_dataframe(data_filename)
    #Check the HDF5 to make sure the location exists, then load it from the file
    panel_location = hdf5_file.get(solar_dataframe['Location'][0])
    if panel_location == None:
        print("Panel Location" + str(panel_location))
        hdf5_file.close()
        raise ValueError("The passed panel location does not exist in "
                       "the hdf5 file. Check the location info.")
    #Check to see if the panel exists, and if so load it from the file
    panel_name_hdf5 = panel_location.get(panel_name)
    if panel_name_hdf5 == None:
        print(panel_name_hdf5)
        print(panel_location)
        print(solar_dataframe['Location'][0])
        hdf5_file.close()
        raise ValueError("The passed panel name does not exist in the"
                        "hdf5 file. Add it to the file using `add_to_hdf5_file` function")

    #Check if interpolation is needed. If so, call the interpolation function.
    if interpolate == True:
        solar_dataframe = interpolate_missing_data(solar_dataframe, polynomial_order)
    
    #Now, we need to update the information stored in that panel entry.
    #First, we delete the existing entry, then we add the new data.
    
    #For "Day", check if it exists in the HDF5 file already.
    if panel_name_hdf5.__contains__("Day"):
        #Check that the dataframe also contains a "day" column
        if "Day" in solar_dataframe.columns:
            del panel_name_hdf5['Day']
            panel_name_hdf5['Day'] = solar_dataframe['Day']
        #Check what user wants to do if new data doesn't have "Day"
        #But old data did.
        elif "Day" not in solar_dataframe.columns:
            print("Are you sure you want to delete the day column, when the "
                  "new data does not contain any daily information? ")
            delete = input("Type 'y' for yes, and 'n' for no.")
            if delete == 'y':
                del panel_name_hdf5['Day']
            elif delete == 'n':
                hdf5_file.close()
                raise ValueError("User declined to progress. Check data being input.")
    elif 'Day' in solar_dataframe.columns:
        panel_name_hdf5['Day'] = solar_dataframe['Day']
        
    ##NEED TO NEST THIS IN AN IF, AND ONLY CALL IT IF THAT DATASET EXISTS
    if panel_name_hdf5.__contains__('Energy'):
        del panel_name_hdf5['Energy']
    panel_name_hdf5['Energy'] = solar_dataframe['Energy']

    #Then repeat for all of the entries.
    if panel_name_hdf5.__contains__('Month'):
        del panel_name_hdf5['Month']
    month_list = month_string_to_int(solar_dataframe)
    panel_name_month = panel_name_hdf5.create_dataset("Month", data = month_list)
    
    if panel_name_hdf5.__contains__('Year'):
        del panel_name_hdf5['Year']
    panel_name_hdf5['Year'] = solar_dataframe['Year']
    
    if panel_name_hdf5.__contains__('Interpolate'):
        del panel_name_hdf5['Interpolate']
    panel_name_hdf5['Interpolate'] = solar_dataframe['Interpolate']
                            
    #Attributes are nice, and can just be updated.
    panel_name_hdf5.attrs.__setitem__('DC Capacity', solar_dataframe['DC Capacity'][0])

    #And close the file, to keep things neat.
    hdf5_file.close()

def delete_panel(hdf5_filename, location_name, panel_name):
    """This function takes in a panel name and deletes that panel from the HDF5 file"""
    #First, check to see if the hdf5 file exists, otherwise raise errors
    if os.path.exists('{}.h5'.format(hdf5_filename)):
        hdf5_file = h5py.File('{}.h5'.format(hdf5_filename), 'r+')
    else:
        raise ValueError("The passed HDF5 filename does not exist."
                        "Check to see if a there are typos in the filename")
    
    #Ok, now check to see if the panel location exists in the HDF5 file
    panel_location = hdf5_file.get(location_name)
    if panel_location == None:
        print("Panel Location" + str(panel_location))
        hdf5_file.close()
        raise ValueError("The passed panel location does not exist in "
                       "the hdf5 file. Check the location info.")
        
    #Check to see if the panel exists
    panel_name_hdf5 = panel_location.get(panel_name)
    if panel_name_hdf5 == None:
        print(panel_name_hdf5)
        print(panel_location)
        print(solar_dataframe['Location'][0])
        hdf5_file.close()
        raise ValueError("The passed panel name does not exist in the"
                        "hdf5 file. Add it to the file using `add_to_hdf5_file` function")

    #Prompt the user one last time to make sure they want to delete this file.
    print("Are you sure you want to delete this panel?")
    delete = input("Type 'y' for yes, and 'n' for no.")
    if delete == 'y':
        print(panel_name_hdf5)
        del panel_location[str(panel_name)]
        print("It's deleted")
    elif delete == 'n':
        hdf5_file.close()
        raise ValueError("User declined to progress. Check data being input.")
    hdf5_file.close()

def extract_file_to_dataframe(filename):
    """This takes a data file name, and extracts it into a pandas dataframe.
    The dataframe is then returned."""
    #Check for either a csv or an excel spreadsheet filetype.
    if filename.split('.')[-1] == 'xlsx':
        dataframe = pd.read_excel(filename)
    elif filename.split('.')[-1] == 'csv':
        dataframe = pd.read_csv(filename)
    else:
        raise TypeError("The file's datatype was not recognized. Please insert an xlsx or csv file")
        
    #In this code, we'll need to check over everything and make sure it's in the 
    #right/expected format, to make sure our other programs don't break.
    return dataframe

def month_string_to_int(solar_dataframe):
    """This function translates string values for months into their integer representations"""
    #Use a dictionary to map text to integer values for the months - HDF5 needs no strings
    month_change = {'January':1,'February':2,'March':3,'April':4, 'May':5,'June':6,'July':7,
                'August':8,'September':9,'October':10, 'November':11,'December':12, 'Jan': 1,
               'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
               'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12} 
    month_list = list(solar_dataframe['Month'].map(month_change).fillna(solar_dataframe['Month']))
    return month_list

def hdf5_to_dataframe(hdf5_filename, location_name, panel_name):
    """This function extracts data from an HDF5 file and loads it into a pandas dataframe"""
    #Load the HDF5 file data
    hdf5_file = h5py.File('{}.h5'.format(hdf5_filename), 'r')
    hdf5_location = hdf5_file.get(location_name)
    panel_location = hdf5_location.get(panel_name)
    dataframe = pd.DataFrame()
    for keys in panel_location.keys():
        dataframe[str(keys)] = panel_location[str(keys)][:]
    #Also need to pull out the DC Capacity and Locations:
    dataframe['DC Capacity'] = ""
    dataframe['Location'] = ""
    dataframe['DC Capacity'][0] = panel_location.attrs.__getitem__('DC Capacity')
    dataframe['Location'][0] = str(location_name)
    hdf5_file.close()
    return dataframe

def interpolate_missing_data(dataframe, polynomial_order = 5):
    
    """
    This is a function that using machine learning in 'polynomial' that in SKLEARN to predict the missing data 
    and will return to a dataframe which has the predicted data and with a new column name 'status' with 0 
    representing that this data is an asumption.
    
    Args:
       dataframe(DataFrame):name of the dataframe which has missing data
       polynomial_order(int): order of polynomial used to fit missing data
       
    Returns:
       dataframe_with_predicted(DataFrame): A dataframe with any missing values replaced by interpolated values
    
    """
    
    #drop the 'DC capacity' & 'Location' columns. They contain NaNs and will influence the 'isnan' judgement.
    dataframe_with_missing = dataframe.drop(['DC Capacity', 'Location'], axis=1)
    
    # change the 'month' to the number instead of 'words'
    month_change = {'January':1,'February':2,'March':3,'April':4, 'May':5,'June':6,'July':7,
                'August':8,'September':9,'October':10, 'November':11,'December':12, 'Jan': 1,
               'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
               'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12} 
    dataframe_with_missing['Month'] = dataframe_with_missing['Month'].map(month_change)
    
    # Find the 'dates' that have missing data
    list_of_missing = []
    index_of_missing = []
    for i in range(len(dataframe_with_missing)):
        if np.isnan(dataframe_with_missing['Energy'][i]) == True:
            index_of_missing.append(i)
            year_month = [dataframe_with_missing['Year'][i],dataframe_with_missing['Month'][i]]
            list_of_missing.append(year_month)
            
    #drop the missing data
    dataframe_without_missing = dataframe_with_missing.dropna()
    dataframe_without_missing.reset_index(drop=True,inplace=True)
    
    #creating the x,y to train the model
    x_list=[]
    for i in range(len(dataframe_without_missing)):
        a = [dataframe_without_missing['Year'][i],dataframe_without_missing['Month'][i]]
        x_list.append(a)

    y_list=[]
    for i in range(len(dataframe_without_missing)):
        b = dataframe_without_missing['Energy'][i]
        y_list.append(b)
    
    # preparing the x_need_predicted for the model
    x_need_predict=list_of_missing
    
    # design the model
    poly = PolynomialFeatures(degree=polynomial_order)
    
    # Transfer the preditor into poly way
    x_train = poly.fit_transform(x_list)
    x_need_predict_transfer = poly.fit_transform(x_need_predict)
    
    # Instantiate the model
    lg = LinearRegression()
    
    # Run the actual fit on the model
    lg.fit(x_train, y_list)
    
    # Use the model that you fit to predict the new data
    y_predicted = lg.predict(x_need_predict_transfer)
    
    # Combine the new, predicted data with the old dataframe.
    list_of_predicted = y_predicted.tolist()
    fill = pd.DataFrame(index=index_of_missing,data=list_of_predicted,columns=['Energy'])
    dataframe_with_predicted = dataframe.fillna(fill)
    
    # Update any interpolated values to give them a value of 1.
    for i in index_of_missing:
        dataframe_with_predicted['Interpolate'][i] = 1
    
    for i in range(len(index_of_missing)):
        if dataframe_with_predicted['Energy'][i] < 0:
            dataframe_with_predicted['Energy'][i] = 0
        else:
            pass
        
    return(dataframe_with_predicted)