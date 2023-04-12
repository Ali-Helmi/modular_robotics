def object_detection(queue) :

    import cv2
    import supervision as sv
    from ultralytics import YOLO
        
    cap = cv2.VideoCapture(0)
    model = YOLO("C:/Users/i3llo/object_detection/best.pt")

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )


    while True:
        ret, frame = cap.read()
        result = model(frame, agnostic_nms=True)[0]
        detections = sv.Detections.from_yolov8(result)
        labels = [
            f"{model.model.names[class_id]} {confidence:0.2f}"
            for _, confidence, class_id, _
            in detections
        ]
        frame = box_annotator.annotate(
            scene=frame, 
            detections=detections, 
            labels=labels
        )
        
        detected_objects = []
        
        if(len(detections.xyxy) > 0):
            for i in range(len(detections.xyxy)):

                obj_name = labels[i].split(' ', 1)[0]
                obj_confidence = float(labels[i].split(' ', 1)[-1])

                x1 = float(detections.xyxy[i][0])
                y1 = float(detections.xyxy[i][1])
                x2 = float(detections.xyxy[i][2])
                y2 = float(detections.xyxy[i][3])

                base_x = min(x1, x2)
                base_y = min(y1, y2)

                w = abs(x1 - x2)
                h = abs(y1 - y2)

                center_x = w/2 + base_x
                center_y = h/2 + base_y

                area = w*h

                obj = {
                    #IDs (Ball: 0, Bucket: 1, Negative: 2, Tape: 3)
                    'id'    : detections.class_id[i],
                    'conf'  : detections.confidence[i],
                    'x'     : center_x,
                    'y'     : center_y,
                    'size'  : area
                }

                if (detections.confidence[i] > 0.6 and detections.class_id[i] != 2) :
                    detected_objects.append(obj)
                    print("Object added (name: ", obj_name, " with confidence: ", obj_confidence, ")")

        queue.put(['cam', detected_objects])


            
#         cv2.imshow("yolov8", frame)

#         if (cv2.waitKey(30) == 27): # break with escape key
#             break


#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     object_detection()    