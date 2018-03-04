import io
import os
import requests
import cv2

image_name = "capture.jpg"
keypress = "q";
data_filename = "data.txt"

# Captures image from webcam on "q" keypress
def take_image(filename, keypress):
    cap = cv2.VideoCapture(0)
    while(True):
        ret, frame = cap.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
#        gray_img = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
#        retval2,threshold2 = cv2.threshold(gray_img,80,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        threshold2 = rgb
        cv2.imshow('frame', threshold2)
        if cv2.waitKey(1) & 0xFF == ord(keypress):
            cv2.imwrite('capture.jpg', threshold2)
            out = cv2.imwrite(filename, threshold2)
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

## Request Microsoft Cognitive Services
#headers  = {'Ocp-Apim-Subscription-Key': subscription_key,
#    "Content-Type": "application/octet-stream" }
#params   = {'language': 'unk', 'detectOrientation ': 'true'}
#response = requests.post(ocr_url,
#                         headers=headers,
#                         params=params,
#                         data=image_data)
#response.raise_for_status()


# Request Microsoft Cognitive Services
headers  = {'Ocp-Apim-Subscription-Key': subscription_key,
    "Content-Type": "application/octet-stream" }
params   = {'handwriting' : True}
response = requests.post(ocr_url,
                         headers=headers,
                         params=params,
                         data=image_data)
response.raise_for_status()


# Parse returned analysis
analysis = response.json()
print("*** JSON ***\n\n", analysis, "\n\n*** End of JSON ***")

print("\n\n*** Start of Text ***\n")
for region in analysis["regions"]:
    for line in region["lines"]:
        print("\n----")
        for word in line["words"]:
            print(word["text"], end=" ")
    print("\n----")
print("\n\n*** End of Text ***\n\n")

#
#open(data_filename, 'w').close()
#
#with open(data_filename, 'a') as file:
#    for region in analysis["regions"]:
#        for line in region["lines"]:
#            for word in line["words"]:
#
#                file.write(word["text"])
#                file.write(" ")
##                file.write(",")

max_box_height = -1
max_box_region = ""

lines_array = []
for region in analysis["regions"]:
    for line in region["lines"]:
        bounding_box = line["boundingBox"].split(",")
        line_content = ""
        for word in line["words"]:
            line_content += word["text"] + " "
        lines_array.append(line_content)
#        size = 0
#        for len in bounding_box:
        height = int(bounding_box[3])
        print("*** Found box of height: ", height)
        if (height > max_box_height):
            max_box_height = height
            max_box_region = line

print("*** Max height found: ", max_box_height)

event_title = ""
for word in max_box_region["words"]:
    event_title += word["text"] + " "

all_text = ""
for line in lines_array:
    all_text += line.replace("-"," ") + " "

print("\n\n*** All text: \n", all_text)

# Find location
from google.cloud import language

client = language.LanguageServiceClient()

def entities_text(text):
    """Detects entities in the text."""
    client = language.LanguageServiceClient()
    document = language.types.Document(content=text, type=language.enums.Document.Type.PLAIN_TEXT)

    # Detects entities in the document.
    entities = client.analyze_entities(document).entities

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION', 'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

    max_salience = -1
    out = ""
    for entity in entities:
        if (entity.type == 2):
            return entity.name
#        print('=' * 20)
#        print(entity.name)
#        print(entity_type[entity.type])
#        print(u'{:<16}: {}'.format('salience', entity.salience))
#        print(u'{:<16}: {}'.format('wikipedia_url',entity.metadata.get('wikipedia_url', '-')))
#        if (entity.type == 2):  or (entity.type == 3): # Find locations and organizations
#            if (entity.salience > max_salience):
#                max_salience = entity.salience
#                out = entity.name
    return ""

location = ""
for line in lines_array:
    location += entities_text(line)
    if location != "":
        break
print(location)

# Get current time
import datetime
event_datetime_start = str(datetime.datetime.now()).replace(" ","T").split(".")[0]+"-07:00"
event_datetime_end = str(datetime.datetime.now() + datetime.timedelta(hours=1)).replace(" ","T").split(".")[0]+"-07:00"

# Final CSV export

import csv

list = [event_title,event_datetime_start,event_datetime_end,location]
csvfile = "events.csv"

with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(list)

###

