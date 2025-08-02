async function getPosts() {
    let posts = [];
    document.getElementById("loading").style.display = "block";
    try {
        const rawData = await fetch("/posts", { method: "GET" });
        const json = await rawData.json();

        json.forEach(post => {
            const content = post[1];
            posts.push(content);
        });

        const container = document.getElementById("blogposts");
        container.innerHTML = "";
        array.forEach(element => {
            
        });
        posts.forEach(content => {
            const postEl = document.createElement("div");
            postEl.className = "post";
            postEl.innerHTML = content;
            container.appendChild(postEl);
        });

    } catch (err) {
        console.log("Failed to fetch posts:", err);
        handleError(`Failed to retrieve posts or add them: ${err}`);
    } finally {
        document.getElementById("loading").style.display = "none";
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await getPosts();
});

setInterval(async () => {
    await getPosts();
}, 10000);