// frontend/index_script.js

// REMOVE Firebase imports and auth_utils import
// import { authenticatedFetch } from './auth_utils.js'; // REMOVE THIS LINE

document.addEventListener("DOMContentLoaded", function () {
    const handwritingUpload = document.getElementById("handwriting-upload");
    const uploadBtn = document.getElementById("upload-btn");
    const fontSelect = document.getElementById("font-select");
    const currentFontDisplay = document.getElementById("current-font-display-index");
    const goToMapBtn = document.getElementById("go-to-map-btn");
    const goToEditBtn = document.getElementById("go-to-edit-btn");
    const newFontNameInput = document.getElementById("new-font-name");
    const deleteFontBtn = document.getElementById("delete-font-btn");

    let activeFontId = null; // This will be updated by loadFonts and fontSelect change

    // No need for window.addEventListener('authReady') anymore
    loadFonts(); // Load fonts directly when DOM is ready

    function updateButtonVisibility() {
        if (fontSelect.value) { // If a font is selected
            goToMapBtn.style.display = "inline-block";
            goToEditBtn.style.display = "inline-block";
            deleteFontBtn.style.display = "inline-block"; // Show delete button
        } else {
            goToMapBtn.style.display = "none";
            goToEditBtn.style.display = "none";
            deleteFontBtn.style.display = "none"; // Hide delete button
        }
    }

    function loadFonts() {
        // Replace authenticatedFetch with standard fetch
        fetch("/get_fonts")
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fontSelect.innerHTML = '<option value="">-- Select a Font --</option>';
                    data.fonts.forEach(font => {
                        const option = document.createElement("option");
                        option.value = font.id;
                        option.textContent = font.name;
                        fontSelect.appendChild(option);
                    });
                    
                    // Replace authenticatedFetch with standard fetch
                    fetch("/get_active_font") // Get current active font
                        .then(resp => resp.json())
                        .then(activeFontData => {
                            if (activeFontData.success && activeFontData.active_font_id) {
                                activeFontId = activeFontData.active_font_id;
                                fontSelect.value = activeFontId;
                                currentFontDisplay.textContent = `Active Font: ${activeFontData.active_font_name}`;
                            } else {
                                activeFontId = null;
                                fontSelect.value = ""; // No active font selected
                                currentFontDisplay.textContent = "Active Font: None Selected";
                            }
                            updateButtonVisibility(); // Update button visibility after setting active font
                        })
                        .catch(error => {
                            console.error("Error fetching active font on load:", error);
                            currentFontDisplay.textContent = "Active Font: Error";
                            updateButtonVisibility();
                        });

                } else {
                    console.error("Failed to load fonts:", data.error);
                    currentFontDisplay.textContent = "Active Font: Error Loading";
                    updateButtonVisibility();
                }
            })
            .catch(error => {
                console.error("Fetch Error loading fonts:", error);
                updateButtonVisibility();
            });
    }

    fontSelect.addEventListener("change", function() {
        const selectedFontId = fontSelect.value;
        if (selectedFontId) {
            // Replace authenticatedFetch with standard fetch
            fetch("/set_active_font", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ font_id: selectedFontId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    activeFontId = selectedFontId;
                    const selectedOption = fontSelect.options[fontSelect.selectedIndex];
                    currentFontDisplay.textContent = `Active Font: ${selectedOption.textContent}`;
                    console.log(data.message);
                } else {
                    console.error("Failed to set active font:", data.error);
                    alert("Failed to set active font: " + data.error);
                    fontSelect.value = activeFontId;
                }
                updateButtonVisibility();
            })
            .catch(error => {
                console.error("Fetch Error setting active font:", error);
                alert("Fetch Error: " + error.message);
                fontSelect.value = activeFontId;
                updateButtonVisibility();
            });
        } else {
            activeFontId = null;
            currentFontDisplay.textContent = "Active Font: None Selected";
            updateButtonVisibility();
        }
    });

    uploadBtn.addEventListener("click", function () {
        const file = handwritingUpload.files[0];
        const fontName = newFontNameInput.value.trim();

        if (!file) {
            alert("Please select a handwriting image to upload.");
            return;
        }
        if (!fontName) {
            alert("Please enter a name for your new font.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("font_name", fontName);

        // Replace authenticatedFetch with standard fetch
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
                newFontNameInput.value = '';
            } else {
                alert("Upload failed: " + data.error);
            }
            updateButtonVisibility();
        })
        .catch(error => {
            console.error("Upload Error:", error);
            updateButtonVisibility();
        });
    });

    // NEW: Delete Font Button Click (Logic remains largely the same)
    deleteFontBtn.addEventListener("click", function() {
        const selectedFontId = fontSelect.value;
        const selectedFontName = fontSelect.options[fontSelect.selectedIndex].textContent;

        if (!selectedFontId) {
            alert("Please select a font to delete.");
            return;
        }

        if (confirm(`Are you sure you want to delete the font "${selectedFontName}"? This action cannot be undone.`)) {
            // Replace authenticatedFetch with standard fetch
            fetch("/delete_font", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ font_id: selectedFontId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    loadFonts(); // Reload fonts list
                } else {
                    alert("Failed to delete font: " + data.error);
                }
            })
            .catch(error => console.error("Delete Font Error:", error));
        }
    });

    goToMapBtn.addEventListener("click", function() {
        const selectedFontId = fontSelect.value;
        if (selectedFontId) {
            window.location.href = `/map`;
        } else {
            alert("Please select a font first.");
        }
    });

    goToEditBtn.addEventListener("click", function() {
        const selectedFontId = fontSelect.value;
        if (selectedFontId) {
            window.location.href = `/edit`;
        } else {
            alert("Please select a font first.");
        }
    });
});