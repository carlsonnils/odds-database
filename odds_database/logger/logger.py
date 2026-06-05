import logging


logger = logging.getLogger("odb")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt="{asctime} - {name} - {levelname} - {message}",
    style="{",
)

fh = logging.FileHandler("log.log")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

