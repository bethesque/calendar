import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..", "..")))

from qr import make_qr_code
from model import Surface
from hardware_screen import hardware_render
from env import IS_LOCAL


if __name__ == "__main__":
    url = "https://www.google.com/calendar"
    surface = Surface(0, 0, 1304, 984)
    image = make_qr_code(url, surface)
    if IS_LOCAL:
        image.show("test")
    else:
        hardware_render(image)
