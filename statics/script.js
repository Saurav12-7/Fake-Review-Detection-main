/**
 * Function to analyze reviews from a given product URL.
 * It sends the URL to the backend for review scraping and classification,
 * then displays the results on the webpage.
 */
function analyzeReviews() {
    const urlInput = document.getElementById("url"); // Get the entered product URL input element
    const url = urlInput.value; // Get the value
    const resultDiv = document.getElementById("result"); // Result display area
    const loadingDiv = document.getElementById("loading"); // Loading indicator

    // Validate if the user entered a URL
    if (!url) {
        resultDiv.innerHTML = "<p class='text-red-400 text-lg'>⚠ Please enter a valid Amazon product URL.</p>";
        return;
    }

    resultDiv.innerHTML = ""; // Clear previous results
    loadingDiv.style.display = "block"; // Show loading animation

    // Send the request to the backend API for review analysis
    // --- CHANGE MADE HERE: Changed URL to relative path for local Flask server ---
    fetch("/analyze", { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json()) // Convert the response to JSON
    .then(data => {
        loadingDiv.style.display = "none"; // Hide loading animation
        
        // Handle errors from the backend
        if (data.error) {
            resultDiv.innerHTML = `<p class='text-red-400 text-lg'>⚠ Error: ${data.error}</p>`;
        } else if (data.length === 0) {
            resultDiv.innerHTML = `<p class='text-yellow-400 text-lg'>ℹ️ No reviews found for this product, or unable to scrape.</p>`;
        }
        else {
            let html = "<h2 class='text-2xl font-bold text-green-300 mb-4'>Analysis Results</h2><div class='review-container'>";
            
            // Loop through the received reviews and generate HTML content
            data.forEach(review => {
                // Log the entire review object to the console for debugging
                console.log("Review data from backend:", review);

                // Make prediction comparison more robust (case-insensitive and trim whitespace)
                const predictionText = review.Prediction ? review.Prediction.trim().toLowerCase() : '';
                const predictionClass = (predictionText === "real (original)") ? "real" : "fake";

                html += `
                    <div class="review-card">
                        <p class="review-text"><strong>Review:</strong> ${review.Review}</p>
                        <p class="review-rating"><strong>Rating:</strong> ⭐ ${review.Rating}</p>
                        <p class="review-prediction ${predictionClass}">
                            <strong>Prediction:</strong> ${review.Prediction || 'N/A'}
                        </p>
                    </div>
                `;
            });
            
            html += "</div>";
            resultDiv.innerHTML = html; // Display the reviews and predictions
            urlInput.value = ""; // Clear the input field after successful analysis
        }
    })
    .catch(error => {
        loadingDiv.style.display = "none"; // Hide loading animation on error
        resultDiv.innerHTML = "<p class='text-red-400 text-lg'>⚠ An unexpected error occurred while processing your request. Please try again.</p>";
        console.error("Fetch error:", error);
    });
}

/**
 * Function to clear the input field and results area.
 */
function clearResults() {
    document.getElementById("url").value = ""; // Clear the URL input
    document.getElementById("result").innerHTML = ""; // Clear the results display
    document.getElementById("loading").style.display = "none"; // Hide loading animation
}
