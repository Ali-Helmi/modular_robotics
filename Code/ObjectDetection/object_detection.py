def object_detections(queue) :    
    import sys
    #this is where my packages are so do not forget to change to yours
    sys.path.append('C:\Python310\Lib\site-packages')
    import cv2
    import numpy as np

    #you can change these files to tiny if you need to reduce the process load but will also lower the accuracy
    #add them in the directory of the program
    net = cv2.dnn.readNet('yolov3.weights', 'yolov3.cfg')

    #pretrained objects names
    classes = []
    with open("coco.names", "r") as names:
        classes = names.read().splitlines()

    #opening the webcame and throw error if couldn't
    capture= cv2.VideoCapture(0)
    if not capture.isOpened():
        raise IOError("Cannot open webcam")
    
    #keeping track of frames
    frame_id = 0

    while True:
        #extracting each frame and its shape
        ret, frame = capture.read()
        height, width, depth = frame.shape

        blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), (0,0,0), swapRB=True, crop=False)
        net.setInput(blob)
        output_layers_names = net.getUnconnectedOutLayersNames()
        layerOutputs = net.forward(output_layers_names)

        objects = []
        confidences = []
        class_ids = []
        boxes = []
        
        #iterating through everything was detected and assigning values
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.2:
                    #only if confident get coordinates
                    center_x = int(detection[0]*width)
                    center_y = int(detection[1]*height)
                    w = int(detection[2]*width)
                    h = int(detection[3]*height)
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)
                    
                    objects.append([center_x, center_y])
                    boxes.append([x, y, w, h])
                    confidences.append((float(confidence)))
                    class_ids.append(class_id)
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)
        
        if len(indexes)>0:
            for i in indexes.flatten():
                #organizing to be sent in queue
                location_x, location_y = objects[i]
                x, y, w, h = boxes[i] #x, y is lower left corner & x+w, y+h is upper right corner
                label = str(classes[class_ids[i]])
                confidence = str(round(confidences[i],2))
                #ping pong seemed to be identified as sports ball and orange
                if label == "sports ball":
                    obj = ["Ping Pong Ball", location_x, location_y, x, y, w, h]
                    queue.put(frame_id)
                    queue.put(obj)
                if label == "orange":
                    obj = ["Ping Pong Ball", location_x, location_y, x, y, w, h]
                    queue.put(frame_id)
                    queue.put(obj)
        #incrementing frame id to prepare for next
        frame_id = frame_id + 1
