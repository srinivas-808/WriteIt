import os
import json
import cv2
import numpy as np
import sys

# Paths
IMAGE_FOLDER = "extracted_letters"
MAPPING_FILE = os.path.join(IMAGE_FOLDER, "character_mapping.json")

# Load character mapping
with open(MAPPING_FILE, "r") as f:
    char_mapping = json.load(f)

# Load character images into a dictionary
def load_character_images():
    char_images = {}
    for char, filename in char_mapping.items():
        img_path = os.path.join(IMAGE_FOLDER, filename)
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            img = cv2.bitwise_not(img)  # Convert to white background with black text

            h, w = img.shape

            # Small letters to half height
            if char in "aceimnorsuvwxz":
                img = cv2.resize(img, (w, h // 2), interpolation=cv2.INTER_AREA)

            # Descenders (extend below baseline)
            elif char in "gjpqy":
                img = cv2.resize(img, (w, h // 2), interpolation=cv2.INTER_AREA)
                img = np.pad(img, ((h // 2, 0), (0, 0)), mode="constant", constant_values=255)

            char_images[char] = img

    print(f"✅ Loaded {len(char_images)} characters.")
    return char_images

# Generate handwritten text image with multi-line support
def generate_text_image(text, output_path="generated_text_multiline.png"):
    char_images = load_character_images()
    space_width = 50  # Space width
    line_spacing = 30  # Space between lines

    # Get maximum character height for alignment
    max_char_height = max(img.shape[0] for img in char_images.values())
    space_image = np.ones((max_char_height, space_width), dtype=np.uint8) * 255  # White space

    lines = text.strip().split("\n")
    line_images = []
    max_width = 0

    for line in lines:
        generated_images = []
        for char in line:
            if char == " ":
                generated_images.append(space_image)  # Add space
            elif char in char_images:
                generated_images.append(char_images[char])
            else:
                print(f"⚠️ Warning: No image found for '{char}'")

        if generated_images:
            max_height = max(img.shape[0] for img in generated_images)
            
            # Adjust height of characters to align within the line
            for i in range(len(generated_images)):
                h, w = generated_images[i].shape
                pad_top = max_height - h
                generated_images[i] = np.pad(generated_images[i], ((pad_top, 0), (0, 0)), mode="constant", constant_values=255)

            line_image = np.hstack(generated_images)
            line_images.append(line_image)
            max_width = max(max_width, line_image.shape[1])

    # **Ensure all lines have equal width**
    for i in range(len(line_images)):
        h, w = line_images[i].shape
        if w < max_width:
            line_images[i] = np.pad(line_images[i], ((0, 0), (0, max_width - w)), mode="constant", constant_values=255)

    # **Add line spacing**
    spaced_lines = []
    for line_image in line_images:
        spaced_lines.append(line_image)
        spaced_lines.append(np.ones((line_spacing, max_width), dtype=np.uint8) * 255)  # Add line spacing

    if not spaced_lines:
        print("❌ No valid characters found. Cannot generate text.")
        return None

    output_image = np.vstack(spaced_lines)

    # **Create a larger white canvas with padding**
    final_height, final_width = output_image.shape
    large_canvas = np.ones((final_height + 100, final_width + 100), dtype=np.uint8) * 255  # Extra padding

    # **Center the text on the larger canvas**
    y_offset = (large_canvas.shape[0] - final_height) // 2
    x_offset = (large_canvas.shape[1] - final_width) // 2
    large_canvas[y_offset:y_offset + final_height, x_offset:x_offset + final_width] = output_image

    # **Save output image**
    cv2.imwrite(output_path, large_canvas)
    print(f"✅ Handwritten text generated: {output_path}")
    return output_path

# Run if script is executed directly
if __name__ == "__main__":
    print("Enter the text you want to generate (press Ctrl+D to finish input):")
    user_text = sys.stdin.read()  # Accepts multi-line input
    generate_text_image(user_text)
