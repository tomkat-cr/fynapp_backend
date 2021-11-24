import logging, logging.config, yaml

LOG_CONFIG_FILE='fynapp_api/config/logging.conf.yml'
with open(LOG_CONFIG_FILE) as f:
    log_config = f.read()
f.closed

logging.config.dictConfig(yaml.safe_load(log_config))
logfile = logging.getLogger('file')
logconsole = logging.getLogger('console')

def log_debug(message):
    logconsole.debug(message)

def log_warning(message):
    logconsole.debug(message)
    logfile.warning(message)
