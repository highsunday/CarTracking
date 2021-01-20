#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 19:40:55 2020

@author: highsunday
"""

import cv2
#from PIL import Image
import CarTracking.function as function

video_path='data/traffic.mkv'
print("Video from: ", video_path )
vid = cv2.VideoCapture(video_path)

width = vid.get(3)
height = vid.get(4)
fps = vid.get(5)

detectArea1=function.DetectArea(240,1200,2240,1200)
detectArea2=function.DetectArea(2400,1400,3600,1400)

frame_id = 0
while True:
    return_value, frame = vid.read()
    print(height,width)
    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame=detectArea1.plotMainLine(frame)
    frame=detectArea2.plotMainLine(frame,color=(0, 255, 0))
    #cv2.line(frame, (detectArea2.start_x, detectArea2.start_y), (detectArea2.end_x, detectArea2.end_y), (0, 255, 0), 3)
    frame=detectArea1.plotSideLine(frame)
    frame=detectArea2.plotSideLine(frame, color=(0, 255, 0))
    frame=cv2.putText(frame, "test1", (80,80), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,255), 4, cv2.LINE_AA)
    frame=cv2.putText(frame, "test2", (3200,80), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,255), 4, cv2.LINE_AA)
    frame=cv2.resize(frame, (int(width/4),int( height/4)), interpolation=cv2.INTER_AREA)
    
    cv2.imshow('Result', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        cv2.destroyAllWindows()
        break
    frame_id += 1