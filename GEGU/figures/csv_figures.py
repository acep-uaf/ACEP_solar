import pandas as pd
import numpy as np


def add_time_col(dataframe):
    """This function can extract the date in the specific format of the dataframe 
       and then create a new column in the dataframe showing the date in the form of the the datetime
       
       Args:
           dataframe(string):The name of the dataframe you want to adjust
       
       Returns:
           A new dataframe with the same name.
    """
    
    # Creating a dictionary that we can use to replace the string to int
    month_change = {'November':11,'December':12,'January': 1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10}
    
    # Check if the input is a dataframe, if not,it won't give the right
    #assert dataframe == pd.DataFrame,"The input should be a dataframe"
    
    # if the input is a dataframe, then we can adjust it
    dataframe['Month'] = dataframe['Month'].map(month_change)
    dataframe['Date'] = ""
    for i in range(len(dataframe)):
        dataframe['Date'][i] = str(dataframe['Year'][i]) + '-' + str(dataframe['Month'][i])
    
    # Change the date into a datetime format
    dataframe['Date'] = pd.to_datetime(dataframe['Date'])
    
    # Since we have a column that shows the 'orderable' format in date, then we can drop the original one
    dataframe.drop(['Year','Month'],axis = 1,inplace = True)
    order = ['Date','Energy','DC Capacity','Location']
    dataframe_new = dataframe[order]
    
    return(dataframe_new)

def annual_Norm(dataframe):
    """This is a function that calculateing the annual production of the panel
       
       Args:
           dataframe(string):The name of the dataframe you want to adjust
       
       Returns:
           annual_values(list): the sum of the past 12 months energy production
           month(list):the month corresponding to the annual_values
         
    """
    # create three list
    lenth_list = list(range(12,len(dataframe.index)))
    annual_values = []
    month = []
    for i in range(len(lenth_list)):
        single_values = dataframe['Energy'][lenth_list[i]-12:lenth_list[i]].sum()/dataframe['DC Capacity'][0]
        #rolling_average.append(each_period)
        single_month = dataframe['Date'][lenth_list[i]]
        # append the result we want to the list
        annual_values.append(single_values)
        month.append(single_month)    
    month.pop(0) # Here we drop the first month data
    annual_values.pop(0)
    
    return(annual_values,month)
