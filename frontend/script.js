document.addEventListener("DOMContentLoaded", function () {
    const generateBtn = document.getElementById("generate-btn");
    const textInput = document.getElementById("text-input");
    const generatedImage = document.getElementById("generated-image");
    const outputContainer = document.querySelector(".output-container");

    const handwritingUpload = document.getElementById("handwriting-upload");
    const uploadBtn = document.getElementById("upload-btn");
    const mappingSection = document.getElementById("mapping-section");
    const characterDisplay = document.getElementById("character-display");
    const saveMappingBtn = document.getElementById("save-mapping-btn");

    const fontSelect = document.getElementById("font-select"); // New: Dropdown for font selection
    const currentFontDisplay = document.getElementById("current-font-display"); // New: To show active font

    if (!generateBtn || !textInput || !generatedImage || !outputContainer ||
        !handwritingUpload || !uploadBtn || !mappingSection || !characterDisplay || !saveMappingBtn ||
        !fontSelect || !currentFontDisplay) {
        console.error("One or more elements are missing!");
        return;
    }

    let activeFontId = null; // Stores the ID of the currently selected font

    // Function to load fonts into the dropdown
    function loadFonts() {
        fetch("/get_fonts")
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fontSelect.innerHTML = '<option value="">-- Select a Font --</option>'; // Clear and add default
                    data.fonts.forEach(font => {
                        const option = document.createElement("option");
                        option.value = font.id;
                        option.textContent = font.name; // For now, name is ID
                        fontSelect.appendChild(option);
                    });
                    // If an active font was previously set (e.g., after upload), select it
                    if (activeFontId) {
                        fontSelect.value = activeFontId;
                        currentFontDisplay.textContent = `Active Font: ${activeFontId}`;
                        loadCharactersForMapping(); // Load mapping for the newly selected active font
                    } else if (data.fonts.length > 0) {
                        // Optionally auto-select the first font if none is active
                        // fontSelect.value = data.fonts[0].id;
                        // activeFontId = data.fonts[0].id;
                        // currentFontDisplay.textContent = `Active Font: ${activeFontId}`;
                        // loadCharactersForMapping();
                    }
                } else {
                    console.error("Failed to load fonts:", data.error);
                }
            })
            .catch(error => console.error("Error loading fonts:", error));
    }

    // Event listener for font selection change
    fontSelect.addEventListener("change", function() {
        const selectedFontId = fontSelect.value;
        if (selectedFontId) {
            fetch("/set_active_font", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ font_id: selectedFontId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    activeFontId = selectedFontId;
                    currentFontDisplay.textContent = `Active Font: ${activeFontId}`;
                    console.log(data.message);
                    loadCharactersForMapping(); // Load characters for the newly active font
                } else {
                    console.error("Failed to set active font:", data.error);
                }
            })
            .catch(error => console.error("Error setting active font:", error));
        } else {
            activeFontId = null;
            currentFontDisplay.textContent = "Active Font: None Selected";
            characterDisplay.innerHTML = ''; // Clear mapping display
            mappingSection.style.display = "none";
        }
    });

    // Generate Handwriting Button Click
    generateBtn.addEventListener("click", function () {
        if (!activeFontId) {
            alert("Please select or upload a font first.");
            return;
        }

        const text = textInput.value.trim();
        console.log("Sending text:", text);

        if (!text) {
            console.error("No text entered!");
            return;
        }

        fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Server Response:", data);

            if (data.success && data.image_url) {
                const imageUrl = `${data.image_url}?t=${new Date().getTime()}`;
                generatedImage.src = imageUrl;
                generatedImage.style.display = "block";
                outputContainer.style.display = "flex";
            } else {
                console.error("Server error:", data.error || "Unknown error");
                alert("Error generating text: " + (data.error || "Unknown error"));
            }
        })
        .catch(error => {
            console.error("Fetch Error:", error);
            alert("Fetch Error: " + error.message);
        });
    });

    // Upload & Extract Button Click
    uploadBtn.addEventListener("click", function () {
        const file = handwritingUpload.files[0];
        if (!file) {
            alert("Please select a handwriting image to upload.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        fetch("/upload_handwriting", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                activeFontId = data.font_id; // Set the newly uploaded font as active
                loadFonts(); // Reload fonts to show the new one and select it
            } else {
                alert("Upload failed: " + data.error);
            }
        })
        .catch(error => console.error("Upload Error:", error));
    });

    // Function to load characters for manual mapping of the active font
    function loadCharactersForMapping() {
        if (!activeFontId) {
            characterDisplay.innerHTML = '<p>Select a font or upload new handwriting to see characters for mapping.</p>';
            mappingSection.style.display = "none";
            return;
        }

        fetch("/get_extracted_chars")
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    characterDisplay.innerHTML = ''; // Clear previous content
                    data.characters.forEach(charInfo => {
                        const charDiv = document.createElement("div");
                        charDiv.className = "char-item";
                        // Image URL now correctly points to the specific font folder
                        charDiv.innerHTML = `
                            <img src="${charInfo.image_url}" alt="${charInfo.filename}" style="width: 50px; height: 50px; border: 1px solid #ddd; margin: 5px;">
                            <input type="text" data-filename="${charInfo.filename}" value="${charInfo.mapped_char || ''}" maxlength="1" style="width: 30px; text-align: center;">
                        `;
                        characterDisplay.appendChild(charDiv);
                    });
                    mappingSection.style.display = "block"; // Show the mapping section
                    currentFontDisplay.textContent = `Active Font: ${data.active_font}`;
                } else {
                    console.error("Failed to load characters for mapping:", data.error);
                    characterDisplay.innerHTML = `<p>Error loading characters: ${data.error}. Please ensure an active font is selected and mapped.</p>`;
                    mappingSection.style.display = "none";
                }
            })
            .catch(error => console.error("Error loading characters:", error));
    }

    // Save Mapping Button Click
    saveMappingBtn.addEventListener("click", function () {
        if (!activeFontId) {
            alert("No active font selected to save mapping for.");
            return;
        }

        const inputs = characterDisplay.querySelectorAll("input[type='text']");
        const newMapping = {};
        inputs.forEach(input => {
            const filename = input.dataset.filename;
            const char = input.value.trim();
            if (char) {
                newMapping[filename] = char;
            }
        });

        fetch("/save_mapping", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mapping: newMapping })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                loadCharactersForMapping(); // Reload to reflect saved changes
            } else {
                alert("Failed to save mapping: " + data.error);
            }
        })
        .catch(error => console.error("Save Mapping Error:", error));
    });

    // Initial load of fonts when the page loads
    loadFonts();
});