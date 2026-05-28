const storageKey = "smartserpent:lastPrediction";

function setStatus(element, message, type = "neutral") {
  if (!element) return;
  element.textContent = message;
  element.className = `status-card ${type}`;
}

function savePrediction(prediction) {
  localStorage.setItem(storageKey, JSON.stringify(prediction));
}

function loadPrediction() {
  const raw = localStorage.getItem(storageKey);
  return raw ? JSON.parse(raw) : null;
}

function getConfidenceLabel(confidence) {
  if (confidence >= 90) return "High confidence";
  if (confidence >= 75) return "Strong match";
  if (confidence >= 55) return "Moderate confidence";
  return "Needs careful review";
}

async function handlePredictionPage() {
  const form = document.getElementById("upload-form");
  if (!form) return;
  let currentPreviewUrl = null;

  const status = document.getElementById("status-message");
  const card = document.getElementById("prediction-card");
  const nameEl = document.getElementById("snake-name");
  const confidenceEl = document.getElementById("snake-confidence");
  const detailsButton = document.getElementById("details-button");
  const fileInput = document.getElementById("snake-image");
  const fileName = document.getElementById("file-name");
  const previewImage = document.getElementById("image-preview");
  const placeholder = document.getElementById("image-placeholder");
  const confidenceFill = document.getElementById("confidence-fill");
  const predictionLevel = document.getElementById("prediction-level");

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) {
      fileName.textContent = "No file selected";
      if (currentPreviewUrl) {
        URL.revokeObjectURL(currentPreviewUrl);
        currentPreviewUrl = null;
      }
      previewImage.classList.add("hidden");
      placeholder.classList.remove("hidden");
      return;
    }

    fileName.textContent = file.name;
    if (currentPreviewUrl) {
      URL.revokeObjectURL(currentPreviewUrl);
    }
    currentPreviewUrl = URL.createObjectURL(file);
    previewImage.src = currentPreviewUrl;
    previewImage.classList.remove("hidden");
    placeholder.classList.add("hidden");
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const file = fileInput.files[0];

    if (!file) {
      setStatus(status, "Please choose an image before uploading.", "error");
      return;
    }

    setStatus(status, "Running prediction on the uploaded image...", "neutral");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Prediction request failed.");
      }

      nameEl.textContent = data.snake_name;
      confidenceEl.textContent = `${data.confidence}%`;
      confidenceFill.style.width = `${Math.max(0, Math.min(100, data.confidence))}%`;
      predictionLevel.textContent = getConfidenceLabel(data.confidence);
      card.classList.remove("hidden");
      savePrediction({
        snake_name: data.snake_name,
        confidence: data.confidence,
      });
      setStatus(status, "Prediction completed successfully.", "success");
    } catch (error) {
      setStatus(status, error.message, "error");
      card.classList.add("hidden");
    }
  });

  detailsButton.addEventListener("click", () => {
    window.location.href = "/details";
  });
}

function renderList(elementId, items) {
  const element = document.getElementById(elementId);
  if (!element) return;
  element.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    element.appendChild(li);
  });
}

async function handleDetailsPage() {
  const loadButton = document.getElementById("load-details-button");
  if (!loadButton) return;

  const status = document.getElementById("details-status");
  const card = document.getElementById("details-card");
  const cachedPrediction = loadPrediction();

  if (cachedPrediction) {
    setStatus(
      status,
      `Ready to fetch details for ${cachedPrediction.snake_name}.`,
      "neutral"
    );
  }

  loadButton.addEventListener("click", async () => {
    const prediction = loadPrediction();
    if (!prediction) {
      setStatus(
        status,
        "No prediction found yet. Please upload an image on the prediction page first.",
        "error"
      );
      return;
    }

    setStatus(status, "Fetching Gemini species report...", "neutral");

    try {
      const response = await fetch("/api/details", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(prediction),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Details request failed.");
      }

      const details = data.details;
      document.getElementById("details-snake-name").textContent = data.snake_name;
      document.getElementById("details-confidence").textContent = `${data.confidence ?? "-"}%`;
      document.getElementById("canonical-name").textContent = details.canonical_name || "-";
      document.getElementById("scientific-name").textContent = details.scientific_name || "-";
      document.getElementById("habitat").textContent = details.habitat || "-";
      document.getElementById("venomous").textContent = details.venomous || "-";
      document.getElementById("venom-type").textContent = details.venom_type || "-";
      document.getElementById("emergency-priority").textContent = details.emergency_priority || "-";
      document.getElementById("confidence-note").textContent = details.confidence_note || "-";

      renderList("first-aid-list", details.first_aid || []);
      renderList("safety-list", details.safety_info || []);
      renderList("verify-sources-list", details.verify_sources || []);

      card.classList.remove("hidden");
      setStatus(status, "Detailed summary loaded successfully.", "success");
    } catch (error) {
      setStatus(status, error.message, "error");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  handlePredictionPage();
  handleDetailsPage();
});
