import qrcode
from PIL import Image

"""
Used to generate the QR code that is displayed when credentials are missing or invalid.
The QR code encodes a URL that the user can visit to authenticate and grant access to their calendar data.
The make_qr_code function creates a QR code image from the provided URL and centers it on a surface of specified dimensions.
If the QR code is too large to fit on the surface, a QRCodeError is raised.
"""

class QRCodeError(Exception):
    pass

def make_qr_code(url, surface):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color=surface.BLACK, back_color=surface.WHITE).convert("1")
    qr_w, qr_h = qr_image.size
    s_w = surface.right - surface.left
    s_h = surface.bottom - surface.top
    px = int((s_w - qr_w) / 2)
    py = int((s_h - qr_h) / 2)
    if px < 0 or py < 0:
        raise QRCodeError(f"Oh oh, image is {qr_w}x{qr_h} and doesn't fit surface {surface}!")
    result = Image.new(qr_image.mode, (s_w, s_h), surface.WHITE)
    result.paste(qr_image, (px, py, px + qr_w, py + qr_h))
    return result
