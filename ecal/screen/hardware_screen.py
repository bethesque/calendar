import time
import logging
from multiprocessing import Process

logger = logging.getLogger(__name__)

def hardware_render_worker(image):
    from waveshare_epd import epd12in48b
    from PIL import Image

    try:
        start = time.monotonic()
        epd = epd12in48b.EPD()
        epd.Init()
        RedImage = Image.new("1", (epd12in48b.EPD_WIDTH, epd12in48b.EPD_HEIGHT), 255)
        epd.display(image, RedImage, 270)
        epd.EPD_Sleep()
        end = time.monotonic()
        logger.info("hardware_render time: %.3f seconds", end - start)
    except IOError as e:
        logger.exception(f"Error rending screen: {e}")
    finally:
        epd12in48b.epdconfig.module_exit()


def hardware_render(image):
    p = Process(target=hardware_render_worker, args=(image,))
    p.start()

    try:
        p.join(timeout=290)  # Almost 5 minutes

        if p.is_alive():
            logger.error("Display update exceeded 5 minute timeout")

            p.terminate()
            p.join(10)

            if p.is_alive():
                logger.error("Failed to terminate display process, forcing kill")
                p.kill()
                p.join()

            raise TimeoutError("Display update timed out")

    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt received — terminating render process")

        if p.is_alive():
            p.terminate()
            p.join(10)

            if p.is_alive():
                p.kill()
                p.join()

        raise

    finally:
        # Safety net: ensure no orphan process remains
        if p.is_alive():
            logger.error("Cleaning up orphan render process in finally block")
            p.terminate()
            p.join(10)
            if p.is_alive():
                p.kill()
                p.join()
