#!/usr/bin/env python3
import rospy

from PIL import Image, ImageOps
from sensor_msgs.msg import Image as ROSImage
from time import time_ns
from ultralytics import YOLO
rospy.loginfo("YOLO imported")


class YOLOClass:
    def __init__(self, yolo_id, color, comment='unknown'):
        self.yolo_id = yolo_id
        self.color = color
        self.comment = comment

    def __str__(self):
        return f"YOLO Class '{self.comment}' at id {self.yolo_id}, colored as {self.color}"

    def check_color(self, color):
        return self.color == color

    def get_id(self):
        return self.yolo_id

    def get_color(self):
        return self.color

class YOLOClassCollection:
    def __init__(self, collection):
        self.collection = collection

    def find_class_by_color(self, color):
        for item in self.collection:
            if item.check_color(color):
                return item
        return None

    def find_color(self, id):
        for item in self.collection:
            if item.get_id() == id:
                return item.get_color()

COLOR_MAP = YOLOClassCollection([
    YOLOClass(0,  (255, 0, 0),     "Red"),
    YOLOClass(1,  (0, 255, 0),     "Green"),
    YOLOClass(2,  (0, 0, 255),     "Blue"),
    YOLOClass(3,  (255, 255, 0),   "Yellow"),
    YOLOClass(4,  (255, 0, 255),   "Magenta"),
    YOLOClass(5,  (0, 255, 255),   "Cyan"),
    YOLOClass(6,  (255, 128, 0),   "Orange"),
    YOLOClass(7,  (128, 0, 255),   "Purple"),
    YOLOClass(8,  (255, 0, 128),   "Hot Pink"),
    YOLOClass(9,  (0, 128, 255),   "Sky Blue"),
    YOLOClass(10, (128, 255, 0),   "Lime"),
    YOLOClass(11, (0, 255, 128),   "Spring Green"),
    YOLOClass(12, (128, 0, 0),     "Maroon"),
    YOLOClass(13, (0, 128, 0),     "Dark Green"),
    YOLOClass(14, (0, 0, 128),     "Navy"),
    YOLOClass(15, (255, 128, 128), "Light Coral"),
    YOLOClass(16, (128, 255, 255), "Light Cyan"),
    YOLOClass(17, (255, 128, 255), "Light Pink"),
    YOLOClass(18, (128, 128, 128), "Gray"),
])
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
                color = COLOR_MAP.find_color(mask_pixels[i, j])
                scale = 1
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

