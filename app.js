const form = document.querySelector("#loan-form");
const button = document.querySelector("#submit-btn");
const content = document.querySelector("#result-content");
const card = document.querySelector("#result-card");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const payload = Object.fromEntries(new FormData(form).entries());
  for (const [key, value] of Object.entries(payload)) {
    if (key !== "education" && key !== "self_employed") payload[key] = Number(value);
  }
  button.disabled = true;
  button.querySelector("span:first-child").textContent = "Generating…";
  card.setAttribute("aria-busy", "true");
  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Unable to generate the estimate.");
    const approved = result.decision === "Approved";
    content.innerHTML = `
      <div class="result-ready" aria-live="polite">
        <div class="decision-label">PREDICTED OUTCOME</div>
        <h2 class="decision-title">${approved ? "Approval" : "Rejection"} estimate</h2>
        <div class="probability">${result.approval_probability}<span>% <span style="font:400 10px 'DM Sans',sans-serif;letter-spacing:0">approval likelihood</span></span></div>
        <div class="meter" role="img" aria-label="${result.approval_probability}% approval likelihood"><span style="width:${result.approval_probability}%"></span></div>
        <p>${approved ? "The model found patterns associated with approved applications." : "The model found fewer patterns associated with approved applications."}</p>
        <div class="result-foot"><span>MODEL OUTCOME</span><strong>${result.decision}</strong></div>
        <p style="font-size:8px;margin-top:9px">${result.disclaimer}</p>
      </div>`;
  } catch (error) {
    content.innerHTML = `<div class="result-ready" role="alert"><div class="decision-label">ESTIMATE UNAVAILABLE</div><h2 class="decision-title">Check your details</h2><div class="error-message">${error.message.replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}</div><p>Review the fields and try again.</p></div>`;
  } finally {
    button.disabled = false;
    button.querySelector("span:first-child").textContent = "Generate estimate";
    card.removeAttribute("aria-busy");
  }
});
