import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


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


def filled_missingdata_with_ML(dataframe):
    
    """
    This is a function that using machine learning in 'polynomial' that in SKLEARN to predict the missing data 
    and will return to a dataframe which has the predicted data and with a new column name 'status' with 0 
    representing that this data is an asumption.
    
    Args:
       dataframe(DataFrame):name of the dataframe which has missing data
       
    Returns:
       dataframe
    
    """
    
    # drop the 'DC capacity' & 'Location' columns cause if will influence the 'isnan' judgement.
    dataframe_with_missing = dataframe.drop(['DC Capacity','Location'],axis=1)
    
    # change the 'month' to the number instead of 'words'
    month_change = {'November':11,'December':12,'January': 1,
                'February':2,'March':3,'April':4,'May':5,
                'June':6,'July':7,'August':8,'September':9,'October':10}
    dataframe_with_missing['Month'] = dataframe_with_missing['Month'].map(month_change)
    
    # get the 'date' that has the missing data
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
    poly = PolynomialFeatures(degree=8)
    
    # Transfer the preditor into poly way
    X_train = poly.fit_transform(x_list)
    x_need_predict_transfer = poly.fit_transform(x_need_predict)
    
    # Instantiate
    lg = LinearRegression()
    
    # Fit
    lg.fit(X_train, y_list)
    
    # Predict
    y_predicted = lg.predict(x_need_predict_transfer)
    
    # put the predicted data back (actually create a new dataframe with predicted data)
    list_of_predicted = y_predicted.tolist()
    fill = pd.DataFrame(index=index_of_missing,data=list_of_predicted,columns=['Energy'])
    dataframe_with_predicted = dataframe.fillna(fill)
    
    # create a new column in dataframe name 'status'
    dataframe_with_predicted['Status'] = ""
    for i in index_of_missing:
        dataframe_with_predicted['Status'][i] = 0
        
    return(dataframe_with_predicted)
