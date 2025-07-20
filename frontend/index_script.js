document.addEventListener("DOMContentLoaded", function () {
    const handwritingUpload = document.getElementById("handwriting-upload");
    const uploadBtn = document.getElementById("upload-btn");
    const fontSelect = document.getElementById("font-select");
    const currentFontDisplay = document.getElementById("current-font-display-index");
    const goToMapBtn = document.getElementById("go-to-map-btn");
    const goToEditBtn = document.getElementById("go-to-edit-btn");
    const newFontNameInput = document.getElementById("new-font-name");

    let activeFontId = null;

    function loadFonts() {
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
                    // Try to re-select if an active font was known
                    fetch("/get_active_font") // New route to get current active font
                        .then(resp => resp.json())
                        .then(activeFontData => {
                            if (activeFontData.success && activeFontData.active_font_id) {
                                activeFontId = activeFontData.active_font_id;
                                fontSelect.value = activeFontId;
                                currentFontDisplay.textContent = `Active Font: ${activeFontId}`;
                                goToMapBtn.style.display = "inline-block";
                                goToEditBtn.style.display = "inline-block";
                            } else {
                                currentFontDisplay.textContent = "Active Font: None Selected";
                                goToMapBtn.style.display = "none";
                                goToEditBtn.style.display = "none";
                            }
                        });
                } else {
                    console.error("Failed to load fonts:", data.error);
                }
            })
            .catch(error => console.error("Error loading fonts:", error));
    }

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
                    goToMapBtn.style.display = "inline-block";
                    goToEditBtn.style.display = "inline-block";
                } else {
                    console.error("Failed to set active font:", data.error);
                    alert("Failed to set active font: " + data.error);
                }
            })
            .catch(error => console.error("Error setting active font:", error));
        } else {
            activeFontId = null;
            currentFontDisplay.textContent = "Active Font: None Selected";
            goToMapBtn.style.display = "none";
            goToEditBtn.style.display = "none";
        }
    });

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
                // No immediate redirection, user can choose map or edit
            } else {
                alert("Upload failed: " + data.error);
            }
        })
        .catch(error => console.error("Upload Error:", error));
    });

    goToMapBtn.addEventListener("click", function() {
        if (activeFontId) {
            window.location.href = `/map`; // Redirect to mapping page
        } else {
            alert("Please select a font first.");
        }
    });

    goToEditBtn.addEventListener("click", function() {
        if (activeFontId) {
            window.location.href = `/edit`; // Redirect to editing page
        } else {
            alert("Please select a font first.");
        }
    });

    loadFonts(); // Initial load
});