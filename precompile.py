import logging
from atst.assets import assets
from webassets.script import CommandLineEnvironment

# Setup a logger
log = logging.getLogger('webassets')
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

cmdenv = CommandLineEnvironment(assets, log)
cmdenv.build()
