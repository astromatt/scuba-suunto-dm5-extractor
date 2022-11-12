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
