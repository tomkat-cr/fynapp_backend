import os
import logging
import logging.config
import yaml
import datetime

DEBUG = (os.environ.get('FLASK_DEBUG', '0') == '1')

LOG_CONFIG_FILE = './config/logging.conf.yml'
LOG_FILE_PATH = './logs/fynapp_general.log'

# read_only_file_system = False
read_only_file_system = True
if not read_only_file_system:
    if not os.path.isfile(LOG_FILE_PATH):
        try:
            with open(LOG_FILE_PATH, mode="a") as log_file_created:
                log_file_created.write(
                    "Init Log file | {}".format(datetime.datetime.now())
                )
        except Exception as err:
            if 'Read-only file system' in err:
                print(">>--> read_only_file_system...")
                read_only_file_system = True
            else:
                raise

if not read_only_file_system:
    with open(LOG_CONFIG_FILE) as f:
        log_config = f.read()
        logging.config.dictConfig(yaml.safe_load(log_config))
        logfile = logging.getLogger('file')
        logconsole = logging.getLogger('console')


def log_debug(message):
    if DEBUG:
        if read_only_file_system:
            print("[DEBUG] {} | {}".format(datetime.datetime.now(), message))
        else:
            logconsole.debug(message)


def log_warning(message):
    if read_only_file_system:
        print("[WARNING] {} | {}".format(datetime.datetime.now(), message))
    else:
        logconsole.debug(message)
        logfile.warning(message)
