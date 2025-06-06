document.getElementById("emailForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const email = document.getElementById("email").value;
  const message = document.getElementById("message").value;
  const sendDate = document.getElementById("send_date").value;
  const image = document.getElementById("image").files[0]; // get uploaded image

  const formData = new FormData();
  formData.append("email", email);
  formData.append("message", message);
  formData.append("send_date", sendDate);
  if (image) {
    formData.append("image", image); // only append if an image is selected
  }

  try {
    const response = await fetch("/api/send-later", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    document.getElementById("status").textContent = result.status;
  } catch (error) {
    document.getElementById("status").textContent = "Error sending message.";
    console.error("Submission error:", error);
  }
});
