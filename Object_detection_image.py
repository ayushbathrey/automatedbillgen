product_details={
    1: {
    'id': 1,
    'name': 'dell-monitor-D1918H',
    'price': 4000
},

2: {
    'id': 2,
    'name': 'dell-mouse-ms116',
    'price': 400
},

3: {
    'id': 3,
    'name': 'hp-monitor-19ka',
    'price': 4200
},

4: {
    'id': 4,
    'name': 'hp-mouse-X1000',
    'price': 330
},

5: {
    'id': 5,
    'name': 'logitech-keyboard-k400',
    'price': 700
},

6: {
    'id': 6,
    'name': 'logitech-mouse-m185',
    'price': 700
},

7: {
    'id': 7,
    'name': 'samsung-hdd-240gb',
    'price': 1300
},

8: {
    'id': 8,
    'name': 'samsung-monitor-b2030',
    'price': 4200
},

9: {
    'id': 9,
    'name': 'seagate-hdd-240gb',
    'price': 1000
}
}


# Import packages
import os
import cv2
import numpy as np
import sys
import tensorflow as tf

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

detection_graph=''
label_map=''
categories=''
category_index=''
sess=''

def load_tensorflow_to_memory(PATH_TO_IMAGE):
    ######## Image Object Detection Using Tensorflow-trained Classifier #########
    #
    # Author: Team StrawHats
    # Date: 5/10/19
    # Description:
    # This program uses a TensorFlow-trained classifier to perform object detection.
    # It loads the classifier uses it to perform object detection on an image.

    ## Some of the code is copied from Google's example at
    ## https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb

    ## but we changed it to make it more understandable, as per our use case.


    # Name of the directory containing the object detection module we're using
    MODEL_NAME = 'inference_graph'

    # Grab path to current working directory
    CWD_PATH = os.getcwd()

    # Path to frozen detection graph .pb file, which contains the model that is used
    # for object detection.
    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

    # Path to label map file
    PATH_TO_LABELS = os.path.join(CWD_PATH,'training','label_map (2).pbtxt')

    # Path to image
    # PATH_TO_IMAGE = os.path.join(CWD_PATH,IMAGE_NAME)

    # Number of classes the object detector can identify
    NUM_CLASSES = 46

    # Load the label map.
    # Label maps map indices to category names, so that when our convolution
    # network predicts `5`, we know that this corresponds to `king`.
    # Here we use internal utility functions, but anything that returns a
    # dictionary mapping integers to appropriate string labels would be fine
    global category_index
    global label_map
    global categories
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    global detection_graph
    # Load the Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

        global sess
        sess = tf.compat.v1.Session(graph=detection_graph)
    return perform_product_detection(PATH_TO_IMAGE)

def perform_product_detection(PATH_TO_IMAGE):

    # Define input and output tensors (i.e. data) for the object detection classifier

    # Input tensor is the image
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Output tensors are the detection boxes, scores, and classes
    # Each box represents a part of the image where a particular object was detected
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represents level of confidence for each of the objects.
    # The score is shown on the result image, together with the class label.
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

    # Number of objects detected
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Load image using OpenCV and
    # expand image dimensions to have shape: [1, None, None, 3]
    # i.e. a single-column array, where each item in the column has the pixel RGB value
    image = cv2.imread(PATH_TO_IMAGE)
    image_expanded = np.expand_dims(image, axis=0)

    # Perform the actual detection by running the model with the image as input
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: image_expanded})


    import csv
    final_score = np.squeeze(scores)
    count = 0
    for i in range(100):
        if scores is None or final_score[i] > 0.6:
                count = count + 1
    print('Detected Product :',count)
    printcount =0;

    if count!=0:
        for i in classes[0]:
            if(printcount == count):
                break
            printcount = printcount +1
            with open('product_list.csv', mode='a',newline='') as product_file:
                lister =[]
                product_writer = csv.writer(product_file)
                lister.append(category_index[i]['id'])
                product_writer.writerow(lister)
        return [1,count]
    else:
        return [PATH_TO_IMAGE,count]
