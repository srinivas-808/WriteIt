import cv2
import numpy as np
import os
import json

# Load Image
image_path = r"C:\Users\srini\Desktop\HandWriting(safe)\backend\handwritten-font.jpg"
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

if image is None:
    print("❌ Error: Image not found or cannot be read.")
    exit()

# Preprocess the image (Thresholding)
_, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)

# Find contours of the characters
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Sort contours from left to right (writing order)
contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

# Output folder for extracted letters
output_dir = "extracted_letters"
os.makedirs(output_dir, exist_ok=True)

# Dictionary to store character mappings
char_map = {}

# Extract and save each character
for idx, contour in enumerate(contours):
    x, y, w, h = cv2.boundingRect(contour)

    # Ignore very small noise
    if w < 10 or h < 10:
        continue

    # Crop & Resize
    roi = thresh[y:y+h, x:x+w]
    roi_resized = cv2.resize(roi, (80, 80))  # Higher quality

    # Save with generic naming
    filename = f"char_{idx+1}.png"
    cv2.imwrite(os.path.join(output_dir, filename), roi_resized)

    char_map[filename] = ""  # Placeholder for manual mapping

# Save the initial mapping file
mapping_file = os.path.join(output_dir, "character_mapping.json")
with open(mapping_file, "w") as f:
    json.dump(char_map, f, indent=4)

print("✅ Extraction complete! Letters saved in:", output_dir)
print("📌 Now, run the character mapping script to manually assign letters.")
