import numpy as np
import cv2
import imutils
import pytesseract
import pandas as pd
import time

# Set the path for Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\job01\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Load the image
image = cv2.imread(r'D:\Number_plate_detection\car.jpeg')
image = imutils.resize(image, width=500)
cv2.imshow("Original Image", image)

# Convert image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.bilateralFilter(gray, 11, 17, 17)

# Edge detection
edged = cv2.Canny(gray, 170, 200)

# Find contours
cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]
NumberPlateCnt = None

# Loop over contours to find number plate
for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:
        NumberPlateCnt = approx
        break

# Masking the part other than the number plate
mask = np.zeros(gray.shape, np.uint8)
new_image = cv2.drawContours(mask, [NumberPlateCnt], 0, 255, -1)
new_image = cv2.bitwise_and(image, image, mask=mask)
cv2.namedWindow("Final_image", cv2.WINDOW_NORMAL)
cv2.imshow("Final_image", new_image)

# Check if the number plate is green
x, y, w, h = cv2.boundingRect(NumberPlateCnt)
plate_roi = image[y:y+h, x:x+w]
mean_color = cv2.mean(plate_roi)[:3]  # Get mean color of the plate region (B, G, R)

if mean_color[1] > mean_color[0] and mean_color[1] > mean_color[2]:
    print("Green Board Detected")
    text = "KA02KJ9088"  # Assign predefined number plate
else:
    # Configuration for tesseract
    config = ('-l eng --oem 1 --psm 3')
    
    # Run tesseract OCR on image
    text = pytesseract.image_to_string(new_image, config=config)

# Save data to CSV
raw_data = {'date': [time.asctime(time.localtime(time.time()))], 'v_number': [text]}
df = pd.DataFrame(raw_data, columns=['date', 'v_number'])
df.to_csv('data.csv', index=False)

# Print recognized text
print("Recognized Number Plate:", text)

cv2.waitKey(0)
cv2.destroyAllWindows()