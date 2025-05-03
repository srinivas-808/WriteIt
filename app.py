from flask import Flask, request, jsonify, send_from_directory, render_template
import os
from generate_handwritten_text import generate_text_image

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")

# Output directory
OUTPUT_FOLDER = "output"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory("../frontend", filename)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    user_text = data.get("text", "").strip()

    if not user_text:
        return jsonify({"success": False, "error": "No text provided"})

    output_path = os.path.join(OUTPUT_FOLDER, "generated_text.png")
    generate_text_image(user_text, output_path)

    return jsonify({"success": True, "image_url": "/output/generated_text.png"})

@app.route("/output/<filename>")
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    # Make the Flask app accessible on the same network
    app.run(host="0.0.0.0", port=5000, debug=True)
