import requests
import json
import logging

logging.basicConfig(level=logging.INFO)


class SEIMSender:
    """
    Base class to facilitate sending data to different SEIM systems.

    This class defines general behavior expected from subclasses implementing
    a specific SEIM system.
    """

    def __init__(self, url, token):
        """Initialize with URL and token."""
        self.url = url
        self.token = token

    def build_headers(self):
        """Must be overriden by subclasses to provide headers."""
        raise NotImplementedError("Must be implemented in a subclass.")

    def build_payload(self, data):
        """Must be overriden by subclasses to build payload."""
        raise NotImplementedError("Must be implemented in a subclass.")

    def send_data(self, data):
        """Sends Data to the SEIM system using a HTTP POST request."""
        headers = self.build_headers()
        payload = self.build_payload(data)
        try:
            response = requests.post(self.url, headers=headers, data=json.dumps(payload), verify=False)
            if response.status_code == 200:
                print("Success")
            else:
                print(f"Failure status: {response.status_code}")
                logging.error(f"Failure status: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error: {e}")


class Splunk(SEIMSender):
    """Implementation of SEIMSender for Splunk. Sends data specifically to the Splunk HEC"""

    def build_headers(self):
        """Builds the HTTP headers needed for sending data to Splunk."""
        return {
            "Authorization": f"Splunk {self.token}",
            "Content-Type": "application/json"
        }

    def build_payload(self, json_data):
        """Wraps the JSON data in the required structure for Splunk."""
        return {
            "event": json_data
        }


def main():
    """Main function, which prompts user for input and send data to their selected SIEM."""
    try:
        seim_choice = input('Enter "Splunk" if you are using Splunk, otherwise please enter "Other": ')
        if seim_choice == "Splunk":

            original_data = input("JSON Data: ")
            try:
                valid_data = json.loads(original_data)
            except json.JSONDecodeError as json_error:
                print(f"Invalid JSON data: {json_error}")
                return
            url = input("Destination URL: ")
            token = input("Authorization Token: ")

            sender = Splunk(url, token)
            sender.send_data(valid_data)
        else:
            print("Only Splunk is supported currently.")

    except json.JSONDecodeError:
        print("Please provide valid JSON data next time.")
    except KeyboardInterrupt:
        print("Interuption occurred.")
    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
