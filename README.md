📝 Handwriting Generator with Custom Fonts
This project is a web-based application that allows users to convert typed text into a handwritten-style image. What makes it unique is the ability for users to upload their own handwriting samples, extract individual characters, manually map them, and then use their personalized font to generate text.

✨ Features
Upload Handwritten Documents: Easily upload an image of your handwriting.

Automatic Character Extraction: The backend processes your uploaded image to automatically identify and extract individual characters.

Manual Character Mapping: A dedicated interface to manually assign extracted image snippets to their corresponding characters (e.g., associating char_abc.png with 'a'). This ensures accuracy for complex or unique characters, including handling of 'i' and 'j' dots.

Multi-Font Support: Organize and manage multiple custom handwriting fonts, allowing you to switch between different styles.

Handwritten Text Generation: Type any text, select your desired custom font, and generate a high-quality image of that text in your unique handwriting style.

Responsive Web Interface: A user-friendly web interface built with HTML, CSS, and JavaScript.

Improved Character Handling: Enhanced extraction logic for characters like 'i' and 'j' to ensure dots and bodies are treated as single characters.

Accurate Descender Placement: Correct rendering of descenders (e.g., 'g', 'j', 'p', 'q', 'y') to extend below the baseline for a natural handwritten look.

User-Friendly Font Naming: Assign custom, human-readable names to your uploaded fonts.

🚀 Technologies Used
Backend:

Flask: A lightweight Python web framework.

OpenCV (cv2): For image processing, character extraction, and text image generation.

NumPy: For numerical operations, especially with image arrays.

Frontend:

HTML5: Structure of the web pages.

CSS3: Styling and responsiveness.

JavaScript: Client-side logic for interactions and API calls.

📁 File Structure
.
├── backend/
│   ├── app.py                      # Flask application main file
│   ├── extract_letters.py          # Script for extracting characters from images
│   ├── generate_handwritten_text.py# Script for generating text images from characters
│   ├── requirements.txt            # Python dependencies
│   ├── uploads/                    # Directory for temporary storage of uploaded handwriting images
│   ├── output/                     # Directory for generated handwritten text images
│   └── extracted_fonts/            # Base directory for all extracted fonts
│       ├── font_uniqueid1/         # Subfolder for a specific font
│       │   ├── char_timestamp_id_1.png # Extracted character image
│       │   ├── char_timestamp_id_2.png
│       │   └── character_mapping.json # JSON mapping for this font (char: filename)
│       │   └── metadata.json       # Stores user-friendly font name
│       ├── font_uniqueid2/
│       │   └── ...
│       └── ...
├── frontend/
│   ├── index.html                  # Main page for font management (upload/select)
│   ├── map.html                    # Page for manual character mapping
│   ├── edit.html                   # Page for text editing and generation
│   ├── style.css                   # Global styles for the application
│   ├── index_script.js             # JavaScript for the index.html page
│   ├── map_script.js               # JavaScript for the map.html page
│   └── edit_script.js              # JavaScript for the edit.html page
└── README.md                       # This README file

⚙️ Setup Instructions
Follow these steps to get the project up and running on your local machine.

Prerequisites
Python 3.8+

pip (Python package installer)

Installation
Clone the repository:

git clone <repository-url>
cd <repository-name>/backend

Create a virtual environment (recommended):

python -m venv venv

Activate the virtual environment:

On Windows:

.\venv\Scripts\activate

On macOS/Linux:

source venv/bin/activate

Install Python dependencies:

pip install -r requirements.txt

(Ensure requirements.txt contains Flask, opencv-python, numpy)

Run the Flask application:

python app.py

The application will typically run on http://127.0.0.1:5000/.

🚀 Usage Guide
Access the Application: Open your web browser and navigate to http://127.0.0.1:5000/.

Font Management (index.html):

Upload New Handwriting:

Click "Choose File" to select an image of your handwriting (e.g., a scanned page with individual characters).

Enter a descriptive name for your new font (e.g., "My Cursive," "Dad's Print").

Click "Upload & Extract New Font." The system will process the image, extract characters, and create a new font profile.

Select Existing Font:

Use the "Select a Font" dropdown to choose from previously uploaded and extracted handwriting styles.

The "Active Font" display will show which font is currently selected.

Character Mapping (map.html):

From the Font Management page, click "Go to Mapping for this Font" after selecting or uploading a font.

On this page, you will see individual extracted character images.

For each image, type the corresponding character in the input box. This is crucial for the generator to know which image represents which letter/number/symbol.

Click "Save Mapping" to save your associations for the active font.

Handwriting Editor (edit.html):

From the Font Management page, click "Go to Editor with this Font" after selecting or uploading a font.

On this page, type the text you want to convert into handwriting in the provided text area.

Click "Generate Handwriting." The system will use the active font's character mappings to create an image of your text.

The generated image will appear below the text area.

💡 Future Enhancements
User Authentication & Profiles: Allow multiple users to have their own fonts and documents.

Full Document Editor: Implement a rich text editor-like interface on the frontend that dynamically renders characters as images as the user types, allowing for real-time preview and more complex layout control.

Advanced Character Segmentation: Utilize more sophisticated image processing techniques or even machine learning to improve automatic character extraction and reduce the need for manual mapping, especially for connected cursive.

Font Management UI: Add options to rename, delete, or download font profiles.

Styling Options: Allow users to adjust line spacing, character spacing (kerning), and "ink" color.

Export Formats: Provide options to export generated handwriting as PDF or other image formats.

Error Handling & Feedback: More robust error messages and loading indicators for a smoother user experience.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details (you would create this file in your root directory).

🙏 Acknowledgements
Built with Flask, OpenCV, and NumPy.

Inspired by the need for personalized digital handwriting.
