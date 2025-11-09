document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const togglePassword = document.getElementById("togglePassword");
  const submitBtn = loginForm.querySelector("button");
  const messageBox = document.getElementById("messageBox");

  // Autofocus email field on page load
  emailInput.focus();

  // Toggle password visibility
  if (togglePassword) {
    togglePassword.addEventListener("click", () => {
      const isPassword = passwordInput.type === "password";
      passwordInput.type = isPassword ? "text" : "password";
      togglePassword.textContent = isPassword ? "🙈" : "👁";
    });
  }

  // Function to show messages
  function showMessage(message, type) {
    if (!messageBox) return;
    messageBox.textContent = message;
    messageBox.className = `message-box ${type} show`;

    // Auto-hide after 3 seconds
    setTimeout(() => {
      messageBox.classList.remove("show");
    }, 3000);
  }

  // Email validation function
  function validateEmail(email) {
    const re = /\S+@\S+\.\S+/;
    return re.test(email);
  }

  // Form submit
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    // Validation
    if (!validateEmail(email)) {
      showMessage("Please enter a valid email address", "error");
      return;
    }
    if (!password) {
      showMessage("Please enter your password", "error");
      return;
    }

    // Loading state
    submitBtn.disabled = true;
    submitBtn.textContent = "Logging in... ⏳";

    // Send credentials to Flask backend
    fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          showMessage(data.error, "error");
        } else {
          showMessage("Logged in successfully! Redirecting...", "success");
          setTimeout(() => {
            window.location.href = "dashboard.html";
          }, 1500);
        }
      })
      .catch((err) => {
        console.error("Login error:", err);
        showMessage("Something went wrong. Try again.", "error");
      })
      .finally(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = "Sign In";
      });
  });
});
