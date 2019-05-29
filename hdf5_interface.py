"""These functions enable the interaction with an HDF5 file for storing solar data."""

import os
import pandas as pd
import numpy as np

def create_hdf5_file(hdf5_filename):
    """Function to initialize the hdf5 file type on your computer"""
    #Initialize the file with the name that is passed
    #the 'w-' command throws an error if a duplicate filename is passed
    solar_data_storage = h5py.File('{}.hdf5'.format(hdf5_filename), 'w-')

def add_to_hdf5_file(filename, data_filename, panel_name, location):
    """This function assumes a specific layout in a pandas dataframe for a single solar panel,
    and takes that data and adds it into an hdf5 file with the name that is passed."""
    #Have a quick conversion that converts all the text inputs to lowercase.

    #Check to see if the HDF5 file exists, otherwise pass info on how to create it.
    if os.path.exists('{}.hdf5'.format(hdf5_filename)):
        hdf5_file = h5py.File('{}.hdf5'.format(hdf5_filename), 'w')
    else:
        raise PathError("The passed HDF5 filename does not exist."
                        "Run the `create_hdf5_file` function to create it")

    #Structure is to check to see if location exists already in the hdf5. If it does, then navigate to under it
    #If it doesn't, then create the location, and navigate to under it. Then, add this data under
    #The name that is passed as panel_name.
    location_finder = 0
    #Check to see if the location already exists in the HDF5 Structure:
    for names in hdf5_file.keys():
        if names == location:
            print("This location already exists. Navigating there now.")
            hdf5_location_group = hdf5_file.get(location)
            location_finder = 1
    #If the location didn't already exist, this will create it in the HDF5 structure.
    if location_finder == 0:
        hdf5_location_group = hdf5_file.create_group(str(location))

    #Check to be sure that the panel doesn't already exist. If it does, raise an error.
    for names in hdf5_location_group.keys():
        if names == panel_name:
            print("You've already entered this panel's data!")
            print("You should use the `update_panel_data` function instead.")
            raise OverwriteError("This panel already exists in the HDF5 structure")
    #If it doesn't exist, then make a group for it to place all the datasets within
    panel_data = hdf5_location_group.create_group(panel_name)

    #Next, make a call to load the data from the excel file into a dataframe.
    solar_dataframe = extract_file_to_dataframe(data_filename)

    #Ok, now we'll create all the datasets within that group at that location from the dataframe
    panel_data_energy = panel_data.create_dataset("Energy", solar_dataframe['Energy'])
    panel_data_month = panel_data.create_dataset("Month", solar_dataframe['Month'])
    panel_data_year = panel_data.create_dataset("Year", solar_dataframe['Year'])

    #Finally, we'll update the attributes of the panel with its DC Capacity
    panel_data.attrs.create('DC Capacity', solar_dataframe['DC Capacity'][0])

    #Then close the HDF5 file to make sure no accidental writings occur.
    hdf5_file.close()

def update_existing_panel_entry(hdf5_filename, data_filename, panel_name, location):
    """This function updates panel entries in the HDF5 file with new data"""
    #First, check to see if that panel data already exists, otherwise raise errors
    if os.path.exists('{}.hdf5'.format(hdf5_filename)):
        hdf5_file = h5py.File('{}.hdf5'.format(hdf5_filename), 'w')
    else:
        raise PathError("The passed HDF5 filename does not exist."
                        "Run the `create_hdf5_file` function to create it")
    panel_location = hdf5_file.get(location)
    if panel_location == None:
        raise PathError("The passed panel location does not exist in"
                       "the hdf5 file. Check the location info.")
    panel_name_hdf5 = panel_location.get(panel_location)
    if panel_name_hdf5 == None:
        raise PathError("The passed panel name does not exist in the"
                        "hdf5 file. Add it to the file using `add_to_hdf5_file` function")

    #Next, make a call to load the data from the excel file into a dataframe.
    solar_dataframe = extract_file_to_dataframe(data_filename)

    #Now, we need to update the information stored in that panel entry.
    #First, we delete the existing entry, then we add the new data.
    del panel_name_hdf5['Energy']
    panel_name_hdf5['Energy'] = solar_dataframe['Energy']

    #Then repeat for all of the entries.
    del panel_name_hdf5['Month']
    panel_name_hdf5['Month'] = solar_dataframe['Month']
    del panel_name_hdf5['Year']
    panel_name_hdf5['Year'] = solar_dataframe['Year']

    #Attributes are nice, and can just be updated.
    panel_name_hdf5.attrs.__setitem__('DC Capacity', solar_dataframe['DC Capacity'][0])

    #And close the file, to keep things neat.
    hdf5_file.close()

def extract_file_to_dataframe(filename):
    """This takes a data file name, and extracts it into a pandas dataframe.
    The dataframe is then returned."""
    #Check for either a csv or an excel spreadsheet filetype.
    if filename.split('.')[-1] == 'xlsx':
        dataframe = pd.read_excel(filename)
    elif data_filename.split('.')[-1] == 'csv':
        dataframe = pd.read_csv(data_filename)
    else:
        raise TypeError("The file's datatype was not recognized. Please insert an xslx or csv file")
    return dataframe
