# import libraries
import os
import time
import cv2
import numpy as np
from model.yolo_model import YOLO

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

        cv2.circle(image, (int((top + right) / 2), int((left + bottom) / 2)),
                   radius=0, color=(0, 0, 255), thickness=10)

        print('class: {0}, score: {1:.2f}'.format('person', score))
        print('box coordinate x,y,w,h: {0}'.format(box))

    array = [{'x': box[0], 'y': box[1], 'w': box[2], 'h': box[3]}
             for box in boxes]
    print(array)

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

    if boxes is not None:
        draw(image, boxes, scores)

    return image

# detect videos


def detect_video(video, yolo):

    # use yolo v3 to detect video.
    video_path = os.path.join("videos", "test", video)
    camera = cv2.VideoCapture(video_path)
    cv2.namedWindow("detection", cv2.WINDOW_AUTOSIZE)

    # Prepare for saving the detected video
    sz = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
          int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fourcc = cv2.VideoWriter_fourcc(*'mpeg')

    vout = cv2.VideoWriter()
    vout.open(os.path.join("videos", "res", video), fourcc, 20, sz, True)

    while True:
        res, frame = camera.read()

        if not res:
            break

        image = detect_image(frame, yolo)
        cv2.imshow("detection", image)

        # Save the video frame by frame
        vout.write(image)

        if cv2.waitKey(110) & 0xff == 27:
            break

    vout.release()
    camera.release()


if __name__ == '__main__':
    yolo = YOLO(0.6, 0.5)
    # testing
    for i in range(0, 9):
        path = 'artificial_intelligence\object_detection\data\dataset/' + str(i) + '.png'
        print(path)
        image = cv2.imread(path)
        print(image.shape)
        image = detect_image(image, yolo)
        cv2.imwrite('artificial_intelligence\object_detection\output\detected_' + str(i) + '.png', image)
