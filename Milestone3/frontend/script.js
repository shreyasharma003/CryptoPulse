// =======================
// 🌙 Theme Toggle Functionality
// =======================
class ThemeManager {
  constructor() {
    this.themeToggle = document.getElementById("themeToggle");
    this.body = document.body;
    this.currentTheme = "dark";
    this.init();
  }

  init() {
    this.setTheme(this.currentTheme);
    if (this.themeToggle) {
      this.themeToggle.addEventListener("click", () => this.toggleTheme());
    }
    this.loadThemePreference();
  }

  toggleTheme() {
    this.currentTheme = this.currentTheme === "dark" ? "light" : "dark";
    this.setTheme(this.currentTheme);
    this.saveThemePreference();
  }

  setTheme(theme) {
    this.body.className = `${theme}-theme`;
    this.currentTheme = theme;
    const themeIcon = this.themeToggle?.querySelector(".theme-icon");
    if (themeIcon) {
      themeIcon.textContent = theme === "dark" ? "🌙" : "☀️";
    }
  }

  saveThemePreference() {
    localStorage.setItem("cryptopulse-theme", this.currentTheme);
  }

  loadThemePreference() {
    const savedTheme = localStorage.getItem("cryptopulse-theme");
    if (savedTheme && (savedTheme === "light" || savedTheme === "dark")) {
      this.setTheme(savedTheme);
    }
  }
}

// =======================
// 👤 Authentication Helper Functions
// =======================
class AuthManager {
  constructor() {
    this.users = JSON.parse(localStorage.getItem("cryptopulse-users")) || [];
    this.currentUser =
      JSON.parse(localStorage.getItem("cryptopulse-current-user")) || null;
  }

  register(userData) {
    const existingUser = this.users.find(
      (user) => user.email === userData.email
    );
    if (existingUser) {
      throw new Error("User already exists with this email");
    }
    const newUser = {
      id: Date.now().toString(),
      fullName: userData.fullName,
      email: userData.email,
      password: userData.password,
      createdAt: new Date().toISOString(),
    };
    this.users.push(newUser);
    this.saveUsers();
    return newUser;
  }

  login(email, password) {
    const user = this.users.find(
      (u) => u.email === email && u.password === password
    );
    if (!user) {
      throw new Error("Invalid email or password");
    }
    this.currentUser = user;
    this.saveCurrentUser();
    return user;
  }

  logout() {
    this.currentUser = null;
    localStorage.removeItem("cryptopulse-current-user");
  }

  isLoggedIn() {
    return this.currentUser !== null;
  }

  getCurrentUser() {
    return this.currentUser;
  }

  saveUsers() {
    localStorage.setItem("cryptopulse-users", JSON.stringify(this.users));
  }

  saveCurrentUser() {
    localStorage.setItem(
      "cryptopulse-current-user",
      JSON.stringify(this.currentUser)
    );
  }
}

// =======================
// 🔔 Utility Functions
// =======================
function showMessage(message, type = "info") {
  const messageEl = document.createElement("div");
  messageEl.className = `message message-${type}`;
  messageEl.textContent = message;

  Object.assign(messageEl.style, {
    position: "fixed",
    top: "20px",
    right: "20px",
    padding: "1rem 1.5rem",
    borderRadius: "0.5rem",
    color: "white",
    fontWeight: "600",
    zIndex: "9999",
    transform: "translateX(100%)",
    transition: "transform 0.3s ease",
  });

  switch (type) {
    case "success":
      messageEl.style.backgroundColor = "#10b981";
      break;
    case "error":
      messageEl.style.backgroundColor = "#ef4444";
      break;
    default:
      messageEl.style.backgroundColor = "#8b5cf6";
  }

  document.body.appendChild(messageEl);

  setTimeout(() => {
    messageEl.style.transform = "translateX(0)";
  }, 100);

  setTimeout(() => {
    messageEl.style.transform = "translateX(100%)";
    setTimeout(() => {
      document.body.removeChild(messageEl);
    }, 300);
  }, 3000);
}

function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function validatePassword(password) {
  return password.length >= 6;
}

// =======================
// 🔮 Prediction Functions
// =======================
async function getPrediction(symbol, mode, value) {
  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ symbol, mode, value }),
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await response.json();
    if (data.error) {
      showMessage(`Error: ${data.error}`, "error");
      return;
    }

    // Save prediction in localStorage for output.html
    localStorage.setItem("cryptopulse-last-prediction", JSON.stringify(data));

    // Redirect to output.html
    window.location.href = "output.html";
  } catch (err) {
    console.error("Prediction error:", err);
    showMessage("Failed to fetch prediction", "error");
  }
}

// =======================
// 🚀 Init
// =======================
document.addEventListener("DOMContentLoaded", () => {
  new ThemeManager();
  window.authManager = new AuthManager();

  const predictBtn = document.getElementById("predictBtn");
  if (predictBtn) {
    predictBtn.addEventListener("click", () => {
      const symbol = document.getElementById("symbol").value;
      const mode = document.querySelector("input[name='mode']:checked")?.value;
      const value = document.getElementById("duration").value;

      if (!symbol || !mode || !value) {
        showMessage("Please select symbol, mode, and duration", "error");
        return;
      }

      getPrediction(symbol, mode, parseInt(value));
    });
  }
});
