#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import math
from sys import getsizeof
import os

def region_of_interest(image, vertices):
    """
    Create the mask using the vertices and apply it to the input image
    """
    mask = np.zeros_like(image)
    if len(mask.shape) == 2:
        cv2.fillPoly(mask, vertices, 255)
    else :
        cv2.fillPoly(mask, vertices, (255, ) * mask.shape[2]) # incase, the input image has a channel dimension
    return cv2.bitwise_and(image, mask)

def draw_lines(img, lines, color=[255, 0, 0], thickness=30):
    # If there are no lines to draw, exit.
    if lines is None:
        return
    # Make a copy of the original image.
    img = np.copy(img) # Create a blank image that matches the original in size.
    line_img = np.zeros(
        (
            img.shape[0],
            img.shape[1],
            3
        ),
        dtype=np.uint8,
    )
    # Loop over all lines and draw them on the blank image.
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(line_img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
    # Merge the image with the lines onto the original.
    img = cv2.addWeighted(img, 0.5, line_img, 1.0, 0.0)
    #img = cv2.addWeighted(img, 1.0, line_img, 0.95, 0.0)
    # Return the modified image.
    return img

def deseneaza(img):
    
    #image = mpimg.imread('/home/valeria/catkin_ws/src/autobot/src/image2.jpg')
    image = img


    #def select_white_yellow(image):
    converted = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
    # white color mask
    lower_white = np.uint8([0, 200, 0])
    upper_white = np.uint8([255, 255, 255])
    white_mask = cv2.inRange(converted, lower_white, upper_white)
    # yellow color mask
    lower_yellow = np.uint8([10, 0, 100])
    upper_yellow = np.uint8([40, 255, 255])
    yellow_mask = cv2.inRange(converted, lower_yellow, upper_yellow)
    # combine the mask
    mask = cv2.bitwise_or(white_mask, yellow_mask)
    combined_mask = cv2.bitwise_and(image, image, mask = mask)

    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    cannyed_image = cv2.Canny(gray_image, 50, 150)

    lines = cv2.HoughLinesP(cannyed_image, rho = 1, theta = np.pi / 180, threshold = 20, minLineLength = 20, maxLineGap = 300)
    
    left_line_x = []
    left_line_y = []
    right_line_x = []
    right_line_y = []

    for line in lines:
        for x1, y1, x2, y2 in line:
            slope = (y2 - y1) / (x2 - x1) # <-- Calculating the slope.
            if math.fabs(slope) < 0.5: # <-- Only consider extreme slope
                continue
            if slope <= 0: # <-- If the slope is negative, left group.
                left_line_x.extend([x1, x2])
                left_line_y.extend([y1, y2])
            else: # <-- Otherwise, right group.
                right_line_x.extend([x1, x2])
                right_line_y.extend([y1, y2])
                
    min_y = image.shape[0] * (3 / 5) # <-- Just below the horizon
    max_y = image.shape[0] # <-- The bottom of the image

    
    #linia stanga
    #verific daca nu e left da e right si return linia right, daca nu e right da e left si return left, si elif return medianae
    # return cu 4 param ( aia 3 de pana acuma + o variabila gen id) 
    # cand apelez in control_lane, vad ce am primit la id, si in functie de asta imi fac controlul 
    if(not right_line_x or not right_line_y):
        if(len(left_line_x)!=0 and len(left_line_y)!=0):
            poly_left = np.poly1d(np.polyfit(
                left_line_y,
                left_line_x,
                deg=1
            ))
            left_x_start = int(poly_left(max_y))
            left_x_end = int(poly_left(min_y))

            line_image = draw_lines(
                image,
                [[
                    [left_x_start, max_y, left_x_end, min_y],
                    #[right_x_start, max_y, right_x_end, min_y],
                ]],
                thickness=20,
            )
            return left_x_start, left_x_end, line_image,1 #case 1
    elif(not left_line_x or not left_line_y):
        if(len(right_line_x)!=0 and len(right_line_y)!=0):
            poly_right = np.poly1d(np.polyfit(
                right_line_y,
                right_line_x,
                deg=1
            ))
            right_x_start = int(poly_right(max_y))
            right_x_end = int(poly_right(min_y))

            line_image = draw_lines(
                image,
                [[
                    #[left_x_start, max_y, left_x_end, min_y],
                    [right_x_start, max_y, right_x_end, min_y],
                ]],
                thickness=20,
            )
            return right_x_start,right_x_end,line_image,2 #case 2
    elif(len(left_line_x)!=0 and len(left_line_y)!=0 and len(right_line_x)!=0 and len(right_line_y)!=0):
        poly_left = np.poly1d(np.polyfit(
                left_line_y,
                left_line_x,
                deg=1
            ))

        poly_right = np.poly1d(np.polyfit(
                right_line_y,
                right_line_x,
                deg=1
            ))

        left_x_start = int(poly_left(max_y))
        left_x_end = int(poly_left(min_y))

        right_x_start = int(poly_right(max_y))
        right_x_end = int(poly_right(min_y))
        
        line_image = draw_lines(
            image,
            [[
                [left_x_start, max_y, left_x_end, min_y],
                [right_x_start, max_y, right_x_end, min_y],
            ]],
            thickness=20,
        )
        median_x_start = int((poly_left(max_y)+poly_right(max_y))/2)
        median_x_end = int((poly_left(min_y)+poly_right(min_y))/2)

        median_image = draw_lines(
            line_image,
            [[
                [median_x_start, max_y, median_x_end, min_y], 
            ]],
            thickness=30,
        )
        return median_x_start, median_x_end, median_image,3 #case 3

    '''
    plt.figure()
    plt.imshow(line_image)

    plt.figure()
    plt.imshow(median_image)
    '''
    print('==================================ACBVGFN====MMMMMMM')
    print(max_y)
    print(min_y)
