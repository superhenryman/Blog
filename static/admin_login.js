const form = document.getElementById("login_form");

form.addEventListener("submit", async (event)=> {
    event.preventDefault();
    const username = document.getElementById("username");
    const password = document.getElementById("password");
    await fetch("/login_check", {
        method: "post",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({
            "username": username,
            "password": password
        })
    });
});