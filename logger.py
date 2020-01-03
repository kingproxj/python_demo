import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
if "log_level" in os.environ:
    logger.setLevel(os.environ["log_level"])
handler = logging.FileHandler("./log/fcs.log")
handler.setLevel(logging.DEBUG)
if "log_level" in os.environ:
    handler.setLevel(os.environ["log_level"])
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(thread)d - %(process)d - %(funcName)s - %('
                              'lineno)d - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
if "log_level" in os.environ:
    console.setLevel(os.environ["log_level"])

logger.addHandler(handler)
logger.addHandler(console)
