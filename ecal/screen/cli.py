import logging
import platform

logging.basicConfig(level=logging.DEBUG)

def clear_screen():
        # if is mac
    if platform.system() == "Darwin":
        logging.info("Running on macOS, skipping hardware rendering")
        exit()

    from waveshare_epd import epd12in48b

    try:
        epd = epd12in48b.EPD()
        logging.info("init")
        epd.init()
        logging.info("Clear")
        epd.Clear()
        logging.info("sleep")
        epd.sleep()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd12in48b.epdconfig.module_exit()
        exit()
