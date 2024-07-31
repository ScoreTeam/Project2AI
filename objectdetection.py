import object_detection
import os
import time
import cv2
import numpy as np
from object_detection.model.yolo_model import YOLO

# preprocess images
def process_image(img):

    image = cv2.resize(img, (416, 416), interpolation=cv2.INTER_CUBIC)
    image = np.array(image, dtype='float32')
    image /= 255.
    image = np.expand_dims(image, axis=0)

    return image

# draw detected boxes
def draw(image, boxes, scores):

    for box, score in zip(boxes, scores):
        x, y, w, h = box

        top = max(0, np.floor(x + 0.5).astype(int))
        left = max(0, np.floor(y + 0.5).astype(int))
        right = min(image.shape[1], np.floor(x + w + 0.5).astype(int))
        bottom = min(image.shape[0], np.floor(y + h + 0.5).astype(int))
                
        cv2.rectangle(image, (top, left), (right, bottom), (255, 0, 0), 2)
        
        cv2.putText(image, '{0} {1:.2f}'.format('person', score),
                    (top, left - 6),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 255), 1,
                    cv2.LINE_AA)
        
        cv2.circle(image, (int((top + right) / 2), int((left + bottom) / 2)), radius=0, color=(0, 0, 255), thickness=10)

        print('class: {0}, score: {1:.2f}'.format('person', score))
        print('box coordinate x,y,w,h: {0}'.format(box))

    array = [{'x': box[0], 'y': box[1], 'w': box[2], 'h': box[3]} for box in boxes]        
    # print(array)
    return array

# detect images
def detect_image(image, yolo):
    
    processed_image = process_image(image)

    start = time.time()
    boxes, _, scores = yolo.predict(processed_image, image.shape)
    end = time.time()

    print('time: {0:.2f}s'.format(end - start))

#   explain how print statement works
#   {0} indicates that a value will be inserted at this position
#   `:.2f` is a format specifier that tells Python to format the value as a floating-point number with 2 decimal places
#   `.format(end - start)` This method is used to insert values into the placeholders within a string
    box_coordinate=[]
    if boxes is not None:
        # person_location = distance(boxes)
        # print(person_location)
        box_coordinate=draw(image, boxes, scores)

    return image,box_coordinate

class ObjectDetection:
    def __init__(self):
        self.yolo=YOLO(obj_threshold=0.5, nms_threshold=0.5)
        pass
    # import yolo model
    
    def DetectImage(self,frame):
        # path = 'data/dataset/'+ str(i) +'.png'
        image = cv2.imread(frame)
        # print(image.shape)
        image,box_coordinate = detect_image(image, self.yolo)
        # cv2.imshow("detected",image)
        cv2.imread("output/detected/detected_test.jpg")
        # cv2.waitKey(0)
        increameant=1
        path="output/detected"
        while os.path.exists(path):
                cv2.imwrite(f'{path}_'+ str(increameant) +'.png', image)
                increameant+=1
        return box_coordinate
       
        