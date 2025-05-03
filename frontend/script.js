document.addEventListener("DOMContentLoaded", function () {
    const generateBtn = document.getElementById("generate-btn");
    const textInput = document.getElementById("text-input");
    const generatedImage = document.getElementById("generated-image");
    const outputContainer = document.querySelector(".output-container");

    if (!generateBtn || !textInput || !generatedImage || !outputContainer) {
        console.error("One or more elements are missing!");
        return;
    }

    generateBtn.addEventListener("click", function () {
        const text = textInput.value.trim();

        console.log("Sending text:", text); // Debugging log

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
                // Ensure the image is refreshed by adding a timestamp
                const imageUrl = `${data.image_url}?t=${new Date().getTime()}`;
                generatedImage.src = imageUrl;
                generatedImage.style.display = "block";
                outputContainer.style.display = "flex"; // Make the paper container visible
            } else {
                console.error("Server error:", data.error || "Unknown error");
            }
        })
        .catch(error => console.error("Fetch Error:", error));
    });
});
