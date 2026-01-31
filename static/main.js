const blogContainer = document.getElementById("blogposts")
const error = document.getElementById("error");
const loading = document.getElementById("loading");
async function main() {
    loading.style.display = "block";
    const response = await fetch("/fetch_posts");
    if (response.ok) {
        const json = await response.json();
        for (let postData of json) {
            let post = document.createElement("article");
            post.classList.add("post");

            let title = document.createElement("h2")
            title.innerText = postData.title;

            let postContent = document.createElement("p");
            postContent.innerText = postData.post;
            
            post.appendChild(title);
            post.appendChild(postContent);
            blogContainer.appendChild(post);
        }
        loading.style.display = "none";
    } else {
        error.style.display = "block";
        error.innerText = "Error occured fetching posts.";
    }
    
}