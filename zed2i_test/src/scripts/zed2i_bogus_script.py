#!/usr/bin/env python3
from PIL import Image, ImageOps
from ultralytics import YOLO

from time import time_ns
print('ULTRALYTICS: LOADED')
import numpy as np

import rospy
from sensor_msgs.msg import Image as ROSImage
from std_msgs.msg import Bool as ROSBool
from ROStoPIL import convert_from_ROS
#import pyzed.sl as sl

COLOR_MAP = {
    0:  (255, 0, 0),      # Red

    1:  (0, 255, 0),      # Green

    2:  (0, 0, 255),      # Blue

    3:  (255, 255, 0),    # Yellow

    4:  (255, 0, 255),    # Magenta

    5:  (0, 255, 255),    # Cyan

    6:  (255, 128, 0),    # Orange

    7:  (128, 0, 255),    # Purple

    8:  (255, 0, 128),    # Hot Pink

    9:  (0, 128, 255),    # Sky Blue

    10: (128, 255, 0),    # Lime

    11: (0, 255, 128),    # Spring Green

    12: (128, 0, 0),      # Maroon

    13: (0, 128, 0),      # Dark Green

    14: (0, 0, 128),      # Navy

    15: (255, 128, 128),  # Light Coral

    16: (128, 255, 255),  # Light Cyan

    17: (255, 128, 255),  # Light Pink

    18: (128, 128, 128),  # Gray
}
class NodeConverter:
    def __init__(self):
        self._pub_rgb = rospy.Publisher('/rgb/image', ROSImage, queue_size=10)
      # self._depth_pub = rospy.Publisher('/', ROSImage, queue_size=10)
        self._clear_pub = rospy.Publisher('/processor/clear', ROSBool, queue_size=10)
        self.model = YOLO('yolo26n-sem.pt', 'semantic')
        self._img_sub= rospy.Subscriber('/rgb/image_rect_color', ROSImage, self.process_RGB)
        print('INITIALIZATION: COMPLETE')


    def process_RGB(self,msg):
        print("Processor: START")
        pil = convert_from_ROS(msg)
        #pil = Image.open('left.png')
        pil.show()
        t0 = time_ns()
        loc_m = self.model
        inference = loc_m(pil)
#        print(f'Inference took: {(time_ns()-t0)/1000000} ms')

        tensor = inference[0]
        print(tensor.semantic_mask.data)
        pil_mask = Image.fromarray( tensor.semantic_mask.data.cpu().numpy())
        pil_grayscale = ImageOps.grayscale(pil)
        result_image = Image.new('RGB', pil_grayscale.size, (0, 0, 0))
        pixels = result_image.load()
        mask_pixels = pil_mask.load()
        grayscale_pixels = pil_grayscale.load()


        for i in range(pil_grayscale.width):
            for j in range(pil_grayscale.height):
                color = COLOR_MAP[mask_pixels[i,j]]
                scale = grayscale_pixels[i, j]/255
                pixels[i, j] = (int(color[0]*scale), int(color[1]*scale), int(color[2]*scale))
        #result_image.show()
        ROSresult = ROSImage(header=msg.header, width=result_image.width, height=result_image.height, encoding='rgb8', step=1*3*result_image.width, is_bigendian=False, data=result_image.tobytes())

        self._pub_rgb.publish(ROSresult)
        self._clear_pub.publish(ROSBool(data=True))
        print("YOLO published")
rospy.init_node('test_node_transformer')
converter = NodeConverter()
while not rospy.is_shutdown():
    pass

