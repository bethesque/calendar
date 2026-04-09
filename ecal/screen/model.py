from dataclasses import dataclass
@dataclass
class Surface:
    top:int = 0
    left:int = 0
    right:int = 800
    bottom:int = 480
    BLACK  = 0x000000   #   00  BGR
    WHITE  = 0xffffff   #   01
    YELLOW = 0x00ffff   #   10
    RED    = 0x0000ff   #   11