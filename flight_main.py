import os # used to help with accessing private usernames and passwords
import time
from datetime import datetime, timedelta
from data_managerr import DataManager
from flight_searchh import FlightSearch
from flight_dataa import find_cheapest_flight
from notification_managerr import Notification_manager
import smtplib
from dotenv import load_dotenv
load_dotenv()


# Google form for users to input data.
# https://docs.google.com/forms/d/e/1FAIpQLServ-pgUnxTYy-K7KAbL1Cne8N-jroTmFucGWYlYqtHc8_J2g/viewform?usp=sf_link
# ************************************* Set up the Flight Search ****************************************

# Creating Classes
data_manager = DataManager()
sheet_data = data_manager.get_destination_data()
flight_search = FlightSearch()


# Set your origin airport, I just used LON for an example.
ORIGIN_CITY_IATA = "LON"

# ************************************* Update the Airport Codes in Google Sheet *************************************

for row in sheet_data:
    if row["iataCode"] == "":
        row["iataCode"] = flight_search.get_destination_code(row["city"])
        # slowing down requests to avoid rate limit or crashes
        time.sleep(2)
# print(f"sheet_data:\n {sheet_data}")

data_manager.destination_data = sheet_data
data_manager.update_destination_codes()

# ************************************* Setting time ***********************************
tomorrow = datetime.now() + timedelta(days=1)
six_month_from_today = datetime.now() + timedelta(days=(6 * 30))

# ************************************* Access all the emails in the user spreadsheet ********************

user_email_list = data_manager.get_user_data()


# ************************************* Main implementation *************************************

for destination in sheet_data:
    # print(f"Getting flights for {destination}")
    # Note that data is the super-big code returned, it holds all flight-offer info.
    data = flight_search.check_flights(
        ORIGIN_CITY_IATA,
        destination["iataCode"],
        from_time=tomorrow,
        to_time=six_month_from_today,
        is_direct='true'
    )

    # print(data)
    # Note that after this try and except, the code still continues to the next line
    # It is not like a return or an error that makes you exit the code.
    try:
        '''
        If it is not direct the data will print("No flight data") which is when the 
        except will kick in and then check if it has multiple stops. 
        '''
        stops_length = len(data['data'][0]['itineraries'][0]['segments'])
    except IndexError:
        data = flight_search.check_flights(
            ORIGIN_CITY_IATA,
            destination["iataCode"],
            from_time=tomorrow,
            to_time=six_month_from_today,
            is_direct= 'false'
        )
        # Indicates how many stops the trip will have.
        stops_length = len(data['data'][0]['itineraries'][0]['segments'])
    cheapest_flight = find_cheapest_flight(data, stops_length)
    # print(cheapest_flight.price)

# ************************************* Sending email to possible client's if valid *********************

    special_character = '\u0404'
    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination['price']: # destination['price']:
        # notification_manager = Notification_manager(cheapest_flight)
        # notification_manager.send_message(stops_length)
        for emails in user_email_list:
            my_email = os.environ['MY_EMAIL']
            password = os.environ['MY_EMAIL_PASSWORD']

            with smtplib.SMTP(os.environ['EMAIL_PROVIDER_SMTP_ADDRESS']) as connection:
                # This protects the email
                connection.starttls()
                # sending the email with message
                connection.login(user=my_email, password=password)
                connection.sendmail(from_addr=my_email, to_addrs=emails,
            msg= f'Subject: ISS Above\n\nLow price Alert: Only: ${float(cheapest_flight.price)} to fly from '
            f'{cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}.'
            f' The flight will have {stops_length} stops and the trip will start '
            f'on {cheapest_flight.out_date} until {cheapest_flight.return_date}. ')


