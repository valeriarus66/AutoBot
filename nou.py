#!/usr/bin/env python3

import sys
import rospy
import cv2
from std_msgs.msg import String
from std_msgs.msg import Float64
from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

import lane_detection
import control_lane


from geometry_msgs.msg import Twist
#from remote_teleop.msg import RemoteTwist
from autobot.msg import RemoteTwist
import termios
import tty



import time

class image_converter():
  def __init__(self):
    #self.image_pub = rospy.Publisher("scan",Image, queue_size=1)
    
    self.bridge = CvBridge()
    self.image_sub = rospy.Subscriber("/camera/image/compressed",CompressedImage,self.callback, queue_size=1)

    #self.image_sub = rospy.Subscriber("/raspicam_node/image/compressed",CompressedImage,self.callback, queue_size=1)

  
  def callback(self,data):
    try:
      cv_image = self.bridge.compressed_imgmsg_to_cv2(data)
  
    except CvBridgeError as e:
      print(e)

    control_lane.ControlLaneMedian(cv_image)



def main(args):
  ic = image_converter()
  rospy.init_node('image_converter', anonymous=True)

  try:

    rospy.spin()
    
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)