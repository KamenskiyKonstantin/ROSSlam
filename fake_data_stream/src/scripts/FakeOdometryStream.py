#!/usr/bin/env python3
import rospy
from std_msgs.msg import Header
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, Twist, PoseWithCovariance, TwistWithCovariance, Vector3, Quaternion, Point

class MockOdometryNode:
    def __init__(self):
        self._odom_publisher = rospy.Publisher('/integration/odom_out', Odometry, queue_size=10)
        cov_matrix = [0.0]*36
        self.ODOM_MESSAGE = Odometry(child_frame_id='base_link',
                                     pose=PoseWithCovariance(
                                         pose=Pose(
                                             position=Point(0, 0, 0),
                                             orientation=Quaternion(0, 0, 0, 1)),
                                         covariance=cov_matrix.copy()),
                                     twist=TwistWithCovariance(
                                         twist=Twist(Vector3(0, 0, 0), Vector3(0, 0, 0)),
                                         covariance=cov_matrix.copy()
                                     ))

    def submit(self):
        header = Header(stamp=rospy.Time.now(), frame_id='base_link')
        self.ODOM_MESSAGE.header = header
        self._odom_publisher.publish(self.ODOM_MESSAGE)


if __name__ == '__main__':
    rospy.init_node('fake_odometry_stream')
    rate = rospy.Rate(100)
    node = MockOdometryNode()
    rospy.sleep(1)
    rospy.loginfo('Began publishing')
    while not rospy.is_shutdown():
        rate.sleep()
        node.submit()
