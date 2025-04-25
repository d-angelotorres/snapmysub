from flask import Flask, render_template, request, jsonify
import requests
import re  # We'll use regex to help with removing the query parameters

app = Flask(__name__)

# Function to clean the URL and remove anything after the image extension (e.g., ?width=100)
def clean_image_url(url):
    if not url:
        return None
    # Use regex to remove anything after .jpg, .png, .gif, etc.
    url = re.sub(r"(\.jpg|\.jpeg|\.png|\.gif)(\?.*)?$", r"\1", url)
    return url

# Function to filter out invalid or placeholder images
def is_valid_image(url):
    if not url:
        return False
    lowered = url.lower()
    # Filter out common Reddit placeholder patterns
    return not (
        "default" in lowered or
        "styles.redditmedia.com" in lowered and "re0s" in lowered or
        "1x1" in lowered or
        "pixel" in lowered
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_subreddit_data", methods=["POST"])
def get_subreddit_data():
    data = request.get_json()
    subreddit_input = data.get("subreddit", "").strip()

    if not subreddit_input:
        return jsonify({"error": "No subreddit provided"}), 400

    # Strip full URLs down to just subreddit name if needed
    if subreddit_input.startswith("http"):
        try:
            parts = subreddit_input.split("/")
            idx = parts.index("r")
            subreddit = parts[idx + 1]
        except (ValueError, IndexError):
            return jsonify({"error": "Invalid subreddit URL"}), 400
    else:
        subreddit = subreddit_input

    url = f"https://www.reddit.com/r/{subreddit}/about.json"

    # Modify the User-Agent and add some additional headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return jsonify({"error": "Subreddit not found"}), 404

        info = res.json()["data"]

        # Check both possible image sources for avatar
        avatar = info.get("icon_img")
        if not avatar:
            avatar = info.get("community_icon")
        
        # Check both possible image sources for banner
        banner = info.get("banner_background_image")
        if not banner:
            banner = info.get("banner_img")

        # Clean URLs to strip out query parameters
        avatar = clean_image_url(avatar) if is_valid_image(avatar) else None
        banner = clean_image_url(banner) if is_valid_image(banner) else None

        # If no valid avatar/banner, provide defaults
        if not avatar:
            avatar = "https://www.redditstatic.com/avatars/defaults/v2/avatar_default_1.png"  # Default icon
        if not banner:
            banner = "https://www.redditstatic.com/avatars/defaults/v2/banner_default_1.png"  # Default banner

        return jsonify({
            "avatar": avatar,
            "banner": banner
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == "__main__":
    app.run(debug=True)


