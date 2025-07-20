import os
import json
import cv2
import numpy as np
import sys

# Constants for character sizing and alignment.
# These values are crucial for good visual output and might require calibration
# based on the specific handwriting style and extracted character sizes.

# FULL_CHAR_BOX_HEIGHT: The total height of the individual character's canvas.
# This must be large enough to accommodate the tallest ascender and deepest descender.
# Retaining previous value, as it should be sufficient if placement is correct.
FULL_CHAR_BOX_HEIGHT = 160 

# BASELINE_POSITION_RATIO: Defines where the baseline sits within the FULL_CHAR_BOX_HEIGHT.
# E.g., 0.75 means the baseline is at 75% from the top of the character box.
# Adjusted to give more room for descenders below the baseline.
# This ratio is critical for vertical alignment.
BASELINE_POSITION_RATIO = 0.55 

# X_HEIGHT_RATIO: The proportion of the height *above the baseline* that 'x-height' letters occupy.
# This defines the height of characters like 'a', 'c', 'e' relative to the ascender height.
X_HEIGHT_RATIO = 0.65 

# CHARACTER_HORIZONTAL_PADDING: Extra horizontal space added around each character's ink.
# This controls the spacing between individual characters. Decrease for tighter spacing.
CHARACTER_HORIZONTAL_PADDING = 0 # Set to 0 for very tight character spacing, relying on natural character width

# BASE_LETTER_SCALE_FACTOR: Overall scaling factor applied to all characters.
# Adjust this to make all characters proportionally smaller or larger overall.
BASE_LETTER_SCALE_FACTOR = 0.9 

# DESCENDER_SCALE_FACTOR: Scaling factor specifically for descending letters.
# This factor will now be applied to the ASCENDER_HEIGHT to determine the descender's overall size.
# A value of 1.0 would make them the same height as ascenders.
# Increased slightly to make descenders proportionally larger than ascenders, which is natural.
DESCENDER_SCALE_FACTOR = 1.1 # Adjusted to make descenders slightly taller than ascenders, proportionally.

def load_character_images(font_image_folder, mapping_file_path):
    """
    Loads character images from a specified font folder and prepares them for generation.
    Each character is placed onto a consistent canvas to ensure proper vertical alignment
    (baseline, x-height, ascenders, descenders) and controlled horizontal spacing.

    Args:
        font_image_folder (str): Path to the directory containing extracted character images.
        mapping_file_path (str): Path to the JSON file containing character mappings.

    Returns:
        tuple: A tuple containing:
            - dict: A dictionary where keys are characters and values are prepared NumPy arrays (images).
            - int: The calculated height of a single line of characters (FULL_CHAR_BOX_HEIGHT).
    
    Raises:
        ValueError: If the mapping file is not found.
    """
    if not os.path.exists(mapping_file_path):
        raise ValueError(f"❌ Error: Mapping file not found at {mapping_file_path}")

    with open(mapping_file_path, "r") as f:
        char_mapping = json.load(f)

    char_images = {}

    # Calculate the actual baseline Y-coordinate on the canvas (from the top)
    BASELINE_Y_COORD = int(FULL_CHAR_BOX_HEIGHT * BASELINE_POSITION_RATIO)
    
    # Calculate the height for capital letters and ascenders (from baseline up)
    ASCENDER_HEIGHT = BASELINE_Y_COORD

    # Calculate the height for x-height letters (from baseline up)
    X_HEIGHT = int(ASCENDER_HEIGHT * X_HEIGHT_RATIO)

    # Calculate the depth for descenders (from baseline down)
    DESCENDER_DEPTH = FULL_CHAR_BOX_HEIGHT - BASELINE_Y_COORD

    for char, filename in char_mapping.items():
        img_path = os.path.join(font_image_folder, filename)
        if img_path is None or not os.path.exists(img_path): # Added check for None img_path
            print(f"⚠️ Warning: Image file not found for character '{char}': {img_path}")
            continue
            
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"⚠️ Warning: Could not read image file: {img_path}")
            continue
        
        # Invert colors: ensure black text on white background for consistency
        img = cv2.bitwise_not(img) 

        current_h, current_w = img.shape
        if current_h == 0 or current_w == 0:
            print(f"⚠️ Warning: Image for '{char}' has zero dimension, skipping.")
            continue

        # Determine target height for resizing based on character type
        target_resize_h = ASCENDER_HEIGHT # Default for capitals/ascenders
        
        if char in "aceimnorsuvwxz": # X-height characters
            target_resize_h = X_HEIGHT + 10
        elif char in "gjpqy": # Descenders
            # --- REVISED: Scale descenders based on ASCENDER_HEIGHT and DESCENDER_SCALE_FACTOR ---
            # This makes their overall height proportional to ascenders, then fine-tuned.
            target_resize_h = int(ASCENDER_HEIGHT * DESCENDER_SCALE_FACTOR) 
            # Ensure it doesn't exceed the full available height for descenders
            target_resize_h = min(target_resize_h, FULL_CHAR_BOX_HEIGHT)
            # --- END REVISED ---

        # Apply BASE_LETTER_SCALE_FACTOR (applied to all characters)
        target_resize_h = int(target_resize_h * BASE_LETTER_SCALE_FACTOR)
        target_resize_h = max(1, target_resize_h) # Ensure it's at least 1 pixel

        # Resize the character image maintaining aspect ratio
        # Ensure new_w is at least 1 to prevent errors with very thin characters
        new_w = int(current_w * (target_resize_h / current_h))
        img_resized = cv2.resize(img, (max(1, new_w), target_resize_h), interpolation=cv2.INTER_AREA)

        # Calculate effective character width for tighter spacing
        # Find the bounding box of the actual ink within the resized character image.
        # This helps to remove excess horizontal whitespace from the extracted character.
        coords = cv2.findNonZero(img_resized)
        if coords is not None:
            x_ink, y_ink, w_ink, h_ink = cv2.boundingRect(coords)
            # Use w_ink for the effective width of the character's ink
        else:
            # If no ink found (e.g., blank image or extraction error), default to a small width
            w_ink = 10 # A small default width for empty/problematic chars

        # Define the total width of the character's individual canvas.
        # This is the ink width plus padding on both sides.
        effective_char_width = w_ink + CHARACTER_HORIZONTAL_PADDING * 2 
        effective_char_width = max(effective_char_width, 1) # Ensure width is at least 1 pixel

        # Create the canvas for this character with the full character box height and effective width
        char_canvas = np.ones((FULL_CHAR_BOX_HEIGHT, effective_char_width), dtype=np.uint8) * 255
        
        # Determine vertical placement (y_offset) on the char_canvas
        y_offset_on_canvas = 0 

        if char in "aceimnorsuvwxz": # X-height characters
            # Place these characters such that their bottom aligns with the baseline.
            y_offset_on_canvas = BASELINE_Y_COORD - img_resized.shape[0]
        elif char in "gjpqy": # Descenders
            # For descenders, place their *visual baseline* (which is typically where the x-height letters sit)
            # at the calculated BASELINE_Y_COORD. This means the top of their body aligns with x-height letters.
            y_offset_on_canvas = BASELINE_Y_COORD - X_HEIGHT 
        else: # Capital letters, ascenders, numbers, punctuation
            # Place these characters such that their bottom aligns with the baseline.
            y_offset_on_canvas = BASELINE_Y_COORD - img_resized.shape[0]

        # Place the resized character onto its individual canvas
        # Calculate horizontal placement to center the ink within its effective_char_width
        x_placement_on_canvas = (effective_char_width - img_resized.shape[1]) // 2
        
        # Ensure indices are within bounds for copying
        y_start_src = 0
        y_end_src = img_resized.shape[0]
        x_start_src = 0
        x_end_src = img_resized.shape[1]

        y_start_dest = max(0, y_offset_on_canvas)
        y_end_dest = min(y_start_dest + img_resized.shape[0], char_canvas.shape[0])
        x_start_dest = max(0, x_placement_on_canvas)
        x_end_dest = min(x_start_dest + img_resized.shape[1], char_canvas.shape[1])

        # Adjust source slices if destination goes out of bounds
        if y_end_dest - y_start_dest < img_resized.shape[0]:
            y_end_src = y_start_src + (y_end_dest - y_start_dest)
        if x_end_dest - x_start_dest < img_resized.shape[1]:
            x_end_src = x_start_src + (x_end_dest - x_start_dest)

        # Perform the copy if dimensions are valid
        if y_end_dest > y_start_dest and x_end_dest > x_start_dest and \
           y_end_src > y_start_src and x_end_src > x_start_src:
            char_canvas[y_start_dest:y_end_dest, x_start_dest:x_end_dest] = \
                img_resized[y_start_src:y_end_src, x_start_src:x_end_src]
        else:
            print(f"⚠️ Warning: Skipping placement for char '{char}' due to invalid slice dimensions after resize.")
            # Fallback to a blank canvas if placement fails
            char_canvas = np.ones((FULL_CHAR_BOX_HEIGHT, effective_char_width), dtype=np.uint8) * 255
        
        char_images[char] = char_canvas
    else:
        print(f"⚠️ Warning: Image file not found for character '{char}'': {img_path}")
        
    print(f"✅ Loaded {len(char_images)} characters from {font_image_folder}.")
    return char_images, FULL_CHAR_BOX_HEIGHT

def generate_text_image(text, output_path="generated_text_multiline.png", 
                        font_image_folder=None, mapping_file_path=None):
    """
    Generates a handwritten text image from input text using loaded character images.

    Args:
        text (str): The input text to be converted. Supports multi-line with '\n'.
        output_path (str): Path where the generated image will be saved.
        font_image_folder (str): Directory containing the extracted character images.
        mapping_file_path (str): JSON file with character to filename mappings.

    Returns:
        str: The path to the generated image, or None if generation fails.
    
    Raises:
        ValueError: If font_image_folder or mapping_file_path are not provided.
    """
    if font_image_folder is None or mapping_file_path is None:
        raise ValueError("Font image folder and mapping file path are required for text generation.")

    char_images, full_char_box_height = load_character_images(font_image_folder, mapping_file_path)
    
    if not char_images:
        print("❌ No character images loaded. Cannot generate text.")
        return None

    space_width = 75  # Horizontal space between words - Adjusted for normal spacing
    # Line spacing should be based on the full character box height
    # This defines the vertical gap between the bottom of one line's character box
    # and the top of the next line's character box.
    line_spacing = int(full_char_box_height * 0.20) # Example: 20% of char box height as line gap, for closer lines

    # Create a space image that matches the overall character canvas height
    space_image = np.ones((full_char_box_height, space_width), dtype=np.uint8) * 255 

    lines = text.strip().split("\n")
    line_images = []
    max_line_overall_width = 0

    for line in lines:
        generated_images_in_line = []
        for char in line:
            if char == " ":
                generated_images_in_line.append(space_image)
            elif char in char_images and char_images[char] is not None and char_images[char].size > 0:
                generated_images_in_line.append(char_images[char])
            else:
                print(f"⚠️ Warning: No image found or invalid image for '{char}'")

        if generated_images_in_line:
            # All images are already padded to full_char_box_height in load_character_images
            line_image = np.hstack(generated_images_in_line)
            line_images.append(line_image)
            max_line_overall_width = max(max_line_overall_width, line_image.shape[1])

    # Ensure all lines have equal width and add vertical spacing between them
    spaced_lines = []
    for line_image in line_images:
        h, w = line_image.shape
        if w < max_line_overall_width:
            # Pad horizontally to make all lines the same width
            line_image = np.pad(line_image, ((0, 0), (0, max_line_overall_width - w)), mode="constant", constant_values=255)
        spaced_lines.append(line_image)
        # Add a white space row between lines
        spaced_lines.append(np.ones((line_spacing, max_line_overall_width), dtype=np.uint8) * 255)

    if not spaced_lines:
        print("❌ No valid characters found. Cannot generate text.")
        return None

    # Remove the last line spacing if it exists (avoids extra space at the bottom)
    if len(spaced_lines) > 0 and spaced_lines[-1].shape[0] == line_spacing:
        spaced_lines.pop()

    # Vertically stack all prepared line images
    output_image = np.vstack(spaced_lines)

    # Create a larger white canvas with padding around the generated text
    final_height, final_width = output_image.shape
    # Add 100 pixels padding on all sides (50px top/bottom, 50px left/right)
    large_canvas = np.ones((final_height + 100, final_width + 100), dtype=np.uint8) * 255

    # Center the generated text image on the larger canvas
    y_offset = (large_canvas.shape[0] - final_height) // 2
    x_offset = (large_canvas.shape[1] - final_width) // 2
    large_canvas[y_offset:y_offset + final_height, x_offset:x_offset + final_width] = output_image

    # Save the final output image
    cv2.imwrite(output_path, large_canvas)
    print(f"✅ Handwritten text generated: {output_path}")
    return output_path

# This block runs only if the script is executed directly (not imported)
if __name__ == "__main__":
    print("This script is primarily designed to be called by app.py.")
    print("If you run it directly, you must provide text, output_path, font_image_folder, and mapping_file_path.")
    # Example for direct testing (uncomment and replace with actual paths as needed)
    # Ensure you have a font extracted and mapped in 'extracted_fonts/test_font_manual'
    # test_text = "Hello World!\nThis is a test with descenders like g, j, p, q, y."
    # test_output_path = "generated_test_output.png"
    # test_font_folder = "extracted_fonts/test_font_manual" # Must match an existing font folder
    # test_mapping_file = os.path.join(test_font_folder, "character_mapping.json")
    #
    # if os.path.exists(test_font_folder) and os.path.exists(test_mapping_file):
    #     try:
    #         generate_text_image(test_text, test_output_path, test_font_folder, test_mapping_file)
    #     except ValueError as e:
    #         print(e)
    # else:
    #     print("Test font folder or mapping file not found. Please create and map a font first.")
