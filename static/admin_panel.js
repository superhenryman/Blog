const form = document.getElementById("posting_form");

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("title");
    const post = document.getElementById("post");

    const response = await fetch("/create_post", {
        method: "post",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        credentials: "include",
        body: JSON.stringify({
            "title": title,
            "post": post
        })
    });
    if (!response.ok) {
        alert("An error has occured creating a post!")
    }
});

