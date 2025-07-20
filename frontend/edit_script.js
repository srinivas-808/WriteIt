document.addEventListener("DOMContentLoaded", function () {
    const generateBtn = document.getElementById("generate-btn");
    const textInput = document.getElementById("text-input");
    const generatedImage = document.getElementById("generated-image");
    const outputContainer = document.querySelector(".output-container");
    const currentFontDisplayEdit = document.getElementById("current-font-display-edit");

    let activeFontId = null;

    // Get the active font from the backend when the page loads
    fetch("/get_active_font")
        .then(response => response.json())
        .then(data => {
            if (data.success && data.active_font_id) {
                activeFontId = data.active_font_id;
                currentFontDisplayEdit.textContent = activeFontId;
            } else {
                currentFontDisplayEdit.textContent = "None Selected";
                alert("No active font selected. Please go to Font Management to select or upload one.");
                // Optionally redirect back to index if no font is active
                // window.location.href = '/';
            }
        })
        .catch(error => {
            console.error("Error getting active font:", error);
            currentFontDisplayEdit.textContent = "Error";
        });

    generateBtn.addEventListener("click", function () {
        if (!activeFontId) {
            alert("No active font selected. Please go back to Font Management to select one.");
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
});