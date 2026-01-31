const form = document.getElementById("posting_form");
let submitted = false;
form.addEventListener("submit", async (e) => {
    if (!submitted) {
        submitted = false;
        e.preventDefault();
        const title = document.getElementById("title");
        const post = document.getElementById("post");

        const response = await fetch("/create_post", {
            method: "post",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
            credentials: "include",
            body: JSON.stringify({
                "title": title.value,
                "post": post.value
        })
        });
        if (response.status = 429) {
            alert("You've been rate limited. Try uploading in the next 1 minute.");
            submitted = false;
        } else if (response.ok) {
            document.getElementById("success").innerText = "Post uploaded!";
            submitted = true;
        } else {
            alert("An error has occured in the server.");
            submitted = true;
        }
    } else {
        alert("Stop spamming!");
    }
});

