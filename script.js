const promptBox = document.getElementById("prompt");
const count = document.getElementById("charCount");
const generateBtn = document.getElementById("generateBtn");
const statusText = document.getElementById("status");
const preview = document.getElementById("preview");
const emptyState = document.getElementById("emptyState");
const downloadBtn = document.getElementById("downloadBtn");
const refreshBtn = document.getElementById("refreshBtn");
let generatedHTML = "";

promptBox.addEventListener("input", () => {
  count.textContent = `${promptBox.value.length} / 1200`;
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    promptBox.value = button.dataset.prompt || "";
    promptBox.dispatchEvent(new Event("input"));
    promptBox.focus();
  });
});

function setStatus(message, kind = "info") {
  statusText.textContent = message;
  statusText.dataset.kind = kind;
}

function setPreview(html) {
  generatedHTML = html;
  preview.srcdoc = html;
  preview.style.display = "block";
  emptyState.hidden = true;
  downloadBtn.disabled = false;
}

generateBtn.addEventListener("click", async () => {
  const prompt = promptBox.value.trim();
  if (!prompt) {
    setStatus("Please describe the website you want to create first.", "error");
    promptBox.focus();
    return;
  }

  generateBtn.disabled = true;
  generateBtn.classList.add("is-loading");
  generateBtn.querySelector(".btn-label").textContent = "Creating your website…";
  setStatus("Sending your brief to Gemini. This may take a moment.", "info");

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        site_type: document.getElementById("siteType").value,
        theme: document.getElementById("theme").value
      })
    });

    let data;
    try {
      data = await response.json();
    } catch {
      throw new Error(`The server returned an unexpected response (HTTP ${response.status}). Check that Flask is running.`);
    }

    if (!response.ok) {
      const error = new Error(data.error || `Generation failed (HTTP ${response.status}).`);
      error.status = response.status;
      throw error;
    }
    if (!data.html) throw new Error("The AI returned no HTML. Please try again.");

    setPreview(data.html);
    setStatus("Website generated successfully. Preview it or download the HTML.", "success");
  } catch (error) {
    if (error.name === "TypeError" && error.message.includes("fetch")) {
      setStatus("Cannot reach the backend. In VS Code, run: python app.py", "error");
    } else {
      setStatus(error.message || "Something went wrong. Please try again.", "error");
    }
  } finally {
    generateBtn.disabled = false;
    generateBtn.classList.remove("is-loading");
    generateBtn.querySelector(".btn-label").textContent = "Generate website";
  }
});

downloadBtn.addEventListener("click", () => {
  if (!generatedHTML) return;
  const blob = new Blob([generatedHTML], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "webgenius-generated-website.html";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
});

refreshBtn.addEventListener("click", () => {
  if (generatedHTML) {
    preview.srcdoc = generatedHTML;
    setStatus("Preview refreshed.", "success");
  } else {
    setStatus("Generate a website first, then you can refresh the preview.", "info");
  }
});

fetch("/api/health")
  .then((response) => response.json())
  .then((health) => {
    if (!health.api_key_configured) {
      setStatus("Setup needed: add your Gemini API key to .env, then restart the server.", "error");
    }
  })
  .catch(() => setStatus("Backend not connected. Start it with: python app.py", "error"));
