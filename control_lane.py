#!/usr/bin/env python3
import rospy
import numpy as np
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
from autobot.msg import RemoteTwist
import lane_detection
import cv2
from time import sleep

LINEAR_INCREMENT = 0.04
ANGULAR_INCREMENT = 0.2

    
def ControlLaneMedian(img):

    center_cooridnates = (int(img.shape[1]*0.5) , int(img.shape[0]*0.9))
    img_merge = cv2.circle(img,center_cooridnates,10,(0,0,255),5)

    x = int(img.shape[1]*0.5) #punct
    

    xline_left,xline_right,img_median,line_case = lane_detection.deseneaza(img_merge)
    #pub = rospy.Publisher('remote_cmd_vel', Twist, queue_size=10)
    pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
    
    linear_vel = 0
    angular_vel = 0

    twist = Twist()
  
    twist.linear.y = 0
    twist.linear.x = 0
    twist.angular.x = 0
    twist.angular.y = 0
    twist.angular.z = 0

    xpointLeft = xline_left - 10
    xpointRight = xline_right +10

    if(line_case == 1): #exista linia stanga da nu exista dreapta
        if(x > xline_right):
            if(x < xpointRight):
                time=4
                while time:
                    linear_vel = linear_vel + LINEAR_INCREMENT 
                    time-=1
                angular_vel = angular_vel - ANGULAR_INCREMENT-0.2
            else:
                time=6
                while time:
                    linear_vel = linear_vel + LINEAR_INCREMENT 
                    time-=1
                angular_vel = angular_vel - ANGULAR_INCREMENT-0.2 #era +

            twist.linear.x = linear_vel
            twist.angular.z = angular_vel
            print('case 1, o ia spre dreapta')
    elif (line_case == 2): #exista linia dreapta da nu exista linia stanga
        if(x < xline_left): #imi fac o marja
            if(x > xpointLeft):
                time=4
                linear_vel = linear_vel + LINEAR_INCREMENT
                while time:
                    #linear_vel = linear_vel + LINEAR_INCREMENT
                    time-=1
                angular_vel = angular_vel + ANGULAR_INCREMENT+0.25
                #sleep(0.5)
                print('case 2, o ia spre stanga in if')
            else:
                time=6
                while time:
                    linear_vel = linear_vel + LINEAR_INCREMENT
                    time-=1
                angular_vel = angular_vel + ANGULAR_INCREMENT+0.2
                #linear_vel = linear_vel + LINEAR_INCREMENT
                print('case 2, o ia spre stanga in elif')
                
            twist.linear.x = linear_vel
            twist.angular.z = angular_vel
          
    elif(line_case == 3): #daca exista mediana
        #for i in range(0,img.shape[1]): #img.shape[1] este max_x pe imagine, maxim dreapta
        if(x <= xline_right+5 and x >= xline_left-5):
            linear_vel = linear_vel + LINEAR_INCREMENT

            twist.linear.x = linear_vel
            twist.angular.z = angular_vel
            #pub.publish(twist)
            print('pe mediana')
        elif(x > xline_right ):
            angular_vel = angular_vel + ANGULAR_INCREMENT
            linear_vel = linear_vel + LINEAR_INCREMENT
            twist.linear.x = linear_vel
            twist.angular.z = angular_vel
            #pub.publish(twist)
            print('in dreapta medianei si xr = ', xline_right)
        elif(x < xline_left):
            angular_vel = angular_vel - ANGULAR_INCREMENT
            linear_vel = linear_vel + LINEAR_INCREMENT
            twist.linear.x = linear_vel
            twist.angular.z = angular_vel
            
            print('in stanga medianei si xl = ', xline_left)

    pub.publish(twist)
    '''
    twist.linear.x = linear_vel
    twist.angular.x = angular_vel
   
    pub.publish(twist)
    '''

    cv2.imshow("Image window", img_median)
    cv2.waitKey(3)

