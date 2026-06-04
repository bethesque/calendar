import time
import logging

logger = logging.getLogger(__name__)

def hardware_render(image):
    from waveshare_epd import epd12in48b
    from PIL import Image

    try:
        start = time.perf_counter()
        logger.info("epd12in48b.EPD()")
        epd = epd12in48b.EPD()
        logger.info("epd.Init()")
        epd.Init()
        logger.info("Making new red image")
        RedImage = Image.new("1", (epd12in48b.EPD_WIDTH, epd12in48b.EPD_HEIGHT), 255)
        logger.info("epd.display(image, RedImage)")
        epd.display(image, RedImage, 270)
        logger.info("epd.EPD_Sleep()")
        epd.EPD_Sleep()
        end = time.perf_counter()
        logger.info("hardware_render time: %.3f seconds", end - start)
    except IOError as e:
        logger.error(f"error: {e}")

    except KeyboardInterrupt:
        logger.info("ctrl + c:")
        epd12in48b.epdconfig.module_exit()
        exit()
