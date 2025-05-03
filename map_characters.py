import cv2
import json
import os

# Path to extracted character images
image_folder = "extracted_letters"
mapping_file = "extracted_letters\character_mapping.json"

# Get all character image filenames in sorted order
image_files = sorted(os.listdir(image_folder))

# Initialize a dictionary to store character mappings
char_map = {}

print("🚀 Mapping characters to images. Enter the correct character for each image.")

# Loop through each extracted character image
for filename in image_files:
    image_path = os.path.join(image_folder, filename)
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        print(f"⚠️ Warning: {filename} could not be opened.")
        continue

    # Show the character image for user input
    cv2.imshow("Character", img)
    cv2.waitKey(200)  # Small delay to prevent freezing

    # Ask the user to manually input the correct character
    mapped_char = input(f"Enter the character for {filename}: ").strip()

    if mapped_char:  # Ensure input is not empty
        char_map[mapped_char] = filename  # Store in correct format

    cv2.destroyAllWindows()

# Save the updated mapping in correct format
with open(mapping_file, "w") as f:
    json.dump(char_map, f, indent=4)

print("\n✅ Character mapping completed! Data saved in", mapping_file)
