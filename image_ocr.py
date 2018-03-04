import io
import os
import requests
import cv2

image_name = "capture.jpg"
keypress = "q";
data_filename = "data.csv"

# Captures image from webcam on "q" keypress
def take_image(filename, keypress):
    cap = cv2.VideoCapture(0)
    while(True):
        ret, frame = cap.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        cv2.imshow('frame', rgb)
        if cv2.waitKey(1) & 0xFF == ord(keypress):
            out = cv2.imwrite(filename, frame)
            break
    cap.release()
    cv2.destroyAllWindows()

# Take image
take_image(image_name, keypress)

# Parameters for Microsoft Cognitive Services
subscription_key = "42c9ccf77bb44fe8b94b649b7877acad"
vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v1.0/"
vision_analyze_url = vision_base_url + "analyze"
ocr_url = vision_base_url + "ocr"
image_data = open(image_name, "rb").read()

# Request Microsoft Cognitive Services
headers  = {'Ocp-Apim-Subscription-Key': subscription_key,
    "Content-Type": "application/octet-stream" }
params   = {'language': 'unk', 'detectOrientation ': 'true'}
response = requests.post(ocr_url,
                         headers=headers,
                         params=params,
                         data=image_data)
response.raise_for_status()

# Parse returned analysis
analysis = response.json()

for region in analysis["regions"]:
    for line in region["lines"]:
        for word in line["words"]:
            print(word["text"], end=" ")
        print()

open(data_filename, 'w').close()

with open(data_filename, 'a') as file:
    for region in analysis["regions"]:
        for line in region["lines"]:
            for word in line["words"]:
                
                file.write(word["text"])
                file.write(",")
