import qrcode
from PIL import Image, ImageDraw, ImageFont
import qrcode
from ecal.screen.rendering import font

class QRCodeError(Exception):
    pass

"""
Used to generate the QR code that is displayed when credentials are missing or invalid.
The QR code encodes a URL that the user can visit to authenticate and grant access to their calendar data.
The make_qr_code function creates a QR code image from the provided URL and centers it on a surface of specified dimensions.
If the QR code is too large to fit on the surface, a QRCodeError is raised.
"""
def make_qr_code(url, surface):
    qr_background = make_qr_code_overlay(url, surface)

    qr_w, qr_h = qr_background.size
    s_w = surface.right - surface.left
    s_h = surface.bottom - surface.top
    px = int((s_w - qr_w) / 2)
    py = int((s_h - qr_h) / 2)
    if px < 0 or py < 0:
        raise QRCodeError(f"Oh oh, image is {qr_w}x{qr_h} and doesn't fit surface {surface}!")
    result = Image.new(qr_background.mode, (s_w, s_h), surface.WHITE)
    result.paste(qr_background, (px, py, px + qr_w, py + qr_h))
    return result

"""
Display the QR code on top of the existing calendar image, in the middle of the second day's events,
so that the calendar can still be used while waiting for the token to be updated.
"""
def add_qr_code(url, surface, image):
    qr_background = make_qr_code_overlay(url, surface)
    qr_w, qr_h = qr_background.size

    # Place the QR code background in the middle of the second day's events box
    s_w = surface.right - surface.left
    half_sw = int(s_w / 2)
    s_h = surface.bottom - surface.top

    px = int((half_sw - qr_w) / 2) + half_sw
    py = int((s_h - qr_h) / 2)

    if px < 0 or py < 0:
        raise QRCodeError(
            f"Oh oh, image is {qr_w}x{qr_h} and doesn't fit surface {surface}!"
        )

    image.paste(qr_background, (px, py, px + qr_w, py + qr_h))
    return image

"""
Make a QR code with a black border, and a white label on the top with an extra thick border.
"""
def make_qr_code_overlay(url, surface):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=6,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color=surface.BLACK,
        back_color=surface.WHITE
    ).convert("1")  # keep 1-bit

    qr_w, qr_h = qr_image.size

    border = 20
    banner_height = 54

    qr_background_w = qr_w + border * 2
    qr_background_h = qr_h + border * 2 + banner_height

    # 0 = black background
    qr_background = Image.new("1", (qr_background_w, qr_background_h), 0)

    # Paste QR (shifted down by banner)
    qr_background.paste(qr_image, (border, border + banner_height))

    draw = ImageDraw.Draw(qr_background)

    text = "Login has expired. Please sign in."
    the_font = font(size=27)

    # get the size of the text
    bbox = draw.textbbox((0, 0), text, font=the_font)
    text_w = bbox[2] - bbox[0]
    #text_h = bbox[3] - bbox[1]

    text_x = (qr_background_w - text_w) // 2
    text_y = border

    draw.text((text_x, text_y), text, fill=1, font=the_font)
    return qr_background