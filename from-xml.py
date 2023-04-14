#!/usr/bin/env python3.11

# Owner: Matt Harasymczuk, +48 781 111 743, matt@astronaut.center
# Emergency: Agata Kolodziejczyk, +48 887 885 188, fichbio@gmail.com

import xml.etree.ElementTree as xml
from datetime import date, datetime, timedelta
from pathlib import Path
import pandas as pd


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
DIRECTORY = '/Users/matt/.config/Suunto/Suunto DM5/1.5.4.510'
OUTPUT = f'_tmp/{date.today()}-suunto-dm5.csv'
NAMESPACE = {'tag': 'http://www.suunto.com/schemas/sml'}
result = []


def kelvin_to_celsius(kelvin):
    try:
        celsius = float(kelvin) - 273.15
        return round(celsius, 1)
    except TypeError:
        return None

def find(root, xpath):
    try:
        value = root.find(xpath, NAMESPACE).text
        return round(float(value), 2)
    except AttributeError:
        return None
    except ValueError:
        return value

def findall(root, xpath):
    return root.findall(xpath, NAMESPACE)

def as_duration(time):
    return timedelta(seconds=int(time)).total_seconds() / DAY


for file in Path(DIRECTORY).glob('*.sml'):
    root = xml.parse(file).getroot()
    device = find(root, './/tag:Device/tag:SerialNumber')
    dt = datetime.fromisoformat(find(root, './/tag:Header/tag:DateTime'))
    duration = find(root, './/tag:Header/tag:Duration')
    depth_max = find(root, './/tag:Header/tag:Depth/tag:Max')
    depth_avg = find(root, './/tag:Header/tag:Depth/tag:Avg')
    dive_mode = find(root, './/tag:Header/tag:Diving/tag:DiveMode')
    conservatism = find(root, './/tag:Header/tag:Diving/tag:Conservatism')
    altitude = find(root, './/tag:Header/tag:Diving/tag:Altitude')
    surface_time = find(root, './/tag:Header/tag:Diving/tag:SurfaceTime')
    algorithm = find(root, './/tag:Header/tag:Diving/tag:Algorithm')
    olf = find(root, './/tag:Header/tag:Diving/tag:EndTissue/tag:OLF')
    cns = find(root, './/tag:Header/tag:Diving/tag:EndTissue/tag:CNS')
    otu = find(root, './/tag:Header/tag:Diving/tag:EndTissue/tag:OTU')
    rgbm_nitrogen = find(root, './/tag:Header/tag:Diving/tag:EndTissue/tag:RgbmNitrogen')
    rgbm_helium = find(root, './/tag:Header/tag:Diving/tag:EndTissue/tag:RgbmHelium')
    temperature_surface, *temperature_bottom = findall(root, './/tag:Temperature')
    temperature_surface = temperature_surface.text
    temperature_bottom = min(T) if (T := [float(t.text) for t in temperature_bottom]) else None

    gases = []
    for i, gas in enumerate(findall(root, './/tag:Header/tag:Diving/tag:Gases/')):
        gases.append({
            'id': i,
            'state': find(gas, './/tag:State'),
            'oxygen': round(o2*100) if (o2 := find(gas, './/tag:Oxygen')) else 0,
            'helium': round(he*100) if (he := find(gas, './/tag:Helium')) else 0})

    result.append({
        'Computer': int(device),
        'Date': dt.date(),
        'Time': dt.time(),
        'Location': None,
        'Category': None,
        'Activity': None,
        'Spec': None,
        'Duration [day]': as_duration(duration),
        'Max Depth [meters]': round(float(depth_max), 1),
        'Average Depth [meters]': round(float(depth_avg), 1),
        'Temperature Surface [C]': kelvin_to_celsius(temperature_surface),
        'Temperature Bottom [C]': kelvin_to_celsius(temperature_bottom),
        'Weight [kg]': None,
        'Gas_0': f'{gases[0]["state"]}; O2={gases[0]["oxygen"]}; He={gases[0]["helium"]}' if len(gases) > 0 else None,
        'Gas_1': f'{gases[1]["state"]}; O2={gases[1]["oxygen"]}; He={gases[1]["helium"]}' if len(gases) > 1 else None,
        'Gas_2': f'{gases[2]["state"]}; O2={gases[2]["oxygen"]}; He={gases[2]["helium"]}' if len(gases) > 2 else None,
        'Gas_3': f'{gases[3]["state"]}; O2={gases[3]["oxygen"]}; He={gases[3]["helium"]}' if len(gases) > 3 else None,
        'Gas_4': f'{gases[4]["state"]}; O2={gases[4]["oxygen"]}; He={gases[4]["helium"]}' if len(gases) > 4 else None,
        'Gas_5': f'{gases[5]["state"]}; O2={gases[5]["oxygen"]}; He={gases[5]["helium"]}' if len(gases) > 5 else None,
        'Gas_6': f'{gases[6]["state"]}; O2={gases[6]["oxygen"]}; He={gases[6]["helium"]}' if len(gases) > 6 else None,
        'Gas_7': f'{gases[7]["state"]}; O2={gases[7]["oxygen"]}; He={gases[7]["helium"]}' if len(gases) > 7 else None,
        'Dive Mode': dive_mode,
        'Conservatism': int(conservatism),
        'Altitude': int(altitude),
        'Surface Time': as_duration(surface_time),
        'Algorithm': algorithm,
        'OLF': olf,
        'CNS': cns,
        'OTU': otu,
        'RGBM Nitrogen': rgbm_nitrogen,
        'RGBM Helium': rgbm_helium,
    })

df = (pd.DataFrame(result)
        .sort_values(['Date', 'Time'], ascending=False)
        .reset_index(drop=True))

df.to_csv(OUTPUT, index=False)
print(f'Saved to {OUTPUT}')
