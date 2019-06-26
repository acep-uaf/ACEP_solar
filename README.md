# ACEP Solar - ARCTIC

***

Data Driven Solar Performance Analysis for Alaska

**Development Team Members** - Ge Gu, Jon Onorato, Zhi Peng

**Advisory Team Members** - Christopher Pike, George Roe, Erin Whitney, Michelle Wilber

This project objective is to calculate a number of different parameters and metrics for solar installations distributed throughout the state of Alaska, and generate an interactive graphic that enables users to investigate the costs and benefits to solar in their area, as well as provide a means to investigate if their installations are underperforming expected performance. The goal of this project is to be able to do all of this while enabling end-users to not need to download any specialized software or to have any coding experience. From this, all of the data is exported and presented in an HTML format, which is currently hosted on the associated github website. 

***

To interact with this software, the first step is to run the setup.py file to install access to our packages. Do so by opening your terminal, and typing in `python setup.py install`. Note that you'll have to repeat this procedure after every time you make changes to these functions, otherwise your function changes won't be used.

The general workflow of this software is to first organize your data into a specific format in an excel or .csv  document. For a template, we've included the "example.xlsx" file to show what the software expects. After organizing, the data can be loaded into an HDF5 file for storage and easy access. During this storage process, it's possible to enable an regression function that can predict the values of any missing data in your workbook, and add that information. Following HDF5 storage, the next step is to generate all of the interactive graphics, rendered in HTML, using Bokeh. Finally, those Bokeh HTML graphics will be placed into either a Folium popup, or the "extra information" tab of data in each location. 

Each of these steps has a Jupyter notebook that should provide clarity on how to interact with our functions, and specific details on how to run each of these steps. Find these demonstrations in the "Demonstrations and Examples" folder. 

Thank you for reading our README. We're excited to have you here and using our tool. 
--The ARCTIC Dev Team
