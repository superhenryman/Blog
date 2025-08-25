const form = document.getElementById("LoginForm")

function getClientId() {
    let clientId = localStorage.getItem("clientId");
    if (!clientId) {
        clientId = crypto.randomUUID();
        localStorage.setItem("clientId", clientId);
    }
    return clientId;
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const response = await fetch("/adminlogin", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: document.getElementById("username").value,
            password: document.getElementById("password").value,
            clientid: getClientId(),
        })
    });
    if (response.ok) {
        // THIS MEANS WE GOT IT BABY
        const data = await response.json();
        const signature = data.result;
        localStorage.setItem("signature", signature);
        window.location.href = "https://shmblog.up.railway.app/adminPostPlace";
    } else {
        const data = await response.json();
        const error = data.error;
        alert(`Error: ${error}`);
    }
});

