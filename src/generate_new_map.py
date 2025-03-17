import urllib.parse
import branca
import folium
import folium.plugins
import requests
import json
import os
import dotenv
import threading
import random
import urllib

from time import strftime, localtime
from folium.plugins import Geocoder, TagFilterButton, Fullscreen
from datetime import datetime, timedelta

def load_environment_variables():
    global KNOX_URL, KNOX_CLIENT_ID, KNOX_API_KEY, KNOX_SERVER_CODE
    global DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_ZOOM
    global DEFAULT_MARKER, DEFAULT_MARKER_LATITUDE, DEFAULT_MARKER_LONGITUDE, DEFAULT_MARKER_NAME
    global HOURS_BEFORE_NOT_SHOWN, MINUTES_BEFORE_MAX_DIM, CATEGORY_LIST

    env_file_path = os.path.join(os.path.dirname(__file__), 'config/.env')
    if not os.path.exists(env_file_path):
        print(".env file not found")        
        print("Please download the .env file from the repository")
        print("Then restart the application")        
        exit()
    
    # Load the environment variables from .env file
    dotenv.load_dotenv(dotenv_path="./config/.env")

    #https://us02.manage.samsungknox.com/
    KNOX_SERVER_CODE = os.getenv("KNOX_SERVER_CODE")
    KNOX_CLIENT_ID = os.getenv("KNOX_CLIENT_ID")
    KNOX_API_KEY = urllib.parse.quote_plus(os.getenv("KNOX_API_KEY"))
    KNOX_URL = f"https://{KNOX_SERVER_CODE}.manage.samsungknox.com/"

    if KNOX_SERVER_CODE is None or KNOX_CLIENT_ID is None or KNOX_API_KEY is None:
        print("KNOX_URL, KNOX_CLIENT_ID, or KNOX_API_KEY environment variables not set")
        exit()

    DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LATITUDE") or 0)
    DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LONGITUDE") or 0)
    DEFAULT_ZOOM = int(os.getenv("DEFAULT_ZOOM") or 20)
    DEFAULT_MARKER = bool(os.getenv("DEFAULT_MARKER")) or False
    DEFAULT_MARKER_LATITUDE = float(os.getenv("DEFAULT_MARKER_LATITUDE") or 0)
    DEFAULT_MARKER_LONGITUDE = float(os.getenv("DEFAULT_MARKER_LONGITUDE") or 0)
    DEFAULT_MARKER_NAME = os.getenv("DEFAULT_MARKER_NAME") or ''

    HOURS_BEFORE_NOT_SHOWN = int(os.getenv("HOURS_BEFORE_NOT_SHOWN") or 5)
    MINUTES_BEFORE_MAX_DIM = int(os.getenv("MINUTES_BEFORE_MAX_DIM") or 60)

    try:
        CATEGORY_LIST = os.getenv("CATEGORY_LIST").split(',') or []
    except:
        print("CATEGORY_LIST environment variable not set")
        CATEGORY_LIST = []

def get_knox_bearer_token():        
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    print(KNOX_URL)
    print(KNOX_CLIENT_ID)
    print(KNOX_API_KEY)
    payload = f'client_id={KNOX_CLIENT_ID}&client_secret={str(KNOX_API_KEY)}&grant_type=client_credentials'
    response = requests.post(KNOX_URL + "/emm/oauth/token", headers=headers, data=payload)
    print(response)
    return response.json()['access_token']

def get_knox_device_list(bearerToken):
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
    
def get_device_location(deviceId, bearerToken):
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization' : f'Bearer {bearerToken}'
    }
    
    data = {
        'deviceId': deviceId
    }
    
    response = requests.post(KNOX_URL + "emm/oapi/device/selectDeviceLocation", headers=headers, data=data)
    return response.json()

def plot_device_location(device,deviceLocation, foliumMap):  
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
    
    opacity = calculate_marker_opacity(timestamp)
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
    global PLOTTED_DEVICES
    PLOTTED_DEVICES += 1

def calculate_marker_opacity(lastConnectionDate):
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
    
def create_folium_map():
    map = folium.Map(location=(DEFAULT_LATITUDE, DEFAULT_LONGITUDE), zoom_start=DEFAULT_ZOOM)
    if DEFAULT_MARKER:        
        folium.Marker(location=(DEFAULT_MARKER_LATITUDE, DEFAULT_MARKER_LONGITUDE), popup=DEFAULT_MARKER_NAME).add_to(map)
        
    #TODO: Different search method
    Geocoder().add_to(map)
    
    folium.plugins.Fullscreen().add_to(map)
    TagFilterButton(CATEGORY_LIST).add_to(map)
    
    # Could add legend for categories, if wanted    
    # map.get_root().add_child(legend)
    return map

def retrieve_and_plot_device_location(device, bearerToken, foliumMap):
    try:        
        deviceLocation = get_device_location(device['deviceId'],bearerToken)
        plot_device_location(device, deviceLocation, foliumMap)
    except:
        print(f"Failed to retrieve location for {device['userName']}")

def main():
    # Call the method to initialize the global variables
    load_environment_variables()
    
    global PLOTTED_DEVICES
    PLOTTED_DEVICES = 0
    
    bearerToken = get_knox_bearer_token()
    deviceList = get_knox_device_list(bearerToken)

    onlineDevices = []
    for device in deviceList:        
        # Only include devices that have been connected in the last {HOURS_BEFORE_NOT_SHOWN} hours
        if ((device["lastConnectionDate"]["time"] / 1000) > (datetime.now() - timedelta(hours=HOURS_BEFORE_NOT_SHOWN)).timestamp()):
            onlineDevices.append(device)
            
    print(f"Total devices: {len(deviceList)}")
    print(f"Online devices: {len(onlineDevices)}")
    
    foliumMap = create_folium_map()
    
    threads = []
    for onlineDevice in onlineDevices:       
        # Multithread
        # Knox rate limit 1800 per minute
        if (len(onlineDevices) >= 1799):
            #TODO: Implement rate limiting
            print("Rate limit exceeded")
            break
        thread = threading.Thread(target=retrieve_and_plot_device_location, args=(onlineDevice, bearerToken, foliumMap))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    print(f"Plotted devices: {PLOTTED_DEVICES}")
    foliumMap.save("./templates/map.html")
    
if __name__ == "__main__":
    main()