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
ATA = 1
PROCENT = 1
DIRECTORY = '/Users/matt/.config/Suunto/Suunto DM5/1.5.4.510'
OUTPUT = f'_tmp/{date.today()}-suunto-dm5.csv'
NAMESPACE = {'tag': 'http://www.suunto.com/schemas/sml'}
result = []


def kelvin_to_celsius(kelvin):
    try:
        celsius = float(kelvin) - 273.15
        return round(celsius)
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
    duration = timedelta(seconds=int(time)).total_seconds()
    return round(duration/DAY, 4)

def as_gas(gas: dict) -> str | None:
    state = gas['state']
    oxygen = gas['oxygen']
    helium = gas['helium']
    if state == 'Primary':
        return f'{oxygen:02}/{helium:02}'
    if state == 'Secondary':
        return None
    if state == 'Off':
        return None

for file in Path(DIRECTORY).glob('*.sml'):
    root = xml.parse(file).getroot()
    device = find(root, './/tag:Device/tag:SerialNumber')
    dt = datetime.fromisoformat(find(root, './/tag:Header/tag:DateTime'))
    duration_dive = find(root, './/tag:Header/tag:Duration')
    depth_max = find(root, './/tag:Header/tag:Depth/tag:Max')
    depth_avg = find(root, './/tag:Header/tag:Depth/tag:Avg')
    computer_mode = find(root, './/tag:Header/tag:Diving/tag:DiveMode')
    computer_conservatism = find(root, './/tag:Header/tag:Diving/tag:Conservatism')
    computer_altitude = find(root, './/tag:Header/tag:Diving/tag:Altitude')
    duration_interval = find(root, './/tag:Header/tag:Diving/tag:SurfaceTime')
    computer_algorithm = find(root, './/tag:Header/tag:Diving/tag:Algorithm')
    calculated_olf = find(root, './/tag:Header/tag:Diving/tag:EndTissue/tag:OLF')
    calculated_cns = find(root, './/tag:Header/tag:Diving/tag:EndTissue/tag:CNS')
    calculated_otu = find(root, './/tag:Header/tag:Diving/tag:EndTissue/tag:OTU')
    calculated_rgbm_nitrogen = find(root, './/tag:Header/tag:Diving/tag:EndTissue/tag:RgbmNitrogen')
    calculated_rgbm_helium = find(root, './/tag:Header/tag:Diving/tag:EndTissue/tag:RgbmHelium')
    temperature_surface, *temperature_bottom = findall(root, './/tag:Temperature')
    temperature_surface = temperature_surface.text
    temperature_bottom = min(T) if (T := [float(t.text) for t in temperature_bottom]) else None

    gases = []
    for i, gas in enumerate(findall(root, './/tag:Header/tag:Diving/tag:Gases/')):
        state = find(gas, './/tag:State')
        oxygen = round(o2*100) if (o2 := find(gas, './/tag:Oxygen')) else 0
        helium = round(he*100) if (he := find(gas, './/tag:Helium')) else 0
        nitrogen = 100-oxygen-helium
        gases.append({'id':i,'state':state,'oxygen':oxygen,'nitrogen':nitrogen,'helium':helium})

    duration_dive = as_duration(duration_dive)
    duration_interval = as_duration(duration_interval)
    temperature_surface = int(t) if (t := kelvin_to_celsius(temperature_surface)) else '?'
    temperature_bottom = int(t) if (t := kelvin_to_celsius(temperature_bottom)) else '?'
    computer_type = 'Suunto HelO2 (2022)' if int(device) == 3602896 else 'Suunto HelO2 (2020)'
    computer_mode = computer_mode.lower()
    computer_algorithm = 'rgbm' if computer_algorithm == 'Suunto Technical RGBM' else computer_algorithm
    computer_altitude = int(computer_altitude)
    computer_conservatism = int(computer_conservatism)
    tank1_gas = as_gas(gases[0]) if len(gases) > 0 else None
    tank2_gas = as_gas(gases[1]) if len(gases) > 1 else None
    tank3_gas = as_gas(gases[2]) if len(gases) > 2 else None
    tank4_gas = as_gas(gases[3]) if len(gases) > 3 else None
    tank5_gas = as_gas(gases[4]) if len(gases) > 4 else None
    tank6_gas = as_gas(gases[5]) if len(gases) > 5 else None
    tank7_gas = as_gas(gases[6]) if len(gases) > 6 else None
    tank8_gas = as_gas(gases[7]) if len(gases) > 7 else None

    pressure = depth_max/10 + 1*ATA
    calculated_cns = round(calculated_cns, 2) if calculated_cns else None
    calculated_otu = round(calculated_otu, 2) if calculated_otu else None
    calculated_olf = round(calculated_olf, 2) if calculated_olf else None
    calculated_ppO2 = round(gases[0]['oxygen'] * (depth_max/pressure) / 100*PROCENT, ndigits=2)
    calculated_ppN2 = round(gases[0]['nitrogen'] * (depth_max/pressure) / 100*PROCENT, ndigits=2)
    calculated_ppHe = round(gases[0]['helium'] * (depth_max/pressure) / 100*PROCENT, ndigits=2)

    result.append({
        'dive number': '?',
        'dive date': f'{dt:%Y-%m-%d}',
        'dive time': f'{dt:%H:%M}',
        'dive location': '?',
        'dive category': '?',
        'dive activity': '?',
        'dive specialization': '?',
        'dive remarks': '?',
        'duration dive': f'{duration_dive:.4f}',
        'duration deco': '?',
        'duration interval': f'{duration_interval:.4f}',
        'depth max': f'{depth_max:.1f}',
        'depth average': f'{depth_avg:.1f}',
        'temperature surface': f'{temperature_surface:2}',
        'temperature bottom': f'{temperature_bottom:2}',
        'computer type': computer_type,
        'computer mode': computer_mode,
        'computer conservatism': computer_conservatism,
        'computer altitude': computer_altitude,
        'computer algorithm': computer_algorithm,
        'item weight': '?',
        'calculated OLF': f'{calculated_olf:.2f}' if calculated_olf else '-',
        'calculated CNS': f'{calculated_cns:.2f}' if calculated_cns else '-',
        'calculated OTU': f'{calculated_otu:.2f}' if calculated_otu else '-',
        'calculated ppO2': f'{calculated_ppO2:.2f}' if calculated_ppO2 else '-',
        'calculated ppN2': f'{calculated_ppN2:.2f}' if calculated_ppN2 else '-',
        'calculated ppHe': f'{calculated_ppHe:.2f}' if calculated_ppHe else '-',
        'tank1 config': '?',
        'tank1 gas': tank1_gas if tank1_gas else '-',
        'tank1 volume': '?' if tank1_gas else '-',
        'tank1 start': '?' if tank1_gas else '-',
        'tank1 end': '?' if tank1_gas else '-',
        'tank1 sac': '?' if tank1_gas else '-',
        'tank1 rmv': '?' if tank1_gas else '-',
        'tank2 gas': tank2_gas if tank2_gas else '-',
        'tank2 volume': '?' if tank2_gas else '-',
        'tank2 start': '?' if tank2_gas else '-',
        'tank2 end': '?' if tank2_gas else '-',
        'tank2 sac': '?' if tank2_gas else '-',
        'tank2 rmv': '?' if tank2_gas else '-',
        'tank3 gas': tank3_gas if tank3_gas else '-',
        'tank3 volume': '?' if tank3_gas else '-',
        'tank3 start': '?' if tank3_gas else '-',
        'tank3 end': '?' if tank3_gas else '-',
        'tank3 sac': '?' if tank3_gas else '-',
        'tank3 rmv': '?' if tank3_gas else '-',
        'tank4 gas': tank4_gas if tank4_gas else '-',
        'tank4 volume': '?' if tank4_gas else '-',
        'tank4 start': '?' if tank4_gas else '-',
        'tank4 end': '?' if tank4_gas else '-',
        'tank4 sac': '?' if tank4_gas else '-',
        'tank4 rmv': '?' if tank4_gas else '-',
        'tank5 gas': tank5_gas if tank5_gas else '-',
        'tank5 volume': '?' if tank5_gas else '-',
        'tank5 start': '?' if tank5_gas else '-',
        'tank5 end': '?' if tank5_gas else '-',
        'tank5 sac': '?' if tank5_gas else '-',
        'tank5 rmv': '?' if tank5_gas else '-',
        'tank6 gas': tank6_gas if tank6_gas else '-',
        'tank6 volume': '?' if tank6_gas else '-',
        'tank6 start': '?' if tank6_gas else '-',
        'tank6 end': '?' if tank6_gas else '-',
        'tank6 sac': '?' if tank6_gas else '-',
        'tank6 rmv': '?' if tank6_gas else '-',
        'tank7 gas': tank7_gas if tank7_gas else '-',
        'tank7 volume': '?' if tank7_gas else '-',
        'tank7 start': '?' if tank7_gas else '-',
        'tank7 end': '?' if tank7_gas else '-',
        'tank7 sac': '?' if tank7_gas else '-',
        'tank7 rmv': '?' if tank7_gas else '-',
        'tank8 gas': tank8_gas if tank8_gas else '-',
        'tank8 volume': '?' if tank8_gas else '-',
        'tank8 start': '?' if tank8_gas else '-',
        'tank8 end': '?' if tank8_gas else '-',
        'tank8 sac': '?' if tank8_gas else '-',
        'tank8 rmv': '?' if tank8_gas else '-',
    })

df = (pd
    .DataFrame(result)
    .sort_values(by=['dive date', 'dive time'], ascending=False)
    .reset_index(drop=True)
).to_csv(OUTPUT, index=False)

print(f'Saved to {OUTPUT}')
