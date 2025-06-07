// frontend/script.js

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("emailForm");
  const status = document.getElementById("status");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    status.textContent = "";

    // Collect inputs
    const email = document.getElementById("email").value.trim();
    const body = document.getElementById("body").value.trim();
    const sendDate = document.getElementById("send_date").value.trim();
    const imageInput = document.getElementById("image");

    if (!email || !body || !sendDate) {
      status.textContent = "Please fill in email, message, and send date.";
      return;
    }

    // Build FormData
    const fd = new FormData();
    fd.append("email", email);
    fd.append("body", body);
    fd.append("send_date", sendDate);
    if (imageInput.files.length) {
      fd.append("image", imageInput.files[0]);
    }

    try {
      const resp = await fetch("/api/send-later", {
        method: "POST",
        body: fd,
      });
      const result = await resp.json();

      if (resp.ok) {
        status.textContent = `📬 Scheduled! (ID: ${result.id})`;
        form.reset();
      } else {
        status.textContent = `Error: ${result.error || "Unknown error"}`;
      }
    } catch (err) {
      console.error(err);
      status.textContent = "Network error. Check console.";
    }
  });
});
