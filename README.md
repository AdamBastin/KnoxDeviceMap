# Knox Worker Map
This web application combines all of your Knox Manage devices onto a single map with their most recent location. It can be configured to filter different categories based on the tags inside of Knox Manage.

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
After the first time the application is ran, it will generate a new `.env` file.

Open the `.env` file that is inside the `src` directory.

Populate the mandatory KNOX fields and optionally, the default map view fields.

## Screenshots
Coming soon

## Libraries
- Folium
- Flask
- Requests
