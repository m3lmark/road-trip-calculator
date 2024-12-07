import math
import pgeocode
import simplejson
import sys
import urllib.request
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("API key not found. Please set GOOGLE_API_KEY in your environment.")

def get_gas_prices():
    """
    Scrapes AAA's website to get state-level gas prices.
    Returns:
        List of lists containing state gas prices.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get("https://gasprices.aaa.com/state-gas-price-averages/")

    try:
        gas_prices_table = driver.find_element(By.XPATH, "//table[@id='sortable']").text
        gas_prices = gas_prices_table.replace("$", "").split("\n")[1:]
    except Exception as e:
        driver.quit()
        raise RuntimeError(f"Failed to scrape gas prices: {e}")

    state_gas_prices = []
    for state in gas_prices:
        split_up = state.split(" ")
        while len(split_up) > 5:
            split_up[0] += f" {split_up[1]}"
            split_up.pop(1)
        split_up[1:] = map(float, split_up[1:])
        state_gas_prices.append(split_up)

    driver.quit()
    return state_gas_prices


def get_trip_stats():
    """
    Collects trip-related details from the user.
    Returns:
        Tuple containing gas type, mpg, and number of stops.
    """
    print("Trip Setup:")
    while True:
        try:
            gas_type = int(input("Select fuel type:\n1. Regular\n2. Mid-grade\n3. Premium\n4. Diesel\n> "))
            if 1 <= gas_type <= 4:
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    while True:
        try:
            mpg = float(input("Enter your vehicle's MPG: "))
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    
    while True:
        try:
            num_of_markers = int(input("How many stops are planned? "))
            break
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    return gas_type, mpg, num_of_markers


def get_stops(num_of_markers):
    """
    Collects stop information from the user.
    Returns:
        Dictionary mapping stop labels to postal codes.
    """
    markers = {}
    print("Enter stop details:")
    for _ in range(num_of_markers):
        while True:
            label = input("Enter a name for this stop: ")
            if label in markers:
                print("This name is already used. Please choose a unique label.")
            else:
                break

        while True:
            try:
                postal = int(input(f"Enter the zip code for {label}: "))
                if 10000 <= postal <= 99999:
                    markers[label] = postal
                    break
                else:
                    print("Invalid zip code. Please enter a 5-digit zip code.")
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

    return markers


def calculate_trip_costs(markers, state_gas_prices, gas_type, mpg):
    """
    Calculates and displays distances and fuel costs for the trip.
    """
    total_crow_distance, total_drive_distance, total_gas_price = 0, 0, 0.0
    nominatim = pgeocode.Nominatim("us")
    geo_distance = pgeocode.GeoDistance("us")

    for i in range(len(markers) - 1):
        origin_label, dest_label = list(markers.keys())[i], list(markers.keys())[i + 1]
        origin_zip, dest_zip = markers[origin_label], markers[dest_label]

        origin_info, dest_info = nominatim.query_postal_code(origin_zip), nominatim.query_postal_code(dest_zip)
        crow_distance = math.ceil(geo_distance.query_postal_code(origin_zip, dest_zip) * 0.621371)
        total_crow_distance += crow_distance

        url = (
            f"https://maps.googleapis.com/maps/api/distancematrix/json?"
            f"origins={origin_info.latitude},{origin_info.longitude}&"
            f"destinations={dest_info.latitude},{dest_info.longitude}&"
            f"mode=driving&language=en&sensor=false&key={GOOGLE_API_KEY}"
        )
        result = simplejson.load(urllib.request.urlopen(url))
        drive_distance = math.ceil(float(result["rows"][0]["elements"][0]["distance"]["text"].replace(",", "")))
        total_drive_distance += drive_distance

        dest_state = dest_info.state_name
        gas_price = next(state[gas_type] for state in state_gas_prices if state[0] == dest_state)
        segment_cost = drive_distance / mpg * gas_price
        total_gas_price += segment_cost

        print(f"{origin_label} -> {dest_label}: {drive_distance} mi (${segment_cost:.2f} for gas)")

    print(f"Total driving distance: {total_drive_distance:,} mi")
    print(f"Total gas cost: ${total_gas_price:.2f}")


if __name__ == "__main__":
    gas_prices = get_gas_prices()
    gas_type, mpg, num_stops = get_trip_stats()
    trip_markers = get_stops(num_stops)
    calculate_trip_costs(trip_markers, gas_prices, gas_type, mpg)
