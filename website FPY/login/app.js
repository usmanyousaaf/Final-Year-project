const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener('click', () => {
  container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener('click', () => {
  container.classList.remove("sign-up-mode");
});

// Handle Sign-In Form Submission
document.querySelector('.sign-in-form').addEventListener('submit', function (e) {
  e.preventDefault();

  const username = this.querySelector('input[type="text"]').value;
  const password = this.querySelector('input[type="password"]').value;

  fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Login successful!');
    } else {
      alert('Login failed: ' + data.error);
    }
  });
});

// Handle Sign-Up Form Submission
document.querySelector('.sign-up-form').addEventListener('submit', function (e) {
  e.preventDefault();

  const username = this.querySelector('input[type="text"]').value;
  const email = this.querySelector('input[type="email"]').value;
  const password = this.querySelector('input[type="password"]').value;

  fetch('/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Sign up successful!');
      container.classList.remove("sign-up-mode"); // Switch to sign-in
    } else {
      alert('Sign up failed: ' + data.error);
    }
  });
});