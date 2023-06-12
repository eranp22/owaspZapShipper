# ZapShipper

ZapShipper is a tool for shipping OWASP ZAP alerts to Logz.io for centralized log management. It collects the newest JSON files containing ZAP alerts, reads their contents, and sends the alerts to Logz.io for further analysis.

## Prerequisites

Before running ZapShipper, make sure you have the following:

- Python 3 installed on your system
- The required Python packages installed (specified in `requirements.txt`)

## Installation

1. Clone the ZapShipper repository to your local machine.
2. Install the required Python packages by running the following command in your terminal:

```shell
pip install -r requirements.txt
```
## Configuration
ZapShipper requires a configuration file (config.yaml) to specify the Logz.io URL, Logz.io token, and parent folder path.

**logzio**
| Parameter Name | Description | Required/Optional | Default |
| --- | --- | --- | --- |
| url | The Logz.io Listener URL for your region with port 8071. https://listener.logz.io:8071 | Required | - |
| token | Your Logz.io log shipping token securely directs the data to your Logz.io account. | Required | - |

**Parent Folder**
| Parameter Name | Description | Required/Optional | Default |
| --- | --- | --- | --- |
| parentFolder | The path to the parent folder containing the website folders. | Required | - |
### yaml
```yaml
logzio:
  url: "https://listener.logz.io:8071"
  token: "<Logz.io_Token>"
parentFolder: "<Path_To_Main_Websites_Folder>"
```

## Usage
To run ZapShipper, execute the main.py script:


```shell
python main.py
```
ZapShipper will start collecting the newest JSON files containing ZAP alerts, reading their contents, and sending the alerts to Logz.io. The tool will display the alerts on the console and log any errors or exceptions encountered during the process.

## Log File
ZapShipper logs its activity to a file named log.log. The log file contains timestamped entries with information about the execution, alerts sent to Logz.io, and any errors or exceptions that occurred.

## Last Created At File
ZapShipper utilizes a `lastCreatedAt.txt` file located in the `parentFolder` to store the timestamp of the last created JSON file that has been processed. This file is used to track the progress of alert collection and ensure that only the newest files are processed during each run. 
