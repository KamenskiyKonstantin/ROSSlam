from PIL import Image
from sensor_msgs.msg import Image as ROSImage

# ROS_MODE_TO_PIL = {
#
# }

def convert_from_ROS(image):
    return Image.frombytes('RGB', (image.width, image.height), image.data)
