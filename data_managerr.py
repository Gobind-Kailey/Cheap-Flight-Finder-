import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SHEETY_PRICES_ENDPOINT = os.environ['sheet_api']

class DataManager:

    def __init__(self):
        self._user = os.environ["SHEETY_USRERNAME"]
        self._password = os.environ["SHEETY_PASSWORD"]
        self._authorization = HTTPBasicAuth(self._user, self._password)
        self.destination_data = {}
        self.email = []

    # This provides the destination data.
    def get_destination_data(self):
        # Use the Sheety API to GET all the data in that sheet.
        response = requests.get(url=SHEETY_PRICES_ENDPOINT)
        data = response.json()
        # print(data)
        self.destination_data = data["prices"]
        # print(self.destination_data)
        return self.destination_data

    # This gets all the users emails and returns them in a list.
    def get_user_data(self):

        response = requests.get(url=os.environ['sheet_user_api'])
        listed_user_data = response.json()['users']
        for user_data in listed_user_data:
            self.email.append(user_data['whatIsYourEmail?'])
        return self.email

    # In the DataManager Class make a PUT request and use the row id from sheet_data
    # to update the Google Sheet with the IATA codes. (Do this using code).
    def update_destination_codes(self):
        for city in self.destination_data:
            new_data = {
                "price": {
                    "iataCode": city["iataCode"]
                }
            }
            response = requests.put(
                url=f"{SHEETY_PRICES_ENDPOINT}/{city['id']}",
                json=new_data
            )
            # print(response.text)
