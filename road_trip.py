import math
import pgeocode
import simplejson
import sys
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def get_gas_prices():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=options)
    driver.get("https://gasprices.aaa.com/state-gas-price-averages/")
    gas_prices = (
        driver.find_element(By.XPATH, "//table[@id='sortable']")
        .text.replace("$", "")
        .split("\n")[1:]
    )
    state_gas_prices = []
    # example state - ["Alaska", 3.719, 3.878, 4.078, 3.555]
    for state in gas_prices:
        split_up = state.split(" ")
        while len(split_up) > 5:
            split_up[0] = f"{split_up[0]} {split_up[1]}"
            split_up.remove(split_up[1])
        for z in range(1, 5):
            split_up[z] = float(split_up[z])
        state_gas_prices.append(split_up)
    return state_gas_prices


def get_trip_stats():
    type_of_gas = 0
    while type_of_gas < 1 or type_of_gas > 4:
        type_of_gas = int(
            input(
                "1 for regular\n2 for mid-grade\n3 for premium\n4 for diesel\n\nwhat type of gas?\t\t\t\t\t\t"
            )
        )
    mpg = int(input("how many mpg are you averaging?\t\t\t"))
    num_of_markers = int(input("how many points are we stopping at?\t\t"))
    return type_of_gas, mpg, num_of_markers


def get_stops(num_of_markers):
    markers = {}
    print("****************************************************************")
    for x in range(num_of_markers):
        label = input("what do you want to call this stop?\t\t")
        while label in list(markers.keys()):
            label = input("what do you want to call this stop?\t\t")
        postal = 0
        while postal >= 99999 or postal <= 10000:
            postal = int(input("what is its zip code?\t\t\t\t\t"))
        markers[label] = postal
        print("********************************")
    print()
    return markers


def output_distance_and_price(markers, state_gas_prices, type_of_gas, mpg):
    total_crow_distance = 0
    total_driving_distance = 0
    total_gas_price = 0.0
    for i in range(len(markers.keys()) - 1):
        first_mark = pgeocode.Nominatim("us").query_postal_code(
            list(markers.values())[i]
        )
        second_mark = pgeocode.Nominatim("us").query_postal_code(
            list(markers.values())[i + 1]
        )
        crow_distance = math.ceil(
            pgeocode.GeoDistance("us").query_postal_code(
                list(markers.values())[i], list(markers.values())[i + 1]
            )
            * 0.621371
        )
        total_crow_distance += crow_distance
        destination_state = second_mark.state_name
        orig_coord = f"{first_mark.latitude}%2C{first_mark.longitude}"
        dest_coord = f"{second_mark.latitude}%2C{second_mark.longitude}"
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={orig_coord}&destinations={dest_coord}&mode=driving&language=en-EN&sensor=false&key={sys.argv[1]}"
        result = simplejson.load(urllib.request.urlopen(url))
        raw_distance = (
            str(result["rows"][0]["elements"][0]["distance"]["text"])
            .split(" ")[0]
            .replace(",", "")
        )
        distance_in_mi = math.ceil(float(raw_distance) * 0.621371)
        total_driving_distance += distance_in_mi
        print(
            f"********************************\n{list(markers.keys())[i]} --> {list(markers.keys())[i+1]}\ncrow flies:\t\t\t\t{crow_distance:,} mi\ncar:\t\t\t\t\t{distance_in_mi:,} mi"
        )
        for state in state_gas_prices:
            if state[0] == destination_state:
                print(
                    f"gas price for {destination_state} is ${state[type_of_gas]}/gal (for the type of gas you selected)"
                )
                gas_price = distance_in_mi / mpg * state[type_of_gas]
                total_gas_price += gas_price
                print(f"price of fuel for this section: ${round(gas_price, 2)}")
    print(f"****************\nTotal distance by crow: {total_crow_distance:,}")
    print(f"Total distance by car: {total_driving_distance:,}")
    print(f"Total gas price: ${round(total_gas_price, 2)}")


prices = get_gas_prices()
gas_type, fuel_econ, markers_count = get_trip_stats()
markers_root = get_stops(markers_count)
output_distance_and_price(markers_root, prices, gas_type, fuel_econ)
