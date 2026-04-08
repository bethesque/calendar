import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..", "..")))

from qr import make_qr_code
from model import Surface
from screen import hardware_render


if __name__ == "__main__":
    url = "https://www.google.com/calendar"
    surface = Surface(0, 0, 1304, 984)
    image = make_qr_code(url, surface)
    hardware_render(image)
