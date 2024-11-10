const authForm = document.getElementById("auth-form");
const authTitle = document.getElementById("auth-title");
const authSubmit = document.getElementById("auth-submit");

let isLoginMode = false;

authForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const name = document.getElementById("name").value;
    const gender = document.getElementById("gender").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const url = isLoginMode ? "/login" : "/signup";
    const data = isLoginMode ? { email, password } : { name, gender, email, password };

    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (response.redirected) {
        window.location.href = response.url;  // Redirect to menu.html after success
    } else {
        try {
            const error = await response.json();
            alert("Error: " + error.detail);
        } catch (e) {
            alert("An unexpected error occurred.");
        }
    }
});

function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    authTitle.textContent = isLoginMode ? "Log In" : "Sign Up";
    authSubmit.textContent = isLoginMode ? "Log In" : "Sign Up";
    document.getElementById("name").style.display = isLoginMode ? "none" : "block";
    document.getElementById("gender").style.display = isLoginMode ? "none" : "block";

    // Change placeholder to indicate it can be either username or email
    document.getElementById("email").placeholder = isLoginMode ? "Email or Username" : "Email";
}
