document.getElementById('emailForm').addEventListener('submit', async function(e) {
  e.preventDefault();

  const email = document.getElementById('email').value;
  const message = document.getElementById('message').value;
  const sendDate = document.getElementById('sendDate').value;

  console.log("⏳ Submitting form...", email, sendDate);

  const res = await fetch('/api/send-later', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email,
      message,
      send_date: sendDate
    })
  });

  const data = await res.json();
  document.getElementById('response').innerText = data.status;

  console.log("✅ API responded:", data);
});
