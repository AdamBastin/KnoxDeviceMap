import generate_new_map
import os
import datetime as datetime
import time 

from flask import Flask, render_template

LAST_MAP_GENERATION_TIME = None
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

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

if __name__ == '__main__':
    app.run()