from flask import Flask, request, jsonify, send_from_directory, render_template, session
import os
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
def get_active_font():
    font_id = get_active_font_id()
    if font_id:
        return jsonify({"success": True, "active_font_id": font_id})
    return jsonify({"success": False, "error": "No active font set."})


@app.route("/get_fonts", methods=["GET"])
def get_fonts():
    fonts = []
    for font_dir in os.listdir(EXTRACTED_FONTS_BASE_FOLDER):
        full_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, font_dir)
        if os.path.isdir(full_path):
            # You might want to store a more user-friendly name, e.g., in a meta.json in the font folder
            fonts.append({"id": font_dir, "name": font_dir})
    return jsonify({"success": True, "fonts": fonts})

@app.route("/set_active_font", methods=["POST"])
def set_active_font_route():
    data = request.json
    font_id = data.get("font_id")
    
    font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, font_id)
    if os.path.isdir(font_path):
        set_active_font_id(font_id)
        return jsonify({"success": True, "message": f"Active font set to {font_id}"})
    return jsonify({"success": False, "error": "Font not found."})

@app.route("/generate", methods=["POST"])
def generate():
    user_text = request.json.get("text", "").strip()

    if not user_text:
        return jsonify({"success": False, "error": "No text provided"})

    current_font_id = get_active_font_id()
    if not current_font_id:
        return jsonify({"success": False, "error": "No active font selected. Please go to Font Management to select a font."})

    current_font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, current_font_id)
    current_mapping_file = os.path.join(current_font_path, "character_mapping.json")

    if not os.path.exists(current_mapping_file):
        return jsonify({"success": False, "error": f"Character mapping not found for active font: {current_font_id}"})

    output_path = os.path.join(OUTPUT_FOLDER, "generated_text.png")
    generate_text_image(user_text, output_path, current_font_path, current_mapping_file)

    return jsonify({"success": True, "image_url": "/output/generated_text.png"})

@app.route("/output/<filename>")
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route("/upload_handwriting", methods=["POST"])
def upload_handwriting():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"})
    if file:
        font_id = f"font_{int(uuid.uuid4())}_{file.filename.split('.')[0][:10]}"
        new_font_folder_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, font_id)
        os.makedirs(new_font_folder_path, exist_ok=True)

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        try:
            extracted_filenames = extract_characters_from_image(filepath, new_font_folder_path)
            set_active_font_id(font_id) # Set this newly uploaded font as the active one
            return jsonify({"success": True, "message": f"File uploaded and characters extracted into font '{font_id}'.", "font_id": font_id, "extracted_files": extracted_filenames})
        except Exception as e:
            return jsonify({"success": False, "error": f"Error during character extraction: {str(e)}"})

@app.route("/get_extracted_chars", methods=["GET"])
def get_extracted_chars():
    current_font_id = get_active_font_id()
    if not current_font_id:
        return jsonify({"success": False, "error": "No active font selected to display characters."})

    current_font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, current_font_id)
    mapping_file = os.path.join(current_font_path, "character_mapping.json")
    
    current_char_to_filename_map = {}
    if os.path.exists(mapping_file):
        with open(mapping_file, "r") as f:
            current_char_to_filename_map = json.load(f)
    
    filename_to_char_map = {v: k for k, v in current_char_to_filename_map.items()}

    extracted_files_info = []
    # Iterate through all PNG files in the active font's directory
    for filename in sorted(os.listdir(current_font_path)):
        if filename.endswith(".png"): # Exclude character_mapping.json itself (if present)
            mapped_char = filename_to_char_map.get(filename, "")
            
            extracted_files_info.append({
                "filename": filename,
                "image_url": f"/extracted_fonts/{current_font_id}/{filename}", # Correct path for frontend
                "mapped_char": mapped_char
            })
    
    extracted_files_info.sort(key=lambda x: (bool(x['mapped_char']), x['filename']))

    return jsonify({"success": True, "characters": extracted_files_info, "active_font": current_font_id})


@app.route("/extracted_fonts/<font_id>/<filename>")
def extracted_font_file(font_id, filename):
    font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, font_id)
    return send_from_directory(font_path, filename)


@app.route("/save_mapping", methods=["POST"])
def save_mapping():
    current_font_id = get_active_font_id()
    if not current_font_id:
        return jsonify({"success": False, "error": "No active font selected to save mapping for."})

    data = request.json
    frontend_new_mapping = data.get("mapping", {})
    
    current_font_path = os.path.join(EXTRACTED_FONTS_BASE_FOLDER, current_font_id)
    mapping_file = os.path.join(current_font_path, "character_mapping.json")

    existing_char_to_filename_map = {}
    if os.path.exists(mapping_file):
        with open(mapping_file, "r") as f:
            existing_char_to_filename_map = json.load(f)
    
    temp_filename_to_char_map = {v: k for k, v in existing_char_to_filename_map.items()}

    for filename, char_val in frontend_new_mapping.items():
        if char_val:
            temp_filename_to_char_map[filename] = char_val
        else:
            # If a character value is empty, remove that mapping for the filename
            # Find the character that was mapped to this filename previously
            char_to_remove = None
            for k, v in existing_char_to_filename_map.items():
                if v == filename:
                    char_to_remove = k
                    break
            if char_to_remove:
                del existing_char_to_filename_map[char_to_remove]
            if filename in temp_filename_to_char_map: # also remove from temp for current session
                del temp_filename_to_char_map[filename]

    # Reconstruct the final char:filename map from the updated temp_filename_to_char_map
    # Prioritize new/updated mappings from current submission
    final_char_to_filename_map = existing_char_to_filename_map.copy() # Start with existing, valid ones
    for filename, char_val in temp_filename_to_char_map.items():
        final_char_to_filename_map[char_val] = filename # This will overwrite if a char maps to multiple files (last one wins)

    with open(mapping_file, "w") as f:
        json.dump(final_char_to_filename_map, f, indent=4)
    
    return jsonify({"success": True, "message": "Character mapping saved successfully."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)