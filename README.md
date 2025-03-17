# Knox Device Map
This web application combines all of your Samsung Knox Manage devices onto a single map with their most recent location. It can be configured to filter different tags based on device tags inside of Knox Manage.

![image](https://github.com/user-attachments/assets/cf4b2422-e4af-4625-9861-99193baf495f)

# Features
- Gather Knox Manage device locations
- Fade pins by a configurable amount based on time since last location
- Categorize devices by Knox Manage tags
- Search for addresses

# Setup
## 1. Docker or Manual
### Manual
1. **Clone repository** `git clone https://github.com/AdamBastin/KnoxDeviceMap.git`
2. **Open** **KnoxDeviceMap**
3. **Install requirements** `pip install requirements.txt`
4. **Run web app** `py knox_worker_map.py`

### Docker 
(Dockerfile coming soon)
## 2. Setup Knox Manage API Key
1. After startup, click the settings wheel in the top right

![image](https://github.com/user-attachments/assets/2b6292ed-6e90-4167-ac7a-8b5055f1e858)

2. Populate the mandatory KNOX fields and optionally, the default map view fields.

![image](https://github.com/user-attachments/assets/9829f5c4-f826-4939-9696-a29fb9caf6fb)




## Libraries
- Folium
- Flask
- Requests
