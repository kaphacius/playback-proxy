# http://uran198.github.io/en/python/2016/07/12/colorful-python-logging.html

import logging
import colorama
import copy

# specify colors for different logging levels
LOG_COLORS = {
    logging.ERROR: colorama.Fore.RED,
    logging.WARNING: colorama.Fore.YELLOW,
    logging.INFO: colorama.Fore.BLUE
}


class ColorFormatter(logging.Formatter):
    def format(self, record, *args, **kwargs):
        # if the corresponding logger has children, they may receive modified
        # record, so we want to keep it intact
        new_record = copy.copy(record)
        if new_record.levelno in LOG_COLORS:
            # we want levelname to be in different color, so let's modify it
            new_record.levelname = "{color_begin}{level}{color_end}".format(
                level=new_record.levelname,
                color_begin=LOG_COLORS[new_record.levelno],
                color_end=colorama.Style.RESET_ALL,
            )
        # now we can let standart formatting take care of the rest
        return super(ColorFormatter, self).format(new_record, *args, **kwargs)

# we want to display only levelname and message
formatter = ColorFormatter("%(levelname)s %(message)s")

# this handler will write to sys.stderr by default
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# adding handler to our logger
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel("INFO")