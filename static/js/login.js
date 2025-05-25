const container = document.getElementById("container");
const registerBtn = document.getElementById("register");
const loginBtn = document.getElementById("login");

registerBtn.addEventListener("click", () => {
  container.classList.add("active");
});

loginBtn.addEventListener("click", () => {
  container.classList.remove("active");
});

const existingUsernames = ["user1", "user2", "admin"];
const localAccount = {
  email: "ro@gmail.com",
  password: "1234",
  userType: "admin",
};

document
  .getElementById("signupForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();
    let isValid = true;

    const username = document.getElementById("signupUsername").value.trim();
    const email = document.getElementById("signupEmail").value.trim();
    const password = document.getElementById("signupPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const userType = document.querySelector(
      '#signupForm input[name="role"]:checked'
    )?.value;

    const usernameError = document.getElementById("usernameError");
    const emailError = document.getElementById("emailError");
    const passwordError = document.getElementById("passwordError");
    const confirmPasswordError = document.getElementById(
      "confirmPasswordError"
    );

    usernameError.style.display = existingUsernames.includes(username)
      ? "block"
      : "none";
    emailError.style.display =
      !email.includes("@") || !email.split("@")[1] ? "block" : "none";
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,}$/;
    passwordError.style.display = !passwordRegex.test(password)
      ? "block"
      : "none";
    confirmPasswordError.style.display =
      password !== confirmPassword ? "block" : "none";

    isValid = !(
      usernameError.style.display === "block" ||
      emailError.style.display === "block" ||
      passwordError.style.display === "block" ||
      confirmPasswordError.style.display === "block" ||
      !userType
    );

    if (isValid) {
      existingUsernames.push(username);
      alert("Signup successful!");
      document.getElementById("signupForm").reset();
      loginBtn.click();
    }
  });

document
  .getElementById("signinForm")
  .addEventListener("submit", function (event) {
    const email = document.getElementById("signinEmail").value.trim();
    const password = document.getElementById("signinPassword").value;
    const userType = document.querySelector(
      '#signinForm input[name="role"]:checked'
    )?.value;
    const signinEmailError = document.getElementById("signinEmailError");
    const signinPasswordError = document.getElementById("signinPasswordError");

    signinEmailError.style.display = "none";
    signinPasswordError.style.display = "none";

    if (
      email === localAccount.email &&
      password === localAccount.password &&
      userType === localAccount.userType
    ) {
      alert("Login success! Redirecting...");
      // Let the form submission proceed to the Flask route
    } else {
      event.preventDefault();
      signinPasswordError.style.display = "block";
    }
  });
