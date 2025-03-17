import dotenv
import generate_new_map
import os
import datetime as datetime
import secrets

from flask import Flask, redirect, render_template, request, url_for, flash

LAST_MAP_GENERATION_TIME = None
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = secrets.token_urlsafe(16)

@app.route('/')
def main_page():
    last_refresh = LAST_MAP_GENERATION_TIME
    if LAST_MAP_GENERATION_TIME is None:
        try:
            last_refresh = os.path.getmtime('templates/map.html')
        except:
            last_refresh = 0
    
    if last_refresh == 0:
        last_refresh = "Never"
    else:
        last_refresh = datetime.datetime.fromtimestamp(last_refresh).strftime('%A, %B %d %I:%M %p')

    return render_template('template.html', last_refresh=last_refresh)

@app.route('/new_map',methods=['POST'])
def new_map():
    data = {
        "statuscode": 200,
        "message": "Map generation successful"
    } 
    
    global LAST_MAP_GENERATION_TIME
    if LAST_MAP_GENERATION_TIME is not None:
        if LAST_MAP_GENERATION_TIME > datetime.datetime.now().timestamp() - 60:
            data['message'] = "Map was generated less than a minute ago. Please wait before generating a new map."
            data['statuscode'] = 400
            return data
    
    LAST_MAP_GENERATION_TIME = datetime.datetime.now().timestamp()
    
    try:
        generate_new_map.main()
        return data
    except:
        data['statuscode'] = 400
        data['message'] = "Map generation failed"
        return data

@app.route('/config', methods=['GET', 'POST'])
def config_page():
    env_file_path = os.path.join(os.path.dirname(__file__), 'config/.env')

    if request.method == 'POST':
        # Update the .env file with the submitted values
        updated_env = {
            "KNOX_SERVER_CODE": request.form.get("KNOX_SERVER_CODE"),
            "KNOX_CLIENT_ID": request.form.get("KNOX_CLIENT_ID"),
            "KNOX_API_KEY": request.form.get("KNOX_API_KEY"),
            "DEFAULT_LATITUDE": request.form.get("DEFAULT_LATITUDE"),
            "DEFAULT_LONGITUDE": request.form.get("DEFAULT_LONGITUDE"),
            "DEFAULT_ZOOM": request.form.get("DEFAULT_ZOOM"),
            "DEFAULT_MARKER": request.form.get("DEFAULT_MARKER"),
            "DEFAULT_MARKER_LATITUDE": request.form.get("DEFAULT_MARKER_LATITUDE"),
            "DEFAULT_MARKER_LONGITUDE": request.form.get("DEFAULT_MARKER_LONGITUDE"),
            "DEFAULT_MARKER_NAME": request.form.get("DEFAULT_MARKER_NAME"),
            "HOURS_BEFORE_NOT_SHOWN": request.form.get("HOURS_BEFORE_NOT_SHOWN"),
            "MINUTES_BEFORE_MAX_DIM": request.form.get("MINUTES_BEFORE_MAX_DIM"),
            "CATEGORY_LIST": request.form.get("CATEGORY_LIST"),
        }

        try:            
            with open(env_file_path, 'w') as env_file:
                for key, value in updated_env.items():
                    env_file.write(f"{key}={value}\n")
            flash("Environment variables updated successfully")
        except:
            flash("Failed to update .env file")

        return redirect(url_for('config_page'))

    # Load current environment variables
    dotenv.load_dotenv(env_file_path, override=True)
    current_env = {
        "KNOX_SERVER_CODE": os.getenv("KNOX_SERVER_CODE", "us01"),
        "KNOX_CLIENT_ID": os.getenv("KNOX_CLIENT_ID", "client@tenant.org"),
        "KNOX_API_KEY": os.getenv("KNOX_API_KEY", ""),
        "DEFAULT_LATITUDE": os.getenv("DEFAULT_LATITUDE", ""),
        "DEFAULT_LONGITUDE": os.getenv("DEFAULT_LONGITUDE", ""),
        "DEFAULT_ZOOM": os.getenv("DEFAULT_ZOOM", ""),
        "DEFAULT_MARKER": os.getenv("DEFAULT_MARKER", ""),
        "DEFAULT_MARKER_LATITUDE": os.getenv("DEFAULT_MARKER_LATITUDE", ""),
        "DEFAULT_MARKER_LONGITUDE": os.getenv("DEFAULT_MARKER_LONGITUDE", ""),
        "DEFAULT_MARKER_NAME": os.getenv("DEFAULT_MARKER_NAME", ""),
        "HOURS_BEFORE_NOT_SHOWN": os.getenv("HOURS_BEFORE_NOT_SHOWN", ""),
        "MINUTES_BEFORE_MAX_DIM": os.getenv("MINUTES_BEFORE_MAX_DIM", ""),
        "CATEGORY_LIST": os.getenv("CATEGORY_LIST", ""),
    }

    return render_template('config.html', env=current_env)


if __name__ == '__main__':
    app.run()