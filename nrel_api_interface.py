"""This file contains a number of functions to interact with the NREL API quickly,
enabling users to explore what NREL's PVWatts tool returns after function calls."""

import requests
import json
import numpy as np
import pandas as pd

def check_all_datasets(latitude, longitude, tilt, azimuth = 180):
    """This function checks all solar resource datasets, and generates a dataframe for each dataset.
    Returned parameters are collected and returned in a dictionary. The dictionary
    has keys that are the names of the solar resource datasets that actually returned data,
    and values that are the outputs from PVWatts (ie, the production predictions)"""
    #List of all of the available solar resource datasets from the PVWatts website.
    dataset_list = ['tmy2', 'tmy3', 'nsrdb', 'intl']
    solar_resource_dict = {}
    #Walk through the list, and check what is available at the lat and long provided.
    for counter, value in enumerate(dataset_list):
        #Call PVWatts API, and get response for specific tilt angle.
        parameters = {"format": 'JSON', "api_key": "2FGNWhrV7X5olr1eVu34xpySQLDytnRKKQtSOeI8",
		      "system_capacity": 4,
                      "module_type": 0, "losses": 14.08, "array_type": 0, "tilt": tilt, "azimuth": azimuth,
                      "lat": latitude, "lon": longitude, "dataset": dataset_list[counter]}
        pvwatts_response = requests.get("https://developer.nrel.gov/api/pvwatts/v6", params = parameters)
        #Check the response from pvwatts to ensure that data was actually received
        #assert pvwatts_response.status_code == 200, "Error: " + str(pvwatts_response.status_code)
        #Convert the requests response into json
        pvwatts_response_json = pvwatts_response.json()
        #The response gives an empty list in the errors parameter if it was able to find the data.
        if pvwatts_response_json['errors'] == []:
            solar_resource_dict[str(dataset_list[counter])] = pvwatts_response_json['outputs']
            print("Added response data from: " + str(dataset_list[counter]) + " solar resource data.")
        else:
            print("The solar resource data from dataset " + str(dataset_list[counter]) + 
                  " at that location is not available.")
            print("We'll try again with other solar resource datasets!")
    print("We found prediction data from these solar resource datasets: " )
    print(solar_resource_dict.keys())
    return solar_resource_dict


def call_pvwatts(latitude, longitude, tilt, dataset, azimuth = 180):
    """This function calls the PVWatts API from NREL, and returns a dataframe of 
    expected power production from a cell with given position and tilt"""
    if not isinstance(latitude, (int, float)):
        raise TypeError("Passed latitude is not a number! Instead, it is: " + str(type(Testing_DataFrame)))
        
    #Call PVWatts API, and get response for specific tilt angle.
    parameters = {"format": 'JSON', "api_key": "2FGNWhrV7X5olr1eVu34xpySQLDytnRKKQtSOeI8", "system_capacity": 4, 
                  "module_type": 0, "losses": 14.08, "array_type": 0, "tilt": tilt, "azimuth": azimuth, 
                  "lat": latitude, "lon": longitude, "dataset": dataset}
    pvwatts_response = requests.get("https://developer.nrel.gov/api/pvwatts/v6", params = parameters)
    
    #Check the response from pvwatts to ensure that data was actually received
    assert pvwatts_response.status_code == 200, "Error: " + str(pvwatts_reponse.status_code)
    
    #Now we convert the response into a json format - 
    pvwatts_response_json = pvwatts_response.json()
    
    #Need a quick check to make sure that there was not a problem in the way PVWatts was called
    #If PVWatts detects an error, it throw it here. 
    if pvwatts_response_json['errors'] != []:
        print("An error occured when calling PVWatts. The error was: ")
        print(pvwatts_response_json['errors'])
        print("Please correct the error and call this function again.")
        raise ResponseError("Please correct the error and call the `call_pvwatts` function again")
    
    #Load the response to a dataframe
    dataframe = pd.DataFrame(pvwatts_response_json['outputs'])
    
    return pvwatts_response_json, dataframe
