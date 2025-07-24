import kopf
import logging

# Import handlers to register them with Kopf
from . import handlers


@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.posting.level = logging.INFO
