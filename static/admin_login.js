const form = document.getElementById("login_form");
const error = document.getElementById("error");
form.addEventListener("submit", async (event)=> {
    event.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const response = await fetch("/login_check", {
        method: "post",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({
            "username": username,
            "password": password
        })
    });
    if (response.ok) {
        window.location.href = "/admin_panel";
    } else if (response.status == 401) {
        error.innerText = "Incorrect username or password.";
    } else {
        error.innerText = "Internal server error.";
    }
});