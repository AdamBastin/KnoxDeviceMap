import os

def Generate():
    env_content = """
    KNOX_URL=https://as.manage.samsungknox.com/
    KNOX_CLIENT_ID=user@tenant.org
    KNOX_API_KEY=

    DEFAULT_LATITUDE = 38.563522
    DEFAULT_LONGITUDE = -121.471363
    DEFAULT_ZOOM = 12

    DEFAULT_MARKER = True
    DEFAULT_MARKER_LATITUDE = 38.563522
    DEFAULT_MARKER_LONGITUDE = -121.471363
    DEFAULT_MARKER_NAME = "Sacramento"

    # Hours before the current time that the device is not shown on the map
    # Set to 0 to disable and show all devices
    HOURS_BEFORE_NOT_SHOWN = 2

    # Minutes before the current time that the marker reaches minimum opacity (0.5)
    MINUTES_BEFORE_MAX_DIM = 30

    CATEGORY_LIST = Category1,Category2,Category3,Category4
    """

    env_file_path = os.path.join(os.path.dirname(__file__), '/config/.env')

    with open(env_file_path, 'w') as env_file:
        env_file.write(env_content)