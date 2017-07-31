"""
This definitions.py file has all function definitions for the project 3 jupyter notebook.
"""
# import librareis
import numpy as np
import pandas as pd
import datetime
from datetime import datetime, timedelta

"""
This function, boolStart, finds start points and returns an array of boolean.

When two points have a gap that is more than 10mins(600 seconds). The model assumes two are different journey.
"""

def boolStart(data):
    fmt = '%Y-%m-%d %H:%M:%S'
    temp = []
    preStamp = datetime.strptime('2018-5-1 00:00:00', fmt) # only for finding first data
    preId = 0
    for stamp, mId in zip(data['event_timestamp'], data['machine_id']):
        timediff = abs((preStamp - stamp).total_seconds())
        if(preStamp == datetime.strptime('2018-5-1 00:00:00', fmt)): # for the first data
            temp.append(True)
            preStamp = stamp
            preId = mId
        elif(timediff > 600): # if there is a gap more than 10 mins, this is regarded as a start point
            temp.append(True)
            preStamp = stamp
            preId = mId
        elif(preId != mId): # if machine IDs are different, this is also regarded as a start point
            temp.append(True)
            preStamp = stamp
            preId = mId
        else :
            temp.append(False) 
            preStamp = stamp
            preId = mId
    return temp

"""
The function, makeJourneyDf, makes raw data into a dataframe by journey.
This function returns a dataframe.
"""

def makeJourneyDf(data):
    start_time = []
    end_time = []
    time_ave_gap = []
    machine_id = []
    is_Heavy = [] # boolean value
    speed_temp = [] # store all speed values temporary to calculate mean and standard deviation
    speed_ave = [] # mean of speed 
    speed_std = [] # std of speed
    start_lat_arr = [] 
    start_lon_arr = []
    end_lat_arr = []
    end_lon_arr = []
    counts = [] # shows how many GPS data a journey has
    count = 0
    max_speed_gap = []
    sum_speed = 0
    for time, mId, heavy, speed, lat, lon, boolStart, boolEnd in zip(data['event_timestamp'], data['machine_id'], data['vehicle_weight_type'], data['speed_gps_kph'], data['latitude'], data['longitude'], data['start_point'], data['end_point']):
        if(boolStart and not boolEnd):
            start_time.append(time)
            machine_id.append(mId)
            speed_temp = []
            time_temp = []
            count =1
            if(heavy == 'HEAVY'):
                is_Heavy.append(True)
            else :
                is_Heavy.append(False)
            start_lat_arr.append(lat)
            start_lon_arr.append(lon)
            speed_temp.append(speed)
            time_temp.append(time)
        elif(not boolStart) and (not boolEnd):
            count += 1
            speed_temp.append(speed)
            time_temp.append(time)
        elif(not boolStart) and (boolEnd):
            count += 1
            speed_temp.append(speed)
            time_temp.append(time)
            end_lat_arr.append(lat)
            end_lon_arr.append(lon)
            end_time.append(time)
            counts.append(count)
            speed_ave.append(np.mean(speed_temp))
            speed_std.append(np.std(speed_temp))
            max_speed_gap.append(np.diff(speed_temp).max())
            time_ave_gap.append(np.diff(time_temp).mean().total_seconds())
            count = 0
        elif(boolStart) and (boolEnd):
            start_time.append(time)
            end_time.append(time)
            machine_id.append(mId)
            sum_speed = speed
            count=1
            if(heavy == 'HEAVY'):
                is_Heavy.append(True)
            else :
                is_Heavy.append(False)
            start_lat_arr.append(lat)
            start_lon_arr.append(lon)
            end_lat_arr.append(lat)
            end_lon_arr.append(lon)
            speed_ave.append(speed)
            speed_std.append(0.0)
            max_speed_gap.append(0.0)
            time_ave_gap.append(0.0)
            counts.append(count)
    
    duration_arr = []
    for i in range(len(start_time)):
        diff = (start_time[i]-end_time[i]).total_seconds()
        duration_arr.append(abs(diff))

    # check a journey was northward or southward
    is_northing = []
    for i in range(len(start_lat_arr)):
        if(start_lat_arr[i]-end_lat_arr[i])>0:
            is_northing.append(False)
        else:
            is_northing.append(True)
    # make a dataframe
    dfjourney = pd.DataFrame()
    dfjourney['is_northing'] = is_northing
    dfjourney['start_time'] = start_time
    dfjourney['end_time'] = end_time 
    dfjourney['duration_second'] = duration_arr
    dfjourney['machine_id'] = machine_id
    dfjourney['is_heavy'] = is_Heavy
    dfjourney['average_GPS_speed'] = speed_ave
    dfjourney['GPS_speed_std'] = speed_std
    dfjourney['Max_speed_gap'] = max_speed_gap
    dfjourney['average_time_gap'] = time_ave_gap
    dfjourney['start_latitude'] = start_lat_arr
    dfjourney['start_longitude'] = start_lon_arr
    dfjourney['end_latitude'] = end_lat_arr
    dfjourney['end_longitude'] = end_lon_arr
    dfjourney['number_data'] = counts
    return dfjourney
    
"""
The function, findClosestData, finds the weather conditions at the nearest data from start time
Returns an array of string
String values are only 'Rain', 'Drizzle', 'Clouds', 'Clear'
"""
def findClosestData(start, w):
    temp_weather = []
    for time in start:
        prediff = 999999.0
        str = ''
        for w_time, weather in zip(start, w):
            timediff = abs((time-w_time).total_seconds())
            if timediff < prediff :
                str = weather
                prediff = timediff
        temp_weather.append(str)
    return temp_weather

"""
The function, weatherDummy, converts string values into dummy values. 
Rain: 4, Drizzle: 3, Clouds: 2, Clear: 1
Returns an array of integer
"""
def weatherDummy(data):
    temp_weather = []
    for str in data:
        if str=='Rain':
            temp_weather.append(4)
        elif str=='Drizzle':
            temp_weather.append(3)
        elif str=='Clouds':
            temp_weather.append(2)
        elif str=='Clear':
            temp_weather.append(1)
    return temp_weather

"""
The function, converNZDT, converts UTC time into New Zealand date time adding 13 hours.
Returns an array of datetime.
"""

def convertNZDT(data):
    temp_time = []
    for t in data:
        t = t.replace(' +0000 UTC', '')
        t = datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
        t = t + timedelta(hours=13)
        temp_time.append(t)
    return temp_time

"""
The function, diffRate, calculates differences between estimate time in traffic condition and actual time, 
and divides by actual time.
Therefore, diffRate positive means the vehicle arrived earlier than expected by Google Maps.
The function returns an array of float.
"""

def diffRate(time, timeTraffic):
    temp_diff_rate=[]
    for act, est in zip(time, timeTraffic):
        diff = est - act
        temp_diff_rate.append(float((diff)/act))
    return temp_diff_rate

"""
The function, calculateAveSpeed, calculates average speed using distance from Google Maps and actual duration time.
Returns an array of float
"""

def calculateAveSpeed(time, dist):
    speed_array = []
    for time, distance in zip(time, dist):
        speed_array.append(float (distance/time*3600/1000))
    return speed_array

"""
The function, boolJamTime, checks whether a journey started at congested time or not.
Here are congested times.
Northwards: only from 6 to 10 AM.
Southwards: both, from 6 to 10 AM and from 13:30 to 18:30.
Returns an array of boolean.
"""

def boolJamTime(start_time, northward):
    start1 = datetime.strptime("06:00:00","%H:%M:%S").time()
    end1 = datetime.strptime("10:00:00","%H:%M:%S").time()
    start2 = datetime.strptime("13:30:00","%H:%M:%S").time()
    end2 = datetime.strptime("18:30:00","%H:%M:%S").time()
    temp = []
    for start, north in zip(start_time, northward):
        if north:
            if (start.time()>start2) and (start.time()<end2):
                temp.append(True)
            else :
                temp.append(False)
        elif not north:
            if (start.time()>start1) and (start.time()<end1):
                temp.append(True)
            elif (start.time()>start2) and (start.time()<end2):
                temp.append(True)
            else :
                temp.append(False)
    return temp

"""
The function, dayOfWeek, calculates the day of the week. 
0 indicates Monday, 6 indicates Sunday.
Returns an array of integer
"""

def dayOfWeek(start):
    temp = []
    for date in start:
        temp.append(date.weekday())
    return temp
