import qrcode
from PIL import Image


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
        print(f"Oh oh, image is {qr_w}x{qr_h} and doesn't fit surface {surface}!")
        return qr_image
    print(type(qr_image))
    result = Image.new(qr_image.mode, (s_w, s_h), surface.WHITE)
    result.paste(qr_image, (px, py, px + qr_w, py + qr_h))
    return result
