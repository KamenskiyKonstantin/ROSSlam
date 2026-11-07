#!/usr/bin/env python3
import math


import rospy
from sensor_msgs.msg import CameraInfo,Image as ROSImage
from std_msgs.msg import Header
import cv2
from cv_bridge import CvBridge
import numpy as np
from PIL import Image

SRC_IMAGE = Image.open('./src/static_assets/left.png')
class MockCameraStream:
    def __init__(self):
        self._rgb_pub = rospy.Publisher('zed/rgb/image_rect_color', ROSImage, queue_size=10)
        self._ci_pub = rospy.Publisher('zed/rgb/camera_info', CameraInfo, queue_size=10)
        self._depth_pub = rospy.Publisher('zed/depth/depth_registered', ROSImage, queue_size=10)

        self.RGB_MESSAGE = ROSImage(height=SRC_IMAGE.height, width=SRC_IMAGE.width, step=SRC_IMAGE.width*3,
                                    is_bigendian=False, encoding='rgb8',
                                    data=SRC_IMAGE.tobytes())

        FOV = math.pi / 2

        fx, fy = SRC_IMAGE.width / math.tan(FOV / 2), SRC_IMAGE.height / math.tan(FOV / 2)
        cx, cy = SRC_IMAGE.width / 2, SRC_IMAGE.height / 2
        self.CI_MESSAGE = CameraInfo(
            height=SRC_IMAGE.height,
            width=SRC_IMAGE.width,
            distortion_model='plumb_bob',
            D=[-1, 0, 0, 0, 0],
            K=[fx, 0, cx, 0, fy, cy, 0, 0, 1],
            R=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            P=[fx, 0, cx, 0, 0, fy, cy, 0, 0, 0, 1, 0]
        )
        self.DEPTH_MESSAGE = CvBridge().cv2_to_imgmsg(np.full((SRC_IMAGE.height, SRC_IMAGE.width), 1.0, dtype=np.float32))

    def submit(self):
        header = Header(stamp=rospy.Time.now(), frame_id='camera')
        self.RGB_MESSAGE.header = header
        self.CI_MESSAGE.header = header
        self.DEPTH_MESSAGE.header = header

        self._rgb_pub.publish(self.RGB_MESSAGE)
        self._ci_pub.publish(self.CI_MESSAGE)
        self._depth_pub.publish(self.DEPTH_MESSAGE)

if __name__ == '__main__':
    rospy.init_node('fake_camera_node')
    rate = rospy.Rate(50)
    node = MockCameraStream()
    rospy.sleep(1)
    rospy.loginfo('Began publishing')
    while not rospy.is_shutdown():
        rate.sleep()
        node.submit()
