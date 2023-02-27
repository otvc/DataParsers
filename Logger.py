import logging

log_settings = { 
    'filemode': 'a', 'format':"%(asctime)s %(levelname)s %(message)s"
}

logging.basicConfig(filename = 'parser_error.log', level=logging.ERROR, **log_settings)
logging.basicConfig(filename = 'parser_warning.log', level=logging.WARNING, **log_settings)