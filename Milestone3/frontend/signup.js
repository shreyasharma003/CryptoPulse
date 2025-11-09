// =======================
// 📝 Signup Form Handling
// =======================
document.addEventListener("DOMContentLoaded", () => {
  const signupForm = document.getElementById("signupForm");

  if (signupForm) {
    signupForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const formData = new FormData(signupForm);
      const fullName = formData.get("fullName").trim();
      const email = formData.get("email");
      const password = formData.get("password");
      const confirmPassword = formData.get("confirmPassword");

      // Client-side validation
      if (!fullName) {
        showMessage("Please enter your full name", "error");
        return;
      }
      if (!validateEmail(email)) {
        showMessage("Please enter a valid email", "error");
        return;
      }
      if (!validatePassword(password)) {
        showMessage("Password must be at least 6 characters long", "error");
        return;
      }
      if (password !== confirmPassword) {
        showMessage("Passwords do not match", "error");
        return;
      }

      // Send data to Flask backend
      fetch("http://127.0.0.1:5000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fullName, email, password }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.error) {
            showMessage(data.error, "error");
          } else {
            showMessage("Account created successfully!", "success");
            setTimeout(() => {
              window.location.href = "login.html";
            }, 2000);
          }
        })
        .catch((err) => {
          console.error("Error:", err);
          showMessage("Something went wrong", "error");
        });
    });
  }
});
