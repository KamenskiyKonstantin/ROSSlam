#!/usr/bin/env python3
import rospy

from PIL import Image, ImageOps
from sensor_msgs.msg import Image as ROSImage
from time import time_ns
from ultralytics import YOLO
rospy.loginfo("YOLO imported")

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
class YOLOProcessor:
    def __init__(self, model_path):
        self.model = YOLO(model_path, 'semantic')
        rospy.loginfo("YOLO Model initialized")

        self._result_pub = rospy.Publisher('/yolo/out', ROSImage, queue_size=10)
        self._in_subscriber = rospy.Subscriber('/yolo/in', ROSImage, self.process)

    def process(self, msg):
        image = self.convert_to_pil(msg)
        rospy.loginfo('YOLO inference started')
        t0 = time_ns()
        semantic_tensor = self.model(image)[0]
        rospy.loginfo(f'YOLO inference complete, took {time_ns()-t0}')
        result = Image.new('RGB', image.size, (0, 0, 0))
        result_pixels = result.load()
        grayscale_pixels = ImageOps.grayscale(image).load()
        mask_pixels = Image.fromarray(semantic_tensor.semantic_mask.data.cpu().numpy()).load()
        for i in range(result.width):
            for j in range(result.height):
                color = COLOR_MAP[mask_pixels[i, j]]
                scale = grayscale_pixels[i, j]/255
                color = (int(color[0]*scale), int(color[1]*scale), int(color[2]*scale))
                result_pixels[i, j] = color

        ROSResult = ROSImage(header=msg.header, height=result.height, width=result.width, step=result.width*3, encoding='rgb8', is_bigendian=False, data=result.tobytes())

        self._result_pub.publish(ROSResult)
        rospy.loginfo('YOLO NODE: REPORTED')

    def convert_to_pil(self, msg):
        return Image.frombytes('RGB', (msg.width, msg.height), msg.data)

if __name__ == '__main__':
    rospy.init_node('yolo_semantic_processor')
    node = YOLOProcessor('./src/static_assets/yolo26n-sem.pt')

    while not rospy.is_shutdown():
        pass

