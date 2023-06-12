import yaml
import signal
from logzio_shipper import *
from zapAlertExporter import *
from logger_config import *



class Manager:
    class logzio_error(Exception):
        pass

    class ConfigError(Exception):
        pass

    def __init__(self):
        """
        Initializes a new Manager object.

        :param config_file: The path to the configuration file.
        :param last_start_dates_file: The path to the file that stores the last start dates.
        """

        self.parentFolder = None
        self.config_file = "config.yaml"
        self.logzio_url = None
        self.logzio_token = None
        self.logzio_shipper = None
        self.headers = None

    def handle_sigint(self, signal, frame):
        logger.info("\nCtrl+C pressed. Stopping the shipper...")
        exit(0)

    def check_keys(self, data):
        if data is not None:
            if 'logzio' in data:
                if data['logzio'] is None:
                    error_message = "The 'logzio' dictionary is None."
                    logger.error(error_message)
                    raise self.ConfigError(error_message)
                elif 'url' not in data['logzio'] or 'token' not in data['logzio']:
                    error_message = "Either 'url' or 'token' is missing from the 'logzio' dictionary."
                    logger.error(error_message)
                    raise self.ConfigError(error_message)
                elif data['logzio']['token'] is None or data['logzio']['token'] == "":
                    error_message = "Logz.io token is missing or empty. Please provide a valid token."
                    logger.error(error_message)
                    raise self.ConfigError(error_message)
                elif data['parentFolder'] is None:
                    error_message = "Parent folder is not specified. Please provide the path to the parent folder."
                    logger.error(error_message)
                    raise self.ConfigError(error_message)
                elif not os.path.exists(data['parentFolder']):
                    error_message = "Parent folder does not exist. Please provide a valid path to the parent folder."
                    logger.error(error_message)
                    raise self.ConfigError(error_message)
        else:
            error_message = "Configuration data is missing."
            logger.error(error_message)
            raise self.ConfigError(error_message)
        return True

    def read_config(self):
        """
        Reads configuration information from a YAML file.
        """
        with open(self.config_file) as f:
            data = yaml.safe_load(f)

        if not self.check_keys(data):
            return False

        self.logzio_url = data['logzio']['url']
        self.logzio_token = data['logzio']['token']
        self.logzio_shipper = LogzioShipper(self.logzio_url, self.logzio_token)
        self.parentFolder = data['parentFolder']
        return True

    def send_alerts_to_logzio(self, filename, alerts):
        try:
            if len(alerts) != 0:
                logger.info("Alerts number: {}".format(len(alerts)))
                for alert in alerts:
                    alert_str = json.dumps(alert)
                    self.logzio_shipper.add_log_to_send(alert_str)
                logger.info("Trying to send alerts to Logz.io- Filename: %s, Number of Alerts: %d", filename, len(alerts))
                self.logzio_shipper.send_to_logzio()
            else:
                logger.info("No events")
        except Exception as e:
           raise self.logzio_error("Failed to send data to Logz.io... {}".format(e))
        except requests.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 400:
                raise self.logzio_error("The logs are bad formatted. response: {}".format(e))
            if status_code == 401:
                raise self.logzio_error("The token is missing or not valid. Make sure you’re using the right account token.")
            raise self.logzio_error("Somthing went wrong. response: {}".format(e))

    def run(self):
        signal.signal(signal.SIGINT, self.handle_sigint)
        if not self.read_config():
            return
        try:

            parent_folder = self.parentFolder
            newest_json_files = collect_newest_json_files(parent_folder)

            for file in newest_json_files:
                exporter = ZapAlertExporter(file)
                try:
                    alerts = exporter.read_json_file()
                    self.send_alerts_to_logzio(file, alerts)

                except self.logzio_error as e:
                    logger.error("Logz.io Error: %s", str(e))
                except self.ConfigError as e:
                    logger.error("Config Error: %s", str(e))
                except Exception as e:
                    logger.error("Error: %s", str(e))
        except Exception as e:
            logger.error("Error: %s", str(e))