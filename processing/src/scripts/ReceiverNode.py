#!/usr/bin/env python3
from dataclasses import field
from YOLOProcessor import COLOR_MAP

import rospy
import struct
from sensor_msgs.msg import PointCloud2, PointField
import sensor_msgs.point_cloud2 as pc2

class Receiver:
    def __init__(self):
       self._subscriber = rospy.Subscriber('cloud_map', PointCloud2, self.handle)
    def handle(self, msg: PointCloud2):
        parsed_points = pc2.read_points(msg, ('x', 'y', 'z', 'rgb'), skip_nans=True)
        for point in parsed_points:
            rgb_f = point[-1]
            rgb_int = struct.unpack('I', struct.pack('f', rgb_f))[0]
            r = (rgb_int >> 16) & 0xFF
            g= (rgb_int >> 8) & 0xFF
            b=rgb_int & 0xFF
            color = (r, g, b)
            print(point, 'resolved to class', self.resolve(color))

        with open("out.txt", "w") as file:
            print(parsed_points, file = file)
    def resolve(self, color):
        return COLOR_MAP.find_class_by_color(color)



