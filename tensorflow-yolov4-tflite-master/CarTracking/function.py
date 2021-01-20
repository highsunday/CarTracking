#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 19:51:39 2020

@author: highsunday
"""
import cv2
import math
import copy
import random
import colorsys
import numpy as np
import copy
import sys
sys.path.append("..")
from core.utils import read_class_names
from core.config import cfg

class DetectArea:    
    def __init__(self, start_x, start_y,end_x,end_y, width=120):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.width = width
        
        self.car_id = 0
        self.motorbike_id = 0
        self.truck_id = 0
        self.bus_id = 0
        
        self.car_list = []
        self.motorbike_list = []
        self.truck_list = []
        self.bus_list = []
        
        area=[0,0,0,0,0,0,0,0]
        if((end_y-start_y)==0):
            area[0]=int(start_x)
            area[1]=int(start_y-self.width)
            area[2]=int(start_x)
            area[3]=int(start_y+self.width)
            area[4]=int(end_x)
            area[5]=int(end_y+self.width)
            area[6]=int(end_x)
            area[7]=int(end_y-self.width)
        else:
            slope=(start_x-end_x)/(end_y-start_y)
            hypotenuse= math.sqrt(1*1+slope*slope)
            
            
            area[0]=int(start_x+self.width/hypotenuse)
            area[1]=int(start_y+slope*self.width/hypotenuse)
            area[2]=int(start_x-self.width/hypotenuse)
            area[3]=int(start_y-slope*self.width/hypotenuse)
            area[4]=int(end_x-self.width/hypotenuse)
            area[5]=int(end_y-slope*self.width/hypotenuse)
            area[6]=int(end_x+self.width/hypotenuse)
            area[7]=int(end_y+slope*self.width/hypotenuse)
        self.area = copy.deepcopy(area)
    
    def plotMainLine(self,frame,color=(0, 0, 255)):
        cv2.line(frame, (self.start_x, self.start_y), (self.end_x, self.end_y), color, 12)
        return frame
    
    def plotSideLine(self,frame,color=(0, 0, 255)):
        cv2.line(frame, (self.area[0], self.area[1]), (self.area[6], self.area[7]), color, 4)
        cv2.line(frame, (self.area[2], self.area[3]), (self.area[4], self.area[5]), color, 4)
        return frame
    
    def showCarCount(self,frame,color=(0, 0, 255),show_info_coord=(80,80)):
        x=show_info_coord[0]
        y=show_info_coord[1]
        cv2.putText(frame, "Cars:"+str(self.car_id-len(self.car_list)), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 3, color, 5, cv2.LINE_AA)
        cv2.putText(frame, "Motorbikes:"+str(self.motorbike_id-len(self.motorbike_list)), (x,y+100), cv2.FONT_HERSHEY_SIMPLEX, 3, color, 5, cv2.LINE_AA)
        cv2.putText(frame, "Trucks:"+str(self.truck_id-len(self.truck_list)), (x,y+200), cv2.FONT_HERSHEY_SIMPLEX, 3, color, 5, cv2.LINE_AA)
        cv2.putText(frame, "Buses:"+str(self.bus_id-len(self.bus_list)), (x,y+300), cv2.FONT_HERSHEY_SIMPLEX, 3, color, 5, cv2.LINE_AA)
        return frame
        
    def testArea(self,centers):
        return inArea_horizon((self.area[0], self.area[1]),(self.area[4], self.area[5]),centers)
        
        
    def findCenters(self,newcenters1,oldcenters,distance_threshold=100,disppear_threshold=10):
        res=[]
        overlap=[0]*len(newcenters1)
        newcenters=[]
        for i in range(len(newcenters1)):
            this_center=newcenters1[i][1]
            this_score=newcenters1[i][0][3]
            for j in range(i+1,len(newcenters1)):
                that_center=newcenters1[j][1]
                that_score=newcenters1[j][0][3]
                if(calDistance(this_center,that_center)<distance_threshold):
                    if(this_score>that_score):
                        overlap[j]=1
                    else:
                        overlap[i]=1
        for i in range(len(newcenters1)):
            if(overlap[i]==0):
                newcenters.append(newcenters1[i])
        
        for i in range(len(newcenters)):
            if(len(oldcenters)>0):
                MaxScoreObj=oldcenters[0]
                for j in range(len(oldcenters)): 
                    if(calDistance(newcenters[i][1],oldcenters[j][1])<distance_threshold):
                        #=>find the big score label

                        if(newcenters[i][0][0]==oldcenters[j][0][0]):
                            newcenters[i][0][1]=oldcenters[j][0][1]
                            res.append(newcenters[i])
                            break
            if(newcenters[i][0][1]==-1):
                res.append(newcenters[i])

        
        for i in range(len(oldcenters)):
            this_id=oldcenters[i][0][1]
            this_class=oldcenters[i][0][0]
            nonFind=True
            for j in range(len(res)):
                if(this_id==res[j][0][1] and this_class==res[j][0][0]):
                    nonFind=False
            if(nonFind):
                oldcenters[i][0][2]+=1
                if(oldcenters[i][0][2]<=disppear_threshold):
                    res.append(oldcenters[i])
        res2=[]
        for i in range(len(res)):
            if(res[i][0][1]==-1):
                if(res[i][0][0]=='car'):
                    if(len(self.car_list)>0):
                        res[i][0][1]=self.car_list[0] 
                        self.car_list.pop(0)
                    else:
                        self.car_id+=1
                        res[i][0][1]=self.car_id  
                elif(res[i][0][0]=='motorbike'):
                    if(len(self.motorbike_list)>0):
                        res[i][0][1]=self.motorbike_list[0] 
                        self.motorbike_list.pop(0)
                    else:
                        self.motorbike_id+=1
                        res[i][0][1]=self.motorbike_id  
                elif(res[i][0][0]=='truck'):
                    if(len(self.truck_list)>0):
                        res[i][0][1]=self.truck_list[0] 
                        self.truck_list.pop(0)
                    else:
                        self.truck_id+=1
                        res[i][0][1]=self.truck_id  
                elif(res[i][0][0]=='bus'):
                    if(len(self.bus_list)>0):
                        res[i][0][1]=self.bus_list[0] 
                        self.bus_list.pop(0)
                    else:
                        self.bus_id+=1
                        res[i][0][1]=self.bus_id  
                res2.append(res[i])
            else:
                res2.append(res[i])
        
        res3=[]
        for i in range(len(res2)):
            flag=True
            for j in range(len(res2)):
                if(i==j):
                    continue
                if(calDistance(res2[i][1],res2[j][1])<distance_threshold):
                    if(res2[i][0][3]<res2[j][0][3] and res2[i][0][0]!=res2[j][0][0]):
                        flag=False
                        if(res2[i][0][0]=='car'):
                            self.car_list.append(res2[i][0][1])
                        elif(res2[i][0][0]=='motorbike'):
                            self.motorbike_list.append(res2[i][0][1])
                        elif(res2[i][0][0]=='truck'):
                            self.truck_list.append(res2[i][0][1])
                        elif(res2[i][0][0]=='bus'):
                            self.bus_list.append(res2[i][0][1])
            if(flag):
                res3.append(res2[i])
        
        return res3
    
    def findCenters_backup(self,newcenters1,oldcenters,distance_threshold=100,disppear_threshold=10):
        res=[]
        overlap=[0]*len(newcenters1)
        newcenters=[]
        for i in range(len(newcenters1)):
            this_center=newcenters1[i][1]
            this_score=newcenters1[i][0][3]
            for j in range(i+1,len(newcenters1)):
                that_center=newcenters1[j][1]
                that_score=newcenters1[j][0][3]
                if(calDistance(this_center,that_center)<distance_threshold):
                    if(this_score>that_score):
                        overlap[j]=1
                    else:
                        overlap[i]=1
        for i in range(len(newcenters1)):
            if(overlap[i]==0):
                newcenters.append(newcenters1[i])
        
        for i in range(len(newcenters)):
            if(len(oldcenters)>0):
                MaxScoreObj=oldcenters[0]
                for j in range(len(oldcenters)): 
                    if(calDistance(newcenters[i][1],oldcenters[j][1])<distance_threshold):
                        #=>find the big score label

                        if(newcenters[i][0][0]==oldcenters[j][0][0]):
                            newcenters[i][0][1]=oldcenters[j][0][1]
                            res.append(newcenters[i])
                            break
            if(newcenters[i][0][1]==-1):
                res.append(newcenters[i])

        print("before res:",res)
        for i in range(len(oldcenters)):
            this_id=oldcenters[i][0][1]
            this_class=oldcenters[i][0][0]
            nonFind=True
            for j in range(len(res)):
                if(this_id==res[j][0][1] and this_class==res[j][0][0]):
                    nonFind=False
            if(nonFind):
                oldcenters[i][0][2]+=1
                if(oldcenters[i][0][2]<=disppear_threshold):
                    res.append(oldcenters[i])
        res2=[]
        for i in range(len(res)):
            if(res[i][0][1]==-1):
                for j in range(len(res)):
                    if(res[j][0][1]==-1):
                        continue
                    if(calDistance(res[i][1],res[j][1])<distance_threshold):
                         if(res[i][0][3]<res[j][0][3]):
                             res[j][1]=res[i][1]
                             break
                if(res[i][0][0]=='car'):
                    res[i][0][1]=self.car_id  
                    self.car_id+=1
                elif(res[i][0][0]=='motorbike'):
                    res[i][0][1]=self.motorbike_id  
                    self.motorbike_id+=1
                elif(res[i][0][0]=='truck'):
                    res[i][0][1]=self.truck_id  
                    self.truck_id+=1
                elif(res[i][0][0]=='bus'):
                    res[i][0][1]=self.bus_id  
                    self.bus_id+=1
                res2.append(res[i])
            else:
                res2.append(res[i])
                
        print(" after res:",res2)
        
        #res=newcenters
        return res2
        
                
def calDistance(point1,point2):
        x_=(point1[0]-point2[0])
        y_=(point1[1]-point2[1])
        return  math.sqrt(x_*x_+y_*y_)
    
def inArea_horizon(LT,RB,centers):
    res=[]
    for i in centers:
        if(i[1][0]>LT[0]and i[1][0]<RB[0]):
            if(i[1][1]>LT[1]and i[1][1]<RB[1]):
                #cv2.circle(image,(i[1][0],i[1][1]), 0, (255, 0, 0), 30)
                res.append(i)
    return res
        
def plotCenters(image,centers):
    for i in centers:
        cv2.circle(image,(i[1][0],i[1][1]), 0, (0, 255, 0), 30)
        color=None
        class_text=""
        if(i[0][0]=='car'):
            color=(255,255,0)
            class_text='car'
        elif(i[0][0]=='motorbike'):
            color=(0,0,0)
            class_text='motorbike'
        elif(i[0][0]=='truck'):
            color=(0,255,255)
            class_text='truck'
        elif(i[0][0]=='bus'):
            color=(255,0,255)
            class_text='bus'
        cv2.putText(image, class_text+"_"+str(i[0][1]), (i[1][0],i[1][1]), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2, cv2.LINE_AA)


def get_centers(image, bboxes, classes=read_class_names(cfg.YOLO.CLASSES), show_label=True):
    num_classes = len(classes)
    dir_class={'car':0,'motorbike':1,'truck':2,'bus':3}
    image_h, image_w, _ = image.shape

    out_boxes, out_scores, out_classes, num_boxes = bboxes
    res=[]
    for i in range(num_boxes[0]):
        if int(out_classes[0][i]) < 0 or int(out_classes[0][i]) > num_classes: continue
        coor = out_boxes[0][i]
        coor[0] = int(coor[0] * image_h)
        coor[2] = int(coor[2] * image_h)
        coor[1] = int(coor[1] * image_w)
        coor[3] = int(coor[3] * image_w)
        
        center=(int((coor[1]+coor[3])/2),int((coor[0]+coor[2])/2))
        
        score = out_scores[0][i]
        class_ind = int(out_classes[0][i])
        temp=[[classes[class_ind], -1,0,score],center]
        
        if(classes[class_ind] in dir_class):
            #cv2.circle(image,center, 0, (0, 0, 255), 30)
            res.append(temp)
            
    return res

        
            
    
    