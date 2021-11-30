import googlemaps
import math
import pgeocode
import simplejson
import sys
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

gmaps = googlemaps.Client(key=sys.argv[1])


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
    gas_tank = float(input("how many gallons does your gas tank hold?\t"))
    miles_until_fill_up = int(gas_tank * mpg)
    buffer = float(
        input(
            f"in theory, your car can go {miles_until_fill_up} miles\nuntil needing to be filled up,\nhowever this isn't recommended.\nhow many miles would you like to leave as a buffer?\t"
        )
    )
    while buffer >= miles_until_fill_up:
        buffer = float(
            input(
                f"in theory, your car can go {miles_until_fill_up} miles\nuntil needing to be filled up,\nhowever this isn't recommended.\nhow many miles would you like to leave as a buffer?\t"
            )
        )
    miles_until_fill_up -= buffer
    num_of_markers = int(input("how many points are we stopping at?\t\t"))
    return type_of_gas, mpg, gas_tank, num_of_markers, miles_until_fill_up


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


def output_distance_and_price(
    markers, state_gas_prices, type_of_gas, mpg, miles_until_fill_up, gas_tank
):
    total_driving_distance = 0
    total_gas_price = 0.0
    buffer_percent = miles_until_fill_up / gas_tank
    buffer_gas_tank = buffer_percent * gas_tank
    origin_state = (
        pgeocode.Nominatim("us").query_postal_code(list(markers.values())[0]).state_name
    )
    for state in state_gas_prices:
        if state[0] == origin_state:
            total_gas_price += state[type_of_gas] * gas_tank
    print(
        f"To completely fill up your gas tank at\nthe start of the trip in {origin_state}\n(assuming it's empty),\nit'll be ${round(total_gas_price, 2)}"
    )
    for i in range(len(markers.keys()) - 1):
        first_mark = pgeocode.Nominatim("us").query_postal_code(
            list(markers.values())[i]
        )
        second_mark = pgeocode.Nominatim("us").query_postal_code(
            list(markers.values())[i + 1]
        )
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
            f"********************************\n{list(markers.keys())[i]} --> {list(markers.keys())[i+1]}\n{distance_in_mi:,} mi"
        )
        for state in state_gas_prices:
            if state[0] == destination_state:
                print(
                    f"gas price for {destination_state} is ${state[type_of_gas]}/gal (for the type of gas you selected)"
                )
                gas_price = distance_in_mi / mpg * state[type_of_gas]
                total_gas_price += gas_price
                print(f"price of fuel for this section: ${round(gas_price, 2)}")
    print(f"\nTotal distance by car: {total_driving_distance:,}")
    print(f"Total gas price: ${round(total_gas_price, 2)}")
    number_of_fills = math.ceil(total_driving_distance/buffer_gas_tank)-1
    print(f"You'll need to stop for gas {number_of_fills} times\n(not including the initial fill up)")
    mile_stop = []
    for index in range(number_of_fills):
        print(f"Stop at mile # {int(buffer_gas_tank*(index+1))}")
        mile_stop.append(int(buffer_gas_tank*(index+1)))
    print(markers)
    return buffer_gas_tank


def get_fuel_stops(waypoints, miles_until_fill):
    waypoints_nested = []
    if len(waypoints) > 2:
        for i in range(1, len(waypoints)-1):
            waypoints_nested.append([waypoints[i], True])
    directions_result = gmaps.directions(str(waypoints[0]), str(waypoints[len(waypoints)-1]), waypoints=waypoints_nested)
    cleaned_list = []
    miles_list = []
    end_coords = []
    for thing in str(directions_result).split(','):
        if 'distance' in thing or 'lat' in thing or 'lng' in thing:
            to_append = thing.replace("'", '')
            to_append = to_append.replace('}', '')
            to_append = to_append.replace('{', '')
            to_append = to_append.replace(',', '')
            to_append = to_append.replace(' [distance: text:', '')
            to_append = to_append.replace('distance: text: ', '')
            to_append = to_append.replace('lat: ', '')
            to_append = to_append.replace('lng: ', '')
            to_append = to_append.replace('location: ', 'location:\n')
            to_append = to_append.replace(' ', '')
            if 'ft' in to_append:
                to_append = ''
            if 'mi' in to_append:
                cleaned_list.append('\n' + to_append)
            else:
                cleaned_list.append(to_append)
    for i in range(len(cleaned_list)):
        if 'mi' in cleaned_list[i] and 'legs' not in cleaned_list[i]:
            miles_list.append(float(cleaned_list[i].replace('steps:', '').replace('mi', '').replace('\n', '')))
            end_coords.append(
                [float(cleaned_list[i + 2]), float(cleaned_list[i + 3].replace('start_location:', ''))])
    total = 0
    for z in range(len(miles_list)):
        total += miles_list[z]
        if total >= miles_until_fill:
            print(f"STOP AT: {end_coords[z-1]}")
            total -= miles_until_fill



prices = get_gas_prices()
gas_type, fuel_econ, tank_capacity, markers_count, miles_before_stop = get_trip_stats()
markers_root = get_stops(markers_count)
miles_to_fill = output_distance_and_price(
    markers_root, prices, gas_type, fuel_econ, miles_before_stop, tank_capacity
)
get_fuel_stops(list(markers_root.values()), miles_to_fill)
