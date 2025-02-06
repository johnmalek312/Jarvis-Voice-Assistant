import instaloader
import re
from typing import Annotated


from logger import app_logger as logging
from tool_registry import register_tool
L = instaloader.Instaloader()
L.context.max_connection_attempts = 1
download_folder = "instagram_downloads"

def login(username="", password="") -> instaloader.Instaloader | None:
    """Logs in to Instagram."""
    global L
    L = instaloader.Instaloader()
    if username and password:
        try:
            L.login(username, password)
            logging.info(f"Logged in as {username}")
            return L
        except instaloader.exceptions.BadCredentialsException:
            logging.info("Invalid username or password.")
            logging.info("Using guest session.")
            return L
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            logging.info("Two-factor authentication is required. Please log in manually.")
            logging.info("Using guest session.")
            return L
    else:
        logging.info("Username and password were not provided.")
        logging.info("Using guest session.")
        return L


def download_highlight(url, path: Annotated[str, "The directory path to save the downloaded highlights."] = download_folder):
    """
    Downloads an Instagram highlight.
    The highlight URL is expected to be in the format:
    https://www.instagram.com/stories/highlights/<highlight_id>/
    Since the username is not included in the URL, the user is prompted to input it.
    """
    highlight_match = re.search(r"/stories/highlights/([^/]+)/", url)
    if not highlight_match:
        logging.warning("Invalid highlight URL format.")
        return
    highlight_id = highlight_match.group(1)

    # Ask for the profile name owning the highlight.
    profile_name = input("Enter the profile username for this highlight: ").strip()
    try:
        profile = instaloader.Profile.from_username(L.context, profile_name)
    except instaloader.exceptions.ProfileNotExistsException:
        logging.warning(f"Profile {profile_name} does not exist.")
        return

    found = False
    for hl in profile.get_highlights():
        # hl.id might be numeric or alphanumeric; compare as strings.
        if str(hl.id) == highlight_id:
            L.download_highlight(hl, target=path)
            print(f"Highlight downloaded: {highlight_id} from profile {profile_name}")
            found = True
            break
    if not found:
        print("Highlight not found for the given profile.")

#@register_tool()
def download_post(url: Annotated[str, "The shortcode or url of the instagram post."], 
                 path: Annotated[str, "The directory path to save the downloaded post."] = download_folder) -> str:
    """Downloads an Instagram post given its shortcode."""
    if not "/p/" in url:
        return "Invalid post URL format."
    shortcode = url.split("/p/")[1].split("/")[0]
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    return "Post downloaded." if L.download_post(post, target=path) else "Post download failed."

#@register_tool()
def download_reel(url: Annotated[str, "The shortcode or url of the instagram reel."], 
                 path: Annotated[str, "The directory path to save the downloaded reels."] = download_folder) -> str:
    """Downloads an Instagram reel given its shortcode or url."""
    if "/reels/" in url:
        shortcode = url.split("/reels/")[1].split("/")[0]
    else:
        shortcode = url
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    return "Reel downloaded." if L.download_post(post, target=path) else "Reel download failed."

# TODO: Broken needs fixing
def download_story(url: Annotated[str, "The url of the instagram story."], 
                  path: Annotated[str, "The directory path to save the downloaded story."] = download_folder) -> str | None:
    """
    Downloads Instagram story content.
    If a specific story item (with media id) is provided in the URL, downloads that item.
    Otherwise, downloads all stories for the given profile.
    Expected formats:
      - Specific story: https://www.instagram.com/stories/<profile_name>/<story_id>/
      - All stories: https://www.instagram.com/stories/<profile_name>/
    """
    story_match = re.search(r"/stories/([^/]+)/(\d+)", url)
    if story_match:
        profile_name, story_id = story_match.groups()
        try:
            profile = instaloader.Profile.from_username(L.context, profile_name)
        except instaloader.exceptions.ProfileNotExistsException:
            return f"Profile {profile_name} does not exist."

        for story_item in profile.get_stories():
            if str(story_item.mediaid) == story_id:
                L.download_storyitem(story_item, target=path)
                return f"Story item downloaded from profile {profile_name}: {story_id}"
        print("Story item not found.")
    else:
        # If no specific story id is provided, download all stories for the profile.
        parts = url.split('/stories/')
        if len(parts) < 2:
            return "Invalid story URL format."
        profile_name = parts[1].split('/')[0]
        try:
            profile = instaloader.Profile.from_username(L.context, profile_name)
            L.download_storyitem(next(profile.get_stories()), target=path)
            return f"All stories downloaded for: {profile_name}"
        except instaloader.exceptions.ProfileNotExistsException:
            return f"Profile {profile_name} does not exist."

#@register_tool()
def download_profile(url: Annotated[str, "The profile url."], 
                    path: Annotated[str, "The directory path to save the downloaded profile."] = download_folder) -> str:
    """
    Downloads an Instagram profile.
    The URL is expected to be a profile URL, e.g., https://www.instagram.com/<profile_name>/.
    """
    profile_match = re.search(r"/([^/]+)/?$", url)
    if profile_match:
        profile_name = profile_match.group(1)
        profile = instaloader.Profile.from_username(L.context, profile_name)
        return "Downloaded profile picture" if L.download_title_pic(profile.profile_pic_url, path, 'profile_pic', profile) else "Profile picture download failed."
    return "Invalid profile URL format."

# TODO: make this cleaner
@register_tool()
def download_from_url(url: Annotated[str, "The url of instagram content to download."]) -> str:
    """
    Download Instagram content based on the provided URL.

    The function determines if the URL points to a post, reel, or profile and then dispatches
    to the corresponding download function.

    Args:
        url (str): The URL of the Instagram content to download.

    Returns:
        str: A message indicating whether the download was successful or describing any error encountered.
    """
    # Validate the URL.
    if not url:
        message = "Please provide a URL."
        logging.error(message)
        return message

    if "instagram.com" not in url:
        message = "Invalid Instagram URL format."
        logging.error(message)
        return message

    content_label = None  # Will hold the type of content we're processing.
    try:
        # Attempt to match posts, reels, or stories using a regular expression.
        match = re.search(r"/(p|reels|stories)/([^/]+)/", url)
        if match:
            content_type, shortcode = match.groups()
            if content_type == "p":
                result = download_post(shortcode, path=download_folder)
                return result
            elif content_type == "reels":
                result = download_reel(shortcode, path=download_folder)
                return result
            elif content_type == "stories":
                result = "Stories download is not supported yet."
                logging.error(result)
                return result
            return "Invalid content type."
        else:
            # If no shortcode pattern is found, assume the URL is for a profile.
            try:
                # Split the URL to isolate the profile.
                after_domain = url.split("instagram.com/", 1)[1]
                profile_segment = after_domain.split("/", 1)[0]
            except IndexError:
                message = "Could not extract profile information from URL."
                logging.error(message)
                return message

            if profile_segment:
                result = download_profile(url, path=download_folder)
                return result
            else:
                result = "Could not determine content type from the URL."
                logging.error(result)
                return result

    except Exception as e:
        error_label = content_label if content_label else "content"
        logging.error(f"Error downloading {error_label}: {e}")
        return f"Error downloading {error_label}: {e}"