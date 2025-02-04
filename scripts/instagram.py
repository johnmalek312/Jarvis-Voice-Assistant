import instaloader
import re

from pydantic import Field
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


def download_highlight(url, path: str=Field(download_folder, description="The directory path to save the downloaded highlights.")):
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
def download_post(url: str = Field(description="The shortcode or url of the instagram post."), path: str=Field(download_folder, description="The directory path to save the downloaded post.")) -> bool:
    """Downloads an Instagram post given its shortcode."""
    if "/p/" in url:
        shortcode = url.split("/p/")[1].split("/")[0]
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    return L.download_post(post, target=path)

#@register_tool()
def download_reel(url: str = Field(description="The shortcode or url of the instagram reel."), path: str=Field(download_folder, description="The directory path to save the downloaded reels.")) -> bool:
    """Downloads an Instagram reel given its shortcode or url."""
    if "reel" in url:
        shortcode = url.split("/reel/")[1].split("/")[0]
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    return L.download_post(post, target=post.owner_username)

# TODO: Broken needs fixing
def download_story(url: str = Field(description="The url of the instagram story."), path: str=Field(download_folder, description="The directory path to save the downloaded story.")) -> bool:
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
            print(f"Profile {profile_name} does not exist.")
            return
        for story_item in profile.get_stories():
            if str(story_item.mediaid) == story_id:
                L.download_storyitem(story_item, target=path)
                print(f"Story item downloaded from profile {profile_name}: {story_id}")
                return
        print("Story item not found.")
    else:
        # If no specific story id is provided, download all stories for the profile.
        parts = url.split('/stories/')
        if len(parts) < 2:
            print("Invalid story URL format.")
            return
        profile_name = parts[1].split('/')[0]
        try:
            profile = instaloader.Profile.from_username(L.context, profile_name)
            L.download_storyitem(next(profile.get_stories()), target=path)
            print(f"All stories downloaded for: {profile_name}")
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"Profile {profile_name} does not exist.")

#@register_tool()
def download_profile(url: str = Field(description="The profile url."), path: str=Field(download_folder, description="The directory path to save the downloaded profile.")) -> bool:
    """
    Downloads an Instagram profile.
    The URL is expected to be a profile URL, e.g., https://www.instagram.com/<profile_name>/.
    """
    profile_match = re.search(r"/([^/]+)/?$", url)
    if profile_match:
        profile_name = profile_match.group(1)
        profile = instaloader.Profile.from_username(L.context, profile_name)
        return L.download_title_pic(profile.profile_pic_url, path, 'profile_pic', profile)
    return False

# TODO: make this cleaner
@register_tool()
def download_from_url(url = Field(description="The url of instagram content to download.")) -> str:
    """
    Determines the type of Instagram content from the URL and dispatches to the appropriate download function.
    Supports posts, reels, and profile downloads.
    """
    if not url:
        print("Please provide a URL.")
        return "Please provide a URL."

    if url.find('instagram.com') == -1:
        print("Invalid Instagram URL format.")
        return "Invalid Instagram URL format."


    # Check for highlights first.
    # if "/stories/highlights/" in url:
    #     download_highlight(url)
    #     return

    # Check for posts, reels, or stories by looking for specific URL patterns.
    shortcode_match = re.search(r"/(p|reel|stories)/([^/]+)/", url)

    if shortcode_match:
        content_type, shortcode = shortcode_match.groups()
        if content_type == "p":
            result = (download_post(shortcode, path=download_folder), "post")
        elif content_type == "reel":
            result = (download_reel(shortcode, path=download_folder), "reel")
    else:
        try:
            after_domain = url.split("instagram.com/")[1]
            profile_part = after_domain.split("/")[0]
            if profile_part:
                download_profile(url, path=download_folder)
                result = (True, "profile picture")
        except Exception as e:
            logging.error(f"Error downloading profile picture: {e}")
            return f"Error downloading profile picture: {e}"
    if result[0]:
        return f"Downloaded {result[1]} successful."
    else:
        return f"Downloading {result[1]} failed."
