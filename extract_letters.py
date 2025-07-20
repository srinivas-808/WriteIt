import cv2
import numpy as np
import os
import json
import uuid
import time

def extract_characters_from_image(image_path, output_dir):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise ValueError(f"❌ Error: Image not found or cannot be read at {image_path}")

    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)

    # --- NEW: Morphological Operations to connect characters ---
    # Define a kernel for dilation (e.g., a 3x3 or 5x5 rectangle)
    kernel = np.ones((3, 3), np.uint8) # You might need to experiment with kernel size
    # Apply dilation to connect nearby components
    dilated_thresh = cv2.dilate(thresh, kernel, iterations=1)
    # --- END NEW ---

    # Find contours on the dilated image
    contours, _ = cv2.findContours(dilated_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

    os.makedirs(output_dir, exist_ok=True)

    extracted_filenames = []
    char_prefix = f"char_{int(time.time())}_{str(uuid.uuid4())[:4]}"

    for idx, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)

        if w < 10 or h < 10: # Still ignore very small noise
            continue

        # Use the original thresholded image for cropping, but contours from dilated
        # This preserves crispness while ensuring connected components are grouped
        roi = thresh[y:y+h, x:x+w]
        roi_resized = cv2.resize(roi, (80, 80))

        filename = f"{char_prefix}_{idx+1}.png"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, roi_resized)
        extracted_filenames.append(filename)
        
    print(f"✅ Extraction complete! Letters saved in: {output_dir}")
    print("📌 Now, go to the UI to manually assign letters for this new font.")
    return extracted_filenames

# ... (rest of extract_letters.py remains the same) ...

# The __main__ block should ideally be removed or modified for testing purposes,
# as this script is now intended to be called by app.py.
if __name__ == "__main__":
    print("This script is primarily designed to be called by app.py.")
    print("If you run it directly, you must provide image_path and output_dir.")
    # Example for direct testing (replace with actual paths as needed)
    # test_image_path = r"C:\Users\srini\Desktop\HandWriting(safe)\backend\handwritten-font.jpg"
    # test_output_dir = "extracted_fonts/test_font_manual"
    # os.makedirs(test_output_dir, exist_ok=True)
    # try:
    #     extract_characters_from_image(test_image_path, test_output_dir)
    # except ValueError as e:
    #     print(e)