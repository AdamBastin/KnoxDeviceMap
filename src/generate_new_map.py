import branca
import folium
import folium.plugins
import requests
import json
import os
import dotenv
import threading
import random
import generate_env_file

from time import strftime, localtime
from folium.plugins import Geocoder, TagFilterButton, Fullscreen
from datetime import datetime, timedelta

env_file_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_file_path):
    print(".env file not found")
    print("Generating new .env file")
    try:
        generate_env_file.Generate()
        print("Please fill in the .env file with the necessary information")
        print("Exiting...")
    except:
        print("Failed to generate .env file")
    exit()
    
# Load the environment variables from .env file
dotenv.load_dotenv()

KNOX_URL = os.getenv("KNOX_URL")
KNOX_CLIENT_ID = os.getenv("KNOX_CLIENT_ID")
KNOX_API_KEY = os.getenv("KNOX_API_KEY")

if KNOX_URL is None or KNOX_CLIENT_ID is None or KNOX_API_KEY is None:
    print("KNOX_URL, KNOX_CLIENT_ID, or KNOX_API_KEY environment variables not set")
    exit()

DEFAULT_LATITUDE = os.getenv("DEFAULT_LATITUDE") or 0
DEFAULT_LONGITUDE = os.getenv("DEFAULT_LONGITUDE") or 0
DEFAULT_ZOOM = os.getenv("DEFAULT_ZOOM") or 20
DEFAULT_MARKER = bool(os.getenv("DEFAULT_MARKER")) or False
DEFAULT_MARKER_LATITUDE = os.getenv("DEFAULT_MARKER_LATITUDE") or 0
DEFAULT_MARKER_LONGITUDE = os.getenv("DEFAULT_MARKER_LONGITUDE") or 0
DEFAULT_MARKER_NAME = os.getenv("DEFAULT_MARKER_NAME") or ''

HOURS_BEFORE_NOT_SHOWN = int(os.getenv("HOURS_BEFORE_NOT_SHOWN")) or 5
MINUTES_BEFORE_MAX_DIM = int(os.getenv("MINUTES_BEFORE_MAX_DIM")) or 60

CATEGORY_LIST = os.getenv("CATEGORY_LIST").split(',') or None

def GetKnoxBearerToken():        
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = f'client_id={KNOX_CLIENT_ID}&client_secret={KNOX_API_KEY}&grant_type=client_credentials'
    response = requests.post(KNOX_URL + "/emm/oauth/token", headers=headers,data=payload)
    return response.json()['access_token']

def GetKnoxDeviceList(bearerToken):
    if bearerToken == "":
        print("No bearer token")
        return None

    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': f'Bearer {bearerToken}'
    }    
    
    data = {
        'deviceStatus': 'A',
        'start': 0
    }
    
    # Device list is paginated, limit of 1000 per page
    response = requests.post(KNOX_URL + "emm/oapi/device/selectDeviceList", headers=headers, data=data)
    devices = []
    while(True):            
        if response.json()['resultValue']['total'] < 1000:
            devices += response.json()['resultValue']['deviceList']
            return devices
        else:
            devices += response.json()['resultValue']['deviceList']
            data['start'] = len(devices)
            response = requests.post(KNOX_URL + "emm/oapi/device/selectDeviceList", headers=headers, data=data)
    
def GetDeviceLocation(deviceId, bearerToken):
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization' : f'Bearer {bearerToken}'
    }
    
    data = {
        'deviceId': deviceId
    }
    
    response = requests.post(KNOX_URL + "emm/oapi/device/selectDeviceLocation", headers=headers, data=data)
    return response.json()

def plotDeviceLocation(device,deviceLocation, foliumMap):  
    if deviceLocation['resultCode'] != '0':
        return
    
    timestamp = int(deviceLocation['resultValue']['updated']['time']) / 1000
    
    # Only plot devices that have location data in the last 2 hours
    if (timestamp < (datetime.now() - timedelta(hours=HOURS_BEFORE_NOT_SHOWN)).timestamp()):
        return
    
    if CATEGORY_LIST == "" or CATEGORY_LIST is None:
        tag = ""
        tag_color = "blue"
    else:
        # TODO: Implement tag retrieval from Knox
        tag = random.choice(CATEGORY_LIST)
        tag_color = {
            CATEGORY_LIST[0]: "blue",
            CATEGORY_LIST[1]: "green",
            CATEGORY_LIST[2]: "red",
            CATEGORY_LIST[3]: "purple"
        }.get(tag, "gray")
    
    opacity = getOpacityDependingOnTime(timestamp)
    tooltip = f'{tag} - {device["userName"]}'
    popupText = folium.IFrame(f"User: {device['userName']}<br>Tablet#: {device['userId']}<br>Last call-in: {datetime.fromtimestamp(timestamp).strftime('%I:%M %p')}")
    popup = folium.Popup(popupText, min_width=300, max_width=300, max_height=60)
    folium.Marker(location=(deviceLocation['resultValue']['latitude'],
                            deviceLocation['resultValue']['longitude']), 
                            tags=[tag],
                            icon=folium.Icon(color=tag_color,icon='user'),
                            tooltip=tooltip,
                            opacity=opacity,
                            popup=popup).add_to(foliumMap)

def getOpacityDependingOnTime(lastConnectionDate):
    # The older the last connection date, the more transparent the marker
    timeDifference = datetime.now() - datetime.fromtimestamp(lastConnectionDate)
    max_time_difference = timedelta(hours=0, minutes=MINUTES_BEFORE_MAX_DIM)
    min_opacity = 0.5
    max_opacity = 1.0

    if timeDifference > max_time_difference:
        return min_opacity

    opacity_range = max_opacity - min_opacity
    time_fraction = timeDifference / max_time_difference
    return max_opacity - (time_fraction * opacity_range)
    
def createFoliumMap():
    map = folium.Map(location=(DEFAULT_LATITUDE, DEFAULT_LONGITUDE), zoom_start=DEFAULT_ZOOM)
    if DEFAULT_MARKER:        
        folium.Marker(location=(DEFAULT_MARKER_LATITUDE, DEFAULT_MARKER_LONGITUDE), popup=DEFAULT_MARKER_NAME).add_to(map)
    Geocoder().add_to(map)
    folium.plugins.Fullscreen().add_to(map)
    TagFilterButton(CATEGORY_LIST).add_to(map)
    
    # Define the legend's HTML using Branca 
    #TODO: Make into table
    legend_html = '''
    {% macro html(this, kwargs) %}
    <div style="">
        &nbsp; <b>Legend (Placeholder data used)</b> <br>
        <table class="legend">
            <tr class="legend-row">
                <td class="legend-key">RN</td>
                <td class="legend-value><i class="fa fa-circle" style="color:#3caadc"></i></td>
            </tr>
            <tr class="legend-row">
                <td class="legend-key">LPN</td>
                <td class="legend-value><i class="fa fa-circle" style="color:#73b02e"></i></td>
            </tr>
            <tr class="legend-row">
                <td class="legend-key">MSW</td>
                <td class="legend-value><i class="fa fa-circle" style="color:#d43f30"></i></td>
            </tr>
            <tr class="legend-row">
                <td class="legend-key">CNA</td>
                <td class="legend-value><i class="fa fa-circle" style="color:#d153b8"></i></td>
            </tr>
        </table>
    </div>
    {% endmacro %}
    '''
    legend = branca.element.MacroElement()
    legend._template = branca.element.Template(legend_html)
    
    map.get_root().add_child(legend)
    return map

def retrieveAndPlotDeviceLocation(device, bearerToken, foliumMap):
    try:        
        deviceLocation = GetDeviceLocation(device['deviceId'],bearerToken)
        plotDeviceLocation(device, deviceLocation, foliumMap)
    except:
        print(f"Failed to retrieve location for {device['userName']}")

def main():
    bearerToken = GetKnoxBearerToken()
    deviceList = GetKnoxDeviceList(bearerToken)

    onlineDevices = []
    for device in deviceList:        
        # Only include devices that have been connected in the last {HOURS_BEFORE_NOT_SHOWN} hours
        if (device["lastConnectionDate"]["time"] > (datetime.now() - timedelta(hours=HOURS_BEFORE_NOT_SHOWN)).timestamp()):
            onlineDevices.append(device)
            
    print(f"Total devices: {len(deviceList)}")
    print(f"Online devices: {len(onlineDevices)}")
    
    foliumMap = createFoliumMap()
    
    threads = []
    for onlineDevice in onlineDevices:       
        # Multithread
        # Knox rate limit 1800 per minute
        if (len(onlineDevices) >= 1799):
            #TODO: Implement rate limiting
            print("Rate limit exceeded")
            break
        thread = threading.Thread(target=retrieveAndPlotDeviceLocation, args=(onlineDevice, bearerToken, foliumMap))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    foliumMap.save("./templates/map.html")
    
if __name__ == "__main__":
    main()