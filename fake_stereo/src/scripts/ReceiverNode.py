#!/usr/bin/env python3
from dataclasses import field

import rospy
import struct
from sensor_msgs.msg import PointCloud2, PointField

class Parser:
    BYTES_RUN_LEN = {
        PointField.INT8:1,
        PointField.INT16:2,
        PointField.INT32:4,
        PointField.UINT8: 1,
        PointField.UINT16: 2,
        PointField.UINT32: 4,
        PointField.FLOAT32: 4,
        PointField.FLOAT64: 8
    }

    BYTES_RECOVERY_FUNCTION = {
        PointField.INT8: 'c',
        PointField.INT16: 'h',
        PointField.INT32: 'i',
        PointField.UINT8: 'C',
        PointField.UINT16: 'H',
        PointField.UINT32: 'I',
        PointField.FLOAT32: 'f',
        PointField.FLOAT64: 'd'
    }

    def __init__(self, fields, is_bigendian: bool):
        self._endianness = ">" if is_bigendian else "<"
        self._fields = fields
        for field in fields:
           print(field.name, field.count)
    def parse(self, points):
        res = []
        for point in points:
            res.append(self.parse_point(point))
        return res
    def parse_point(self, point: bytes):
        result = dict()

        def recover(data: bytes, cur_field):
#            print(data)
            return struct.unpack(self._endianness + self.BYTES_RECOVERY_FUNCTION[cur_field.datatype], data)
        for field in self._fields:
            if field.count != 1:
                rospy.logwarn(f"Field {field.name} has more than 1 count, this is not implemented")

            result[field.name] = recover(point[field.offset:field.offset+self.BYTES_RUN_LEN[field.datatype]], field)
        return result






class Receiver:
    def __init__(self):
       self._subscriber = rospy.Subscriber('cloud_map', PointCloud2, self.handle)
    def handle(self, msg: PointCloud2):
        parser = Parser(msg.fields, msg.is_bigendian)
        data = msg.data
        step = msg.point_step
        points = [data[i:i+step] for i in range(0, len(data), step)]
        rospy.loginfo(f"fMessage with time {msg.header.stamp} reported f{len(points)} points found")
        parsed_points = parser.parse(points)
#        rospy.loginfo(f"Parsed points: {parsed_points}")
        with open("out.txt", "w") as file:
            print(parsed_points, file = file)


if __name__ == '__main__':
    rospy.init_node('map_receiver')
    node = Receiver()
    while not rospy.is_shutdown():
        pass
