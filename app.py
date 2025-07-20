from flask import Flask, request, jsonify, send_from_directory, render_template, session
import os
import shutil 
import json
import uuid
from generate_handwritten_text import generate_text_image
from extract_letters import extract_characters_from_image

app = Flask(__name__, static_folder="frontend", template_folder="frontend")
# app.secret_key = 'your_secret_key_here' # Needed for Flask sessions, if you go that route

OUTPUT_FOLDER = "output"
UPLOAD_FOLDER = "uploads"
EXTRACTED_FONTS_BASE_FOLDER = "extracted_fonts"

# Using a global variable for active_font_folder_name.
# IMPORTANT: For multi-user environments, replace this with Flask sessions or a database lookup.
active_font_folder_name = None

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(EXTRACTED_FONTS_BASE_FOLDER):
    os.makedirs(EXTRACTED_FONTS_BASE_FOLDER)

# Helper to get/set active font (can be used by multiple routes)
def get_active_font_id():
    # In a real app, this would be session.get('active_font_id')
    return active_font_folder_name

def set_active_font_id(font_id):
    global active_font_folder_name
    active_font_folder_name = font_id
    # In a real app, this would be session['active_font_id'] = font_id

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory("frontend", filename)

# Main Font Management Page
@app.route("/")
def index():
    return render_template("index.html")

# New: Mapping Page
@app.route("/map")
def map_page():
    return render_template("map.html")

# New: Editing Page
@app.route("/edit")
def edit_page():
    return render_template("edit.html")

# Route to get the currently active font for frontend pages
@app.route("/get_active_font", methods=["GET"])
def get_active_font_route():
    if active_font_folder_name:
        # For simplicity without authentication, we won't load name from metadata.json here.
        # The frontend will display the folder ID as the name.
        # If you want the user-friendly name, you'd need to read metadata.json for the active_font_folder_name.
        # For this non-auth scenario, let's keep it simple.
        # To get the display name, you would do:
        font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, active_font_folder_name)
        metadata_path = os.path.join(font_path, "metadata.json")
        font_name = active_font_folder_name
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                    font_name = metadata.get("font_name", active_font_folder_name)
            except json.JSONDecodeError:
                pass
        return jsonify({"success": True, "active_font_id": active_font_folder_name, "active_font_name": font_name})
    return jsonify({"success": False, "error": "No active font set."})


@app.route("/get_fonts", methods=["GET"])
def get_fonts():
    fonts = []
    for font_dir in os.listdir(EXTRACTED_FONTS_BASE_FOLDER):
        full_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, font_dir)
        if os.path.isdir(full_path):
            metadata_path = os.path.join(full_path, "metadata.json")
            display_name = font_dir # Default to folder name
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                        display_name = metadata.get("font_name", font_dir)
                except json.JSONDecodeError:
                    print(f"⚠️ Warning: Could not read metadata.json for {font_dir}")
            fonts.append({"id": font_dir, "name": display_name})
    return jsonify({"success": True, "fonts": fonts})

@app.route("/set_active_font", methods=["POST"])
def set_active_font_route():
    global active_font_folder_name # Declare global to modify
    data = request.json
    font_id = data.get("font_id")
    
    font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, font_id)
    if os.path.isdir(font_path):
        active_font_folder_name = font_id # Set the global variable
        return jsonify({"success": True, "message": f"Active font set to {font_id}"})
    return jsonify({"success": False, "error": "Font not found."})

@app.route("/generate", methods=["POST"])
def generate():
    user_text = request.json.get("text", "").strip()

    if not user_text:
        return jsonify({"success": False, "error": "No text provided"}), 400

    if not active_font_folder_name:
        return jsonify({"success": False, "error": "No active font selected. Please select a font."}), 400

    current_font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, active_font_folder_name)
    current_mapping_file = os.path.join(current_font_path, "character_mapping.json")

    if not os.path.exists(current_mapping_file):
        return jsonify({"success": False, "error": f"Character mapping not found for active font: {active_font_folder_name}"}), 404

    output_path = os.path.join(OUTPUT_FOLDER, "generated_text.png")
    # Pass the font's image folder and mapping file path to generate_text_image
    generate_text_image(user_text, output_path, current_font_path, current_mapping_file)

    return jsonify({"success": True, "image_url": "/output/generated_text.png"})

@app.route("/delete_font", methods=["POST"])
def delete_font():
    data = request.json
    font_id_to_delete = data.get("font_id")

    if not font_id_to_delete:
        return jsonify({"success": False, "error": "Font ID is required for deletion."}), 400

    try:
        global active_font_folder_name
        # If the font to be deleted is currently active, clear the active selection
        if active_font_folder_name == font_id_to_delete:
            active_font_folder_name = None
            print(f"Disassociated active font {font_id_to_delete}")

        # Delete the corresponding local folder and its contents
        font_local_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, font_id_to_delete)
        if os.path.exists(font_local_path):
            shutil.rmtree(font_local_path)
            print(f"Deleted local font folder: {font_local_path}")
        else:
            print(f"Warning: Local font folder not found for {font_id_to_delete} at {font_local_path}")

        return jsonify({"success": True, "message": f"Font '{font_id_to_delete}' deleted successfully."})

    except Exception as e:
        print(f"Error deleting font '{font_id_to_delete}': {e}")
        return jsonify({"success": False, "error": f"Error deleting font: {str(e)}"}), 500

@app.route("/output/<filename>")
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route("/upload_handwriting", methods=["POST"])
def upload_handwriting():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    
    file = request.files['file']
    font_name = request.form.get("font_name", "").strip()

    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
    if not font_name:
        return jsonify({"success": False, "error": "Font name is required."}), 400

    try:
        font_id = str(uuid.uuid4()) # Unique ID for the font folder
        new_font_folder_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, font_id)
        os.makedirs(new_font_folder_path, exist_ok=True)

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        extracted_filenames = extract_characters_from_image(filepath, new_font_folder_path)
        
        # Save font metadata (name, uploaded filename) to local JSON
        metadata_path = os.path.join(new_font_folder_path, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump({"font_name": font_name, "uploaded_filename": file.filename}, f, indent=4)
        
        # Initialize an empty character_mapping.json in the new folder
        mapping_file = os.path.join(new_font_folder_path, "character_mapping.json")
        with open(mapping_file, "w") as f:
            json.dump({}, f, indent=4)

        global active_font_folder_name
        active_font_folder_name = font_id # Set the newly uploaded font as active

        return jsonify({"success": True, "message": f"Font '{font_name}' uploaded and characters extracted.", "font_id": font_id, "font_name": font_name})
    except Exception as e:
        print(f"Error during upload or character extraction: {e}")
        return jsonify({"success": False, "error": f"Error during upload or character extraction: {str(e)}"}), 500


@app.route("/get_extracted_chars", methods=["GET"])
def get_extracted_chars():
    if not active_font_folder_name:
        return jsonify({"success": False, "error": "No active font selected to display characters."}), 400

    current_font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, active_font_folder_name)
    mapping_file = os.path.join(current_font_path, "character_mapping.json")
    
    current_char_to_filename_map = {}
    if os.path.exists(mapping_file):
        with open(mapping_file, "r") as f:
            current_char_to_filename_map = json.load(f)
    
    filename_to_char_map = {v: k for k, v in current_char_to_filename_map.items()}

    extracted_files_info = []
    # Get list of extracted files from the font's local folder
    if os.path.exists(current_font_path):
        for filename in sorted(os.listdir(current_font_path)):
            if filename.endswith(".png"): # Exclude non-image files like character_mapping.json
                mapped_char = filename_to_char_map.get(filename, "")
                extracted_files_info.append({
                    "filename": filename,
                    "image_url": f"/extracted_fonts/{active_font_folder_name}/{filename}",
                    "mapped_char": mapped_char
                })
    
    extracted_files_info.sort(key=lambda x: (bool(x['mapped_char']), x['filename']))

    # Get font name from metadata.json
    font_name = active_font_folder_name
    metadata_path = os.path.join(current_font_path, "metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                font_name = metadata.get("font_name", active_font_folder_name)
        except json.JSONDecodeError:
            pass

    return jsonify({"success": True, "characters": extracted_files_info, "active_font": font_name})



@app.route("/extracted_fonts/<font_id>/<filename>")
def extracted_font_file(font_id, filename):
    font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, font_id)
    return send_from_directory(font_path, filename)


@app.route("/save_mapping", methods=["POST"])
def save_mapping():
    if not active_font_folder_name:
        return jsonify({"success": False, "error": "No active font selected to save mapping for."}), 400

    data = request.json
    frontend_new_mapping = data.get("mapping", {})
    
    if not isinstance(frontend_new_mapping, dict):
        return jsonify({"success": False, "error": "Invalid mapping data format."}), 400

    current_font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, active_font_folder_name)
    mapping_file = os.path.join(current_font_path, "character_mapping.json")

    existing_char_to_filename_map = {}
    if os.path.exists(mapping_file):
        with open(mapping_file, "r") as f:
            existing_char_to_filename_map = json.load(f)
    
    # Create a temporary filename -> char map for processing updates
    temp_filename_to_char_map = {v: k for k, v in existing_char_to_filename_map.items()}

    for filename, char_val in frontend_new_mapping.items():
        if char_val: # If a character is provided, update the mapping
            temp_filename_to_char_map[filename] = char_val
        else: # If character value is empty, remove any existing mapping for this filename
            if filename in temp_filename_to_char_map:
                del temp_filename_to_char_map[filename]

    # Reconstruct the final char:filename map from the updated temp_filename_to_char_map
    final_char_to_filename_map = {}
    for filename, char_val in temp_filename_to_char_map.items():
        # Handle cases where multiple files might be mapped to the same character
        # (last one wins for the key, typical dictionary behavior)
        final_char_to_filename_map[char_val] = filename

    with open(mapping_file, "w") as f:
        json.dump(final_char_to_filename_map, f, indent=4)
    
    return jsonify({"success": True, "message": "Character mapping saved successfully."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)