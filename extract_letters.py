import cv2
import numpy as np
import os
import json
import uuid
import time

def extract_characters_from_image(image_path, output_dir):
    """
    Extracts individual character images from a handwritten document.

    Args:
        image_path (str): Path to the input handwritten image.
        output_dir (str): Directory where extracted character images will be saved.

    Returns:
        list: A list of filenames of the extracted character images.
    
    Raises:
        ValueError: If the input image cannot be found or read.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise ValueError(f"❌ Error: Image not found or cannot be read at {image_path}")

    # Preprocess the image: Convert to binary (black text on white background)
    # THRESH_BINARY_INV means pixels > 150 become 0 (black), others become 255 (white)
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)

    # --- NEW/REVISED: Clean up noise before dilation and make dilation stronger ---
    # Optional: Morphological Opening to remove small noise/dots BEFORE dilation
    # This helps prevent unwanted connections to tiny artifacts.
    kernel_open = np.ones((2, 2), np.uint8) # Small kernel for opening
    thresh_cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_open)

    # Define a larger kernel for dilation and more iterations for stronger connection.
    # Experiment with these values (e.g., 5x5, 7x7, or even larger if gaps are wide).
    # Increasing iterations will make components "grow" more aggressively.
    kernel_dilate = np.ones((7, 7), np.uint8) # Increased kernel size for stronger connection
    
    # Apply dilation on the cleaned thresholded image
    dilated_thresh = cv2.dilate(thresh_cleaned, kernel_dilate, iterations=3) # Increased iterations
    # --- END NEW/REVISED ---

    # Find contours of the characters on the dilated image.
    contours, _ = cv2.findContours(dilated_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours from left to right (approximates writing order)
    contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    extracted_filenames = []
    char_prefix = f"char_{int(time.time())}_{str(uuid.uuid4())[:4]}"

    for idx, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)

        # Re-evaluate these thresholds. If characters are very small, this might filter them.
        # However, for 'i' and 'j' dots, dilation should make them larger.
        # Adjust these if very small valid characters are being missed.
        if w < 10 or h < 10:
            continue

        # Crop the Region of Interest (ROI) from the *original* thresholded image (thresh).
        # This is important: we use contours from the dilated image for grouping,
        # but crop from the original to maintain the crispness of the character.
        roi = thresh[y:y+h, x:x+w]
        
        # Resize the extracted character ROI to a consistent size (e.g., 80x80 pixels).
        roi_resized = cv2.resize(roi, (80, 80), interpolation=cv2.INTER_AREA)

        # Generate a unique filename for the extracted character image.
        filename = f"{char_prefix}_{idx+1}.png"
        filepath = os.path.join(output_dir, filename)
        
        # Save the resized character image
        cv2.imwrite(filepath, roi_resized)
        extracted_filenames.append(filename)
        
    print(f"✅ Extraction complete! Letters saved in: {output_dir}")
    print("📌 Now, go to the UI to manually assign letters for this new font.")
    return extracted_filenames

# This block runs only if the script is executed directly (not imported)
if __name__ == "__main__":
    print("This script is primarily designed to be called by app.py.")
    print("If you run it directly, you must provide image_path and output_dir.")
    # Example for direct testing (uncomment and replace with actual paths as needed)
    # test_image_path = "path/to/your/handwritten-font.jpg" # e.g., "handwritten-font.jpg"
    # test_output_dir = "extracted_fonts/test_font_manual"
    # os.makedirs(test_output_dir, exist_ok=True)
    # try:
    #     extracted_files = extract_characters_from_image(test_image_path, test_output_dir)
    #     print(f"Extracted files: {extracted_files}")
    # except ValueError as e:
    #     print(e)
