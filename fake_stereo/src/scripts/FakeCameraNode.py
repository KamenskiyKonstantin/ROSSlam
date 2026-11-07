#!/usr/bin/env python3
import math, os

from PIL import Image
from std_msgs.msg import Bool as ROSBool, Header
from sensor_msgs.msg import Image as ROSImage, CameraInfo
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, PoseWithCovariance, Twist, TwistWithCovariance, Point, Quaternion, Vector3
from math import tan
import numpy as np
import cv2
from cv_bridge import CvBridge

import rospy

script_dir = os.path.dirname(os.path.abspath(__file__))

rgb = Image.open(os.path.join(script_dir, "left.png"))


class FakeCameraNode:
    def __init__(self):
            self._rgb_img_pub = rospy.Publisher('/rgb/image_rect_color', ROSImage, queue_size=10)
            self._rgb_ci_pub = rospy.Publisher('/rgb/camera_info', CameraInfo, queue_size=10)
            self._depth_img_pub = rospy.Publisher('/depth/image', ROSImage, queue_size=10)
            self._depth_ci_pub = rospy.Publisher('/depth/camera_info', CameraInfo, queue_size=10)
            self._odom_pub = rospy.Publisher('/odom', Odometry, queue_size=10)
            self.flag = False
            rospy.Subscriber('/processor/clear', ROSBool, self.generate_bogus_message)
    def generate_bogus_message(self, msg):
        if self.flag:
            pass
        time = rospy.Time.now()
        rospy.loginfo(f"Sent message at {time}")
        header_rgb = Header()
        header_rgb.stamp = time
        header_rgb.frame_id = 'rgb_stereo'

        header_depth = Header()
        header_depth.stamp =time
        header_depth.frame_id = 'depth_stereo'

        header_odom = Header()
        header_odom.stamp = time
        header_odom.frame_id = 'odom'



        ROSrgb = ROSImage()

        FOV = math.pi/2


        fx, fy = rgb.width/tan(FOV/2), rgb.height/tan(FOV/2)
        cx, cy = rgb.width/2, rgb.height/2

        ROSrgb.header = header_rgb
        ROSrgb.width = rgb.width
        ROSrgb.height = rgb.height
        ROSrgb.step = rgb.width * 3
        ROSrgb.encoding='rgb8'
        ROSrgb.is_bigendian=False
        ROSrgb.data = rgb.tobytes()

        self._rgb_img_pub.publish(ROSrgb)
        print('RGB image published')

        bridge = CvBridge()

        array = np.full((rgb.height, rgb.width), 1.0, dtype=np.float32)
        ROSDepth = bridge.cv2_to_imgmsg(array, encoding='32FC1')
        ROSDepth.header = header_depth

       # self._rgb_img_pub.publish(ROSrgb)

        self._depth_img_pub.publish(ROSDepth)

        # published all the images by now

        CIrgb = CameraInfo()
        CIrgb.height = rgb.height
        CIrgb.header = header_rgb
        CIrgb.width = rgb.width
        CIrgb.distortion_model = 'plumb_bob'
        CIrgb.D = [-1, 0, 0, 0, 0] #some bogus parameters for plumb_bob system
        CIrgb.K = [fx, 0, cx, 0, fy, cy, 0, 0, 1]
        CIrgb.R = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        CIrgb.P = [fx, 0, cx, 0, 0, fy, cy, 0, 0, 0, 1, 0]
        self._rgb_ci_pub.publish(CIrgb)

        CIDepth = CameraInfo()
        CIDepth.header = header_depth
        CIDepth.height = rgb.height
        CIDepth.width = rgb.width
        CIDepth.distortion_model = 'plumb_bob'
        CIDepth.D = [-1, 0, 0, 0, 0]  # some bogus parameters for plumb_bob system
        CIDepth.K = [fx, 0, cx, 0, fy, cy, 0, 0, 1]
        CIDepth.R = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        CIDepth.P = [fx, 0, cx, 0, 0, fy, cy, 0, 0, 0, 1, 0]
        self._depth_ci_pub.publish(CIDepth)

        # odom message
        odom = Odometry()
        odom.header = header_odom
        odom.child_frame_id='odom'

        pose = Pose()

        position = Point()
        position.x = 0
        position.y = 0
        position.z = 0

        orientation = Quaternion()
        orientation.w = 1
        orientation.x = 0
        orientation.y = 0
        orientation.z = 0


        pose.position = position
        pose.orientation = orientation

        cov_pose = PoseWithCovariance()
        cov_pose.pose = pose
        cov_pose.covariance = [0]*36


        odom.pose =cov_pose

        twist = Twist()
        twist_vec = Vector3()
        twist_vec.x = twist_vec.y = twist_vec.z = 0
        twist.linear = twist_vec
        twist.angular = twist_vec

        cov_twist = TwistWithCovariance()
        cov_twist.twist = twist
        cov_twist.covariance = [0]*36

        odom.twist = cov_twist

        self._odom_pub.publish(odom)
        self.flag = True
    def untrue_the_flag(self, msg):
        self.flag = False
if __name__ == '__main__':
    rospy.init_node('fake_camera')
    node = FakeCameraNode()
    rospy.sleep(1)
    node.generate_bogus_message(None)
    #rate = rospy.Rate(10)
    while not rospy.is_shutdown():
     #   node.generate_bogus_message()
      #  rate.sleep()
        pass
