import os
import folium
import pandas as pd
import branca
from ARCTIC import supplyinfo


def read_file(file_path):
    all_the_text = open(file_path).read()
    # print type(all_the_text)
    return all_the_text

def map(file_name,coordinate):
    
    '''
    This function is used to generate a folium map with Alaska in the center. 
    At the same time, there are a lot of pins on it. You can click the pin and a figure pop out.
    You need hdf5 file and a dataframe with locations and coordinate.
    For the figures in popup, you need the figure file in html named 'popup_name.html'
    
    input: hdf5 file_name, the dataframe with location and coordinate.
    output: HTML file with Alaska map named 'map.html'. 
    '''
    
    alaska= folium.Map(location = [63.977161, -152.024667], zoom_start = 4)
    for i in range(len(coordinate)):
        loc = coordinate['location'][i]
        popupfigure = read_file("popup_"+loc+".html")

        tab = supplyinfo.table("solar_panel_data_alaska",loc,
                               coordinate['latitude'][i],coordinate['longitude'][i])

        html = """
            <p align='center' style="font-size:35px;margin:0.5px 0"><b>{1}</b></p >
            {0}
            <p style="font-size:10px;margin:1px 0"><i style="color:grey">Click on the legend entries to hide or show the data.</i> 
            {2}
             <p>For more information, and to explore the data in greater detail, please click the arrow.</p>
             <a href="https://acep-solar.github.io/ACEP_solar/webpages/{1}.html" target="_blank" title="Go ahead">
        <img border="0" src="https://acep-solar.github.io/ACEP_solar/All_figures/arrow.jpeg" alt="Click Here" width="110" height="68"></a></p>

        """
        html = html.format(popupfigure,loc,tab)


        iframe = branca.element.IFrame(html = html, width=650, height=400)
        popup = folium.Popup(iframe, max_width=850)

        folium.Marker([coordinate['latitude'][i], coordinate['longitude'][i]], popup = popup, 
                      tooltip = loc + ', AK.').add_to(alaska)
    alaska.save(os.path.join( 'map.html'))