import os
import json
import cv2
import numpy as np
import sys

# Removed hardcoded IMAGE_FOLDER and MAPPING_FILE
# These will now be passed as arguments to the functions

# Load character mapping and images from a specific font folder
def load_character_images(font_image_folder, mapping_file_path):
    # Ensure the mapping file exists
    if not os.path.exists(mapping_file_path):
        print(f"❌ Error: Mapping file not found at {mapping_file_path}")
        return {}

    with open(mapping_file_path, "r") as f:
        char_mapping = json.load(f)

    char_images = {}
    for char, filename in char_mapping.items():
        img_path = os.path.join(font_image_folder, filename) # Use the passed font_image_folder
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                print(f"⚠️ Warning: Could not read image file: {img_path}")
                continue
            
            img = cv2.bitwise_not(img) 

            h, w = img.shape

            if char in "aceimnorsuvwxz":
                # Ensure height is not zero before resizing
                if h > 0:
                    img = cv2.resize(img, (w, max(1, h // 2)), interpolation=cv2.INTER_AREA)
                else:
                    print(f"⚠️ Warning: Image for '{char}' has zero height, skipping resize.")

            elif char in "gjpqy":
                if h > 0:
                    resized_img = cv2.resize(img, (w, max(1, h // 2)), interpolation=cv2.INTER_AREA)
                    # Pad to original height to account for descenders
                    img = np.pad(resized_img, ((h - resized_img.shape[0], 0), (0, 0)), mode="constant", constant_values=255)
                else:
                    print(f"⚠️ Warning: Image for '{char}' has zero height, skipping resize and padding.")
                    
            char_images[char] = img
        else:
            print(f"⚠️ Warning: Image file not found for character '{char}': {img_path}")
            
    print(f"✅ Loaded {len(char_images)} characters from {font_image_folder}.")
    return char_images

# Generate handwritten text image with multi-line support
def generate_text_image(text, output_path="generated_text_multiline.png", 
                        font_image_folder=None, mapping_file_path=None): # Now accepts these args
    
    if font_image_folder is None or mapping_file_path is None:
        print("❌ Error: font_image_folder and mapping_file_path must be provided.")
        # Fallback to previous default or raise error
        # For a robust system, this should probably raise an error
        # For now, let's just use the hardcoded path if not provided (for backward compat if desired)
        # However, for this new font-specific system, it should always be provided.
        # Let's enforce it.
        raise ValueError("Font image folder and mapping file path are required for text generation.")

    char_images = load_character_images(font_image_folder, mapping_file_path)
    
    if not char_images:
        print("❌ No character images loaded. Cannot generate text.")
        return None

    space_width = 50
    line_spacing = 30

    # Get maximum character height for alignment from the loaded characters
    # Filter out empty images if any
    valid_char_images = [img for img in char_images.values() if img is not None and img.size > 0]
    if not valid_char_images:
        print("❌ No valid character images to determine max height.")
        return None
    
    max_char_height = max(img.shape[0] for img in valid_char_images)
    space_image = np.ones((max_char_height, space_width), dtype=np.uint8) * 255

    lines = text.strip().split("\n")
    line_images = []
    max_width = 0

    for line in lines:
        generated_images = []
        for char in line:
            if char == " ":
                generated_images.append(space_image)
            elif char in char_images and char_images[char] is not None and char_images[char].size > 0:
                generated_images.append(char_images[char])
            else:
                print(f"⚠️ Warning: No image found or invalid image for '{char}'")

        if generated_images:
            max_height_in_line = max(img.shape[0] for img in generated_images)
            
            for i in range(len(generated_images)):
                h, w = generated_images[i].shape
                # Pad at top to align characters to the bottom of the "line box"
                pad_top = max_height_in_line - h
                generated_images[i] = np.pad(generated_images[i], ((pad_top, 0), (0, 0)), mode="constant", constant_values=255)

            line_image = np.hstack(generated_images)
            line_images.append(line_image)
            max_width = max(max_width, line_image.shape[1])

    for i in range(len(line_images)):
        h, w = line_images[i].shape
        if w < max_width:
            line_images[i] = np.pad(line_images[i], ((0, 0), (0, max_width - w)), mode="constant", constant_values=255)

    spaced_lines = []
    for line_image in line_images:
        spaced_lines.append(line_image)
        spaced_lines.append(np.ones((line_spacing, max_width), dtype=np.uint8) * 255)

    if not spaced_lines:
        print("❌ No valid characters found. Cannot generate text.")
        return None

    output_image = np.vstack(spaced_lines)

    final_height, final_width = output_image.shape
    large_canvas = np.ones((final_height + 100, final_width + 100), dtype=np.uint8) * 255

    y_offset = (large_canvas.shape[0] - final_height) // 2
    x_offset = (large_canvas.shape[1] - final_width) // 2
    large_canvas[y_offset:y_offset + final_height, x_offset:x_offset + final_width] = output_image

    cv2.imwrite(output_path, large_canvas)
    print(f"✅ Handwritten text generated: {output_path}")
    return output_path

if __name__ == "__main__":
    print("This script is primarily designed to be called by app.py.")
    print("If you run it directly, you must provide text, output_path, font_image_folder, and mapping_file_path.")
    # Example for direct testing:
    # test_text = "Hello World!"
    # test_output_path = "generated_test_output.png"
    # test_font_folder = "extracted_fonts/test_font_manual" # Must match a created font folder
    # test_mapping_file = os.path.join(test_font_folder, "character_mapping.json")
    # if os.path.exists(test_font_folder) and os.path.exists(test_mapping_file):
    #     generate_text_image(test_text, test_output_path, test_font_folder, test_mapping_file)
    # else:
    #     print("Test font folder or mapping file not found. Please create and map a font first.")