import xml.etree.ElementTree as xml
from datetime import date, datetime, timedelta
from pathlib import Path
import pandas as pd


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# # DATABASE = '~/.config/Suunto/Suunto DM5/1.5.2.488/DM4.db'
# DATABASE = './_tmp/2021-10-27-DM5.sqlite3'
#
# SQL_SELECT = """
#     SELECT DiveId,
#            StartTime,
#            Duration,
#            MaxDepth,
#            StartTemperature,
#            BottomTemperature,
#            SurfaceTime,
#            AvgDepth
#     FROM Dive
# """
#
#
# with sqlite3.connect(DATABASE) as db:
#     df = pd.read_sql(SQL_SELECT, db)


SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
DIRECTORY = '/Users/matt/.config/Suunto/Suunto DM5/1.5.2.488'
OUTPUT = f'_tmp/{date.today()}-suunto-dm5.csv'
NAMESPACE = {'suunto': 'http://www.suunto.com/schemas/sml'}
result = []


def kelvin_to_celsius(kelvin):
    try:
        celsius = float(kelvin) - 273.15
        return round(celsius, 1)
    except TypeError:
        return None


for file in Path(DIRECTORY).glob('*.sml'):
    root = xml.parse(file).getroot()

    dt = root.find('.//suunto:Header/suunto:DateTime', NAMESPACE).text
    dt = datetime.fromisoformat(dt)
    duration = root.find('.//suunto:Header/suunto:Duration', NAMESPACE).text
    depth_max = root.find('.//suunto:Header/suunto:Depth/suunto:Max', NAMESPACE).text
    depth_avg = root.find('.//suunto:Header/suunto:Depth/suunto:Avg', NAMESPACE).text
    temperature_surface, *temperature_bottom = root.findall('.//suunto:Temperature', NAMESPACE)
    temperature_surface = temperature_surface.text
    temperature_bottom = min(T) if (T := [float(t.text) for t in temperature_bottom]) else None

    result.append({
        'Date': dt.date(),
        'Time': dt.time(),
        'Location': None,
        'Category': None,
        'Spec': None,
        'Duration [min]': timedelta(seconds=int(duration)).total_seconds() / DAY,
        'Max Depth [meters]': round(float(depth_max), 1),
        'Average Depth [meters]': round(float(depth_avg), 1),
        'Temperature Surface [C]': kelvin_to_celsius(temperature_surface),
        'Temperature Bottom [C]': kelvin_to_celsius(temperature_bottom),
    })

df = (pd.DataFrame(result)
        .sort_values(['Date', 'Time'], ascending=False)
        .reset_index(drop=True))

df.to_csv(OUTPUT, index=False)
