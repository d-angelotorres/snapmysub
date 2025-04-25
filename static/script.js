// script.js

document.addEventListener("DOMContentLoaded", function () {
  const button = document.getElementById("fetchBtn");
  const input = document.getElementById("subredditInput");
  const avatarImg = document.getElementById("avatar");
  const bannerImg = document.getElementById("banner");
  const errorDiv = document.getElementById("error");
  const loader = document.getElementById("loader");

  async function fetchSubredditImages() {
    const inputValue = input.value.trim();

    // Clear previous results
    avatarImg.style.display = "none";
    bannerImg.style.display = "none";
    errorDiv.textContent = "";

    if (!inputValue) {
      errorDiv.textContent = "Please enter a subreddit.";
      return;
    }

    // Extract subreddit name
    let subreddit = inputValue;
    if (inputValue.includes("/r/")) {
      subreddit = inputValue.split("/r/")[1].split("/")[0];
    }

    loader.style.display = "block";

    try {
      const response = await fetch("/get_subreddit_data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subreddit })
      });

      const result = await response.json();
      loader.style.display = "none";

      if (result.error) {
        errorDiv.textContent = result.error;
        return;
      }

      if (result.avatar) {
        avatarImg.src = result.avatar;
        avatarImg.style.display = "block";
      }

      if (result.banner) {
        bannerImg.src = result.banner;
        bannerImg.style.display = "block";
      }
    } catch (err) {
      loader.style.display = "none";
      errorDiv.textContent = "Something went wrong. Please try again.";
    }
  }

  button.addEventListener("click", fetchSubredditImages);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      fetchSubredditImages();
    }
  });
});

