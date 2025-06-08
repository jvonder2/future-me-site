document.addEventListener("DOMContentLoaded", () => {
  const form    = document.getElementById("emailForm");
  const status  = document.getElementById("status");
  const preview = document.getElementById("preview");
  let previewData = null;  // will hold data for scheduling

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    status.textContent = "";
    preview.innerHTML   = "";

    const email     = document.getElementById("email").value.trim();
    const body      = document.getElementById("body").value.trim();
    const rawLocal  = document.getElementById("send_date").value.trim();
    const imageInput= document.getElementById("images");

    if (!email || !body || !rawLocal) {
      status.textContent = "Please fill in email, message, and send date.";
      return;
    }

    // Build formData for preview endpoint
    const fd = new FormData();
    fd.append("email", email);
    fd.append("body", body);
    fd.append("send_date", new Date(rawLocal).toISOString());
    fd.append("raw_local", rawLocal);  // send the raw local value for preview formatting
    for (let file of imageInput.files) {
      fd.append("images", file);
    }

    // Call preview
    try {
      const resp   = await fetch("/api/preview", { method: "POST", body: fd });
      const result = await resp.json();
      if (!resp.ok) {
        status.textContent = `Error: ${result.error || 'Unknown error'}`;
        return;
      }
      // Show preview
      preview.innerHTML = result.preview;
      // Hide form
      form.style.display = 'none';
      // Store preview data
      previewData = result.data;
      // Attach event handlers for buttons
      document.getElementById("confirmSend").addEventListener("click", sendScheduled);
      document.getElementById("editMessage").addEventListener("click", editScheduled);
    } catch (err) {
      console.error(err);
      status.textContent = "Network error. Check console.";
    }
  });

  async function sendScheduled() {
    if (!previewData) return;
    status.textContent = "Sending...";
    try {
      const resp = await fetch("/api/schedule", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(previewData)
      });
      const result = await resp.json();
      if (resp.ok) {
        status.textContent = `📬 Scheduled! (ID: ${result.id})`;
        preview.innerHTML = "";
      } else {
        status.textContent = `Error: ${result.error || 'Unknown error'}`;
      }
    } catch (err) {
      console.error(err);
      status.textContent = "Network error. Check console.";
    }
  }

  function editScheduled() {
    // clear preview and show form
    preview.innerHTML = "";
    form.style.display = 'block';
    status.textContent = "";
  }
});
