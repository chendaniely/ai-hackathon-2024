import instaloader

# Initialize Instaloader
L = instaloader.Instaloader()

# Replace 'REEL_URL' with the actual Reel URL or the post's shortcode
reel_url = "https://www.instagram.com/reel/C_-tH8cPbyO/"

shortcode = reel_url.split("/")[-2]  # Extracts the shortcode from the URL

# Download the Reel using its shortcode
post = instaloader.Post.from_shortcode(L.context, shortcode)
L.download_post(post, target="downloaded_reel")
