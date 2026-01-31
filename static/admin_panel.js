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
        if (!response.ok) {
            alert("An error has occured creating a post!");
            submitted = true;
        } else {
            document.getElementById("success").innerText = "Post uploaded!";
            submitted = true;
        }
    } else {
        alert("Stop spamming!");
    }
});

