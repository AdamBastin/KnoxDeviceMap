# Knox Device Map
This web application combines all of your Samsung Knox Manage devices onto a single map with their most recent location. It can be configured to filter different tags based on device tags inside of Knox Manage.

# Setup
## 1. Docker or Manual
### Manual
1. Download source code
2. Install requirements
`pip install requirements.txt`
3. Run web app
`py knox_worker_map.py`
### Docker 
(Dockerfile coming soon)
## 2. Setup .env file
After startup, click the settings wheel in the top right

Populate the mandatory KNOX fields and optionally, the default map view fields.

## Screenshots
![image](https://github.com/user-attachments/assets/cf4b2422-e4af-4625-9861-99193baf495f)


## Libraries
- Folium
- Flask
- Requests
