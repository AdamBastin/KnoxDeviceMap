FROM python:3.12.9-slim

WORKDIR /usr/

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/AdamBastin/KnoxDeviceMap.git

WORKDIR /usr/KnoxDeviceMap

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

WORKDIR /usr/KnoxDeviceMap/src

# Run knox_device_map.py when the container launches
ENV FLASK_APP=knox_device_map.py
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]