# Road Trip Calculator, [Mel Mark](https://m3l.me), 2021
# Background
I love to go on road trips with my dog and camp along the way. I'm also a type A planner that likes to have a rough estimate for costs.
<br><br>Traditionally, I have used the [United States Department of Energy's price calculator](https://www.fueleconomy.gov/trip/) to estimate the price of fuel, but I believe it could be more accurate.
<br><br>Their website uses the national average of regular grade fuel to calculate the total cost, but this is significantly flawed if you like to do a lot of driving in California, like me, where the price of fuel is much higher than the national average.
<br><br>Therefore, I made a tool that accounts for state averages, segments of the road trip, up-to-date accuracy, and fuel grades (regular/mid/premium/diesel).
# Installation 
You'll want to run the following commands to install the required packages
- ```pip install pgeocode```
- ```pip install simplejson```
- ```pip install selenium```

<br>You will also need a [Google Maps Platform](https://developers.google.com/maps) API key. You can get one for free but be sure to keep it a secret so it can't be compromised.
<br><br>Once the packages are installed and you have an API key, use the following to run in the terminal (make sure to use python3),
- ```python road_trip.py "key"```
  - Replace key with whatever your Google API key is
    - (keep the quotation marks wrapped around it, though)
# Notes
This is just a quick little tool I made one late night preparing for a trip out to NorCal (from the Midwest where I'm from). If you have suggestions on how to improve it, please give me a shout or feel free to fork it and improve upon it yourself!
<br><br>Safe travels and always fill up for gas _before_ the gas light comes on ;)
