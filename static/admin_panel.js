async function isAllowed() {
    try {
    const clientId = localStorage.getItem("clientId");
    const signature = localStorage.getItem("signature");
    // i'm a masochist so i'm dealing with undefined and null here. be careful.
    const response = await fetch("/verify_signature", {
        method: "POST",
        body: JSON.stringify({
            clientId: clientId,
            signature: signature
        })
    });
    if (response.ok) {
        const data = await response.json();
        if (!data.result) { // result will be boolean
            alert("You don't belong here.")
            document.write("Get out.")
        }
    }
    } catch (err) {
        alert(err);
        document.write(err);
    }   
}

// excessive
document.addEventListener("DOMContentLoaded", async () => {
    await isAllowed()
});

setInterval(async () => {
    await isAllowed();
}, 10000)

// normal code begins here

const form = document.getElementById("postForm");

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await fetch("/adminPostPlace", {
        method: "POST",
        body: JSON.stringify({
            content: document.getElementById("content"),
            clientId: localStorage.getItem("clientId"),
            signature: localStorage.getItem("signature")
        })
    });
});

