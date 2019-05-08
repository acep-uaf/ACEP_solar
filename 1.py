import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox


nrel_long_tilt = []
tilts = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
for i in tilts:
    list_parameters = {"format": 'JSON', "api_key": "spJFj2l5ghY5jwk7dNfVYs3JHbpR6BOGHQNO8Y9Z", "system_capacity": 4, "module_type": 0, "losses": 14.08,
              "array_type": 0, "tilt": i, "azimuth": 180, "lat": 64.82, "lon": -147.87, "dataset": 'tmy2'}
    json_response = requests.get("https://developer.nrel.gov/api/pvwatts/v6", params = list_parameters).json()
    new_dataframe = pd.DataFrame(data = json_response['outputs'])
    nrel_long_tilt.append(new_dataframe)


fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
x = range(1,13)
y = nrel_long_tilt[0]['ac_monthly']
initial_text = "5"
l, = plt.plot(x, y, lw=2)


def submit(text):
    if text == '10':
        l.set_ydata(nrel_long_tilt[1]['ac_monthly'])
    elif text == '15':
        l.set_ydata(nrel_long_tilt[2]['ac_monthly'])
    elif text == '5':
        l.set_ydata(nrel_long_tilt[0]['ac_montnly'])
    elif text == '20':
        l.set_ydata(nrel_long_tilt[3]['ac_monthly'])
    elif text == '25':
        l.set_ydata(nrel_long_tilt[4]['ac_monthly'])
    else:
        l.set_ydata(nrel_long_tilt[5]['ac_monthly'])
    plt.draw()

axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
text_box = TextBox(axbox, 'Tilt=', initial=initial_text)
text_box.on_submit(submit)

plt.show()
