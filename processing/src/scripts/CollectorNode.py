#!/usr/bin/env python3
from std_msgs.msg import Header
from nav_msgs.msg import Odometry
from sensor_msgs.msg import CameraInfo, Image
import rospy

class CollectorNode:
    def __init__(self):
        # egress publishers

        self._odom_pub = rospy.Publisher('/odom', Odometry, queue_size=10)
        self._rgb_pub = rospy.Publisher('/rgb/image', Image, queue_size=10)
        self._ci_pub = rospy.Publisher('/rgb/camera_info', CameraInfo, queue_size=10)
        self._depth_pub = rospy.Publisher('/depth/image', Image, queue_size=10)

        self._yolo_pub = rospy.Publisher('/yolo/in', Image, queue_size=10)

        # ingress
        rospy.Subscriber('/integration/odom_out', Odometry, self.handle_odom)
        rospy.Subscriber('/zed/rgb/image_rect_color', Image, self.handle_image)
        rospy.Subscriber('/zed/rgb/camera_info', CameraInfo, self.handle_ci)
        rospy.Subscriber('/zed/depth/depth_registered', Image, self.handle_depth)
        rospy.Subscriber('/yolo/out', Image, self.handle_yolo)

        # storage
        self.ci = None
        self.depth = None
        self.odom = None
        self.yolo_result = None
        self.yolo_busy = False

    def submit(self):
        if self.yolo_result is None:
            rospy.loginfo('YOLO result missing, rejecting publish')
            return
        if self.depth is None:
            rospy.loginfo('Depth map missing, rejecting publish')
            return
        if self.ci is None:
            rospy.loginfo('Camera info missing, rejecting publish')
            return
        if self.odom is None:
            rospy.loginfo('Odometry missing, rejecting publish')
            return
        rospy.loginfo('Package assembled. Submitting')
        # do we need a force synchronizer?
        self._ci_pub.publish(self.ci)
        self._odom_pub.publish(self.odom)
        self._rgb_pub.publish(self.yolo_result)
        self._depth_pub.publish(self.depth)
        rospy.loginfo('Package sent. Clearing data')

        self.ci = None
        self.depth = None
        self.odom = None
        self.yolo_result = None
#        self.yolo_busy = False #??
    def handle_odom(self, msg):
        if self.odom is None:
            self.odom = msg
#        else:
#            rospy.loginfo('Received Odometry when already had one, dropping message')
    def handle_depth(self, msg):
        if self.depth is None:
            self.depth = msg
 #       else:
 #           rospy.loginfo('Received Depth map message when already had one, dropping message')
    def handle_ci(self, msg):
        if self.ci is None:
            self.ci = msg
  #      else:
  #          rospy.loginfo('Received Camera Info when already had one, dropping message')
    def handle_yolo(self, msg):
        if self.yolo_result is None:
            self.yolo_result = msg
            self.yolo_busy = False
   #     else:
   #         rospy.loginfo('Received YOLO result when already had one, dropping message')
    def handle_image(self, msg):
        if not self.yolo_busy:
            rospy.loginfo("Handing of to YOLO")
            self._yolo_pub.publish(msg)
            self.yolo_busy = True
    #    else:
    #        rospy.loginfo('Received camera image, YOLO is busy, dropping message')

if __name__ == '__main__':
    rospy.init_node('Collector')
    node = CollectorNode()
    rate = rospy.Rate(10)
    rospy.sleep(1)
    while not rospy.is_shutdown():
        rate.sleep()
        node.submit()




