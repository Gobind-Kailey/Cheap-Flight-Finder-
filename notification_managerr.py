import os
from dotenv import load_dotenv
from twilio.rest import Client
from flight_dataa import FlightData

load_dotenv()
# Belows class is used to send a text message instead of an email.
class Notification_manager():

  def __init__(self, cheapest_flight):
    self.account_sid = os.environ['TWILIO_SID']
    self.auth_token = os.environ['auth_token']
    self.client = Client(self.account_sid, self.auth_token)
    self.cheapest_flight = cheapest_flight

  def send_message(self, stop_length):
    message = self.client.messages.create(
      body= f'Low price Alert: Only: Є{float(self.cheapest_flight.price)}, to fly from '
            f'{self.cheapest_flight.origin_airport} to {self.cheapest_flight.destination_airport}.'
            f'The flight will have {stop_length} stops and the trip will start '
            f',on {self.cheapest_flight.out_date} until {self.cheapest_flight.return_date}. ',
      from_= os.environ["FROM_NUMBER"],
      to= os.environ['MY_NUMBER'],
    )
    print(message.status)




