def object_detections() :    
    import sys
    sys.path.append('C:\Python310\Lib\site-packages')
    import cv2
    import numpy as np

    net = cv2.dnn.readNet('yolov3-tiny.weights', 'yolov3.cfg')

    classes = []
    with open("coco.names", "r") as names:
        classes = names.read().splitlines()

    capture= cv2.VideoCapture(0)
    if not capture.isOpened():
        raise IOError("Cannot open webcam")

    while True:
        ret, frame = capture.read()
        height, width, depth = frame.shape

        blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), (0,0,0), swapRB=True, crop=False)
        net.setInput(blob)
        output_layers_names = net.getUnconnectedOutLayersNames()
        layerOutputs = net.forward(output_layers_names)

        objects = []
        confidences = []
        class_ids = []

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.2:
                    center_x = int(detection[0]*width)
                    center_y = int(detection[1]*height)

                    objects.append([center_x, center_y])
                    confidences.append((float(confidence)))
                    class_ids.append(class_id)

        if len(objects)>0:
            for i in range(len(objects)):
                label = str(classes[class_ids[i]])
                confidence = str(round(confidences[i],2))
                print("Object Detected: " + label + " with accuracy of " + confidence)
                #print("Object location x: " + objects[i][0] + " y: " + objects[i][1])
        
        key = cv2.waitKey(1)
        if key==27:
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    object_detections()