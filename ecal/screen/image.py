from ecal.screen.layout import layout_calendars
from ecal.screen.qr import make_qr_code, add_qr_code
from ecal.env import filter, SERVER_ADDRESS, DATA_DIRECTORY, CACHE_DIRECTORY
import logging
import os
import hashlib


LAST_RENDERED_IMAGE_SHA_FILE = CACHE_DIRECTORY + "/last_rendered_image_sha.txt"

logger = logging.getLogger(__name__)

def load_image(calendar_source, surface, force, use_cached_data = False):
    calendar_source.load_creds()
    calendar_days = None
    image = None

    if calendar_source.creds_valid() and not use_cached_data:
        logger.info("Fetching calendar data from Google")
        calendar_days = calendar_source.fetch_data(filter)
        calendar_source.save_data_to_file()
    elif calendar_source.cache_file_exists():
        logger.info(f"Using cached calendar data from {calendar_source.cache_file_path}")
        calendar_days = calendar_source.load_data_from_file()

    if calendar_days:
        image = layout_calendars(calendar_days, surface)
        if not calendar_source.creds_valid():
            logger.info("Credentials invalid, rendering QR code for re-auth")
            # Show the QR code on top of the calendar screen using the cached data file
            image = add_qr_code(SERVER_ADDRESS, surface, image)
    else:
        # Show a blank screen with a QR code
        logger.info("No cached calendar data found, rendering QR code for re-auth")
        image = make_qr_code(SERVER_ADDRESS, surface)

    return return_image_if_modified_or_forced(image, force)


def return_image_if_modified_or_forced(image, force):
    last_image_sha = get_last_rendered_image_sha()
    this_image_sha = sha256_img(image)

    if force:
        logger.info(f"Returning image for rendering as force is True")
        save_last_rendered_image_sha(this_image_sha)
        return image
    elif this_image_sha != last_image_sha:
        logger.info(f"Returning image for rendering as image SHA has changed from {last_image_sha} to {this_image_sha}")
        save_last_rendered_image_sha(this_image_sha)
        return image
    else:
        logger.info(f"Image sha has not changed ({this_image_sha}), and force is not True, so returning None")
        return None

def save_last_rendered_image_sha(sha):
    os.makedirs(os.path.dirname(LAST_RENDERED_IMAGE_SHA_FILE), exist_ok=True)
    with open(LAST_RENDERED_IMAGE_SHA_FILE, "w") as f:
        f.write(sha + "\n")

def get_last_rendered_image_sha():
    if os.path.exists(LAST_RENDERED_IMAGE_SHA_FILE):
        with open(LAST_RENDERED_IMAGE_SHA_FILE) as f:
            return f.read().strip()
    return None

def sha256_img(image) -> str:
    data = image.tobytes()
    return hashlib.sha256(data).hexdigest()

def local_render(image):
    image.show("test")
