document.addEventListener("DOMContentLoaded", function () {
    const characterDisplay = document.getElementById("character-display");
    const saveMappingBtn = document.getElementById("save-mapping-btn");
    const currentFontDisplayMap = document.getElementById("current-font-display-map");

    let activeFontId = null;

    // Get the active font from the backend when the page loads
    fetch("/get_active_font")
        .then(response => response.json())
        .then(data => {
            if (data.success && data.active_font_id) {
                activeFontId = data.active_font_id;
                currentFontDisplayMap.textContent = activeFontId;
                loadCharactersForMapping();
            } else {
                currentFontDisplayMap.textContent = "None Selected";
                characterDisplay.innerHTML = '<p>No active font. Please go back to Font Management to select or upload one.</p>';
                saveMappingBtn.style.display = "none";
            }
        })
        .catch(error => {
            console.error("Error getting active font:", error);
            currentFontDisplayMap.textContent = "Error";
        });

    function loadCharactersForMapping() {
        if (!activeFontId) {
            characterDisplay.innerHTML = '<p>No active font to display characters for.</p>';
            return;
        }

        fetch("/get_extracted_chars") // This now implicitly uses the active font on the backend
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    characterDisplay.innerHTML = '';
                    if (data.characters.length === 0) {
                        characterDisplay.innerHTML = '<p>No characters found for this font. Please ensure extraction was successful.</p>';
                    } else {
                        data.characters.forEach(charInfo => {
                            const charDiv = document.createElement("div");
                            charDiv.className = "char-item";
                            charDiv.innerHTML = `
                                <img src="${charInfo.image_url}" alt="${charInfo.filename}" style="width: 50px; height: 50px; border: 1px solid #ddd; margin: 5px;">
                                <input type="text" data-filename="${charInfo.filename}" value="${charInfo.mapped_char || ''}" maxlength="1" style="width: 30px; text-align: center;">
                            `;
                            characterDisplay.appendChild(charDiv);
                        });
                    }
                } else {
                    console.error("Failed to load characters for mapping:", data.error);
                    characterDisplay.innerHTML = `<p>Error loading characters: ${data.error}.</p>`;
                }
            })
            .catch(error => console.error("Error loading characters:", error));
    }

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
                // Optionally reload characters to show they are now mapped
                loadCharactersForMapping(); 
            } else {
                alert("Failed to save mapping: " + data.error);
            }
        })
        .catch(error => console.error("Save Mapping Error:", error));
    });
});