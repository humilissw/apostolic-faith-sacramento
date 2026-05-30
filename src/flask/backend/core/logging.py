import logging
import sys

log = logging.getLogger("authlib")
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)
