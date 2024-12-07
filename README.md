# **Road Trip Cost Calculator**

## **Overview**
Planning a road trip and want a more accurate fuel cost estimate? The Road Trip Cost Calculator takes the guesswork out of budgeting by calculating trip costs based on **state-specific gas prices**, **fuel efficiency**, and **real driving distances** between stops. Perfect for Type-A planners who love road trips and want to avoid surprises at the pump!

This tool uses data from AAA’s gas price averages and Google Maps Distance Matrix to give you up-to-date, tailored estimates for your road trip costs.

---

## **Features**
- **State-Specific Gas Prices**: Scrapes the latest state gas price data from AAA’s website.
- **Fuel Efficiency**: Calculates costs based on your vehicle's miles-per-gallon (MPG).
- **Driving vs. Straight-Line Distances**: Incorporates real driving distances using Google Maps.
- **Custom Stops**: Input multiple stops and get detailed cost breakdowns for each segment.

---

## **Requirements**
1. **Python 3.8+**
2. **Dependencies**:
   - [pgeocode](https://pypi.org/project/pgeocode/)
   - [simplejson](https://pypi.org/project/simplejson/)
   - [selenium](https://pypi.org/project/selenium/)
   - [dotenv](https://pypi.org/project/python-dotenv/)
3. **Google Maps API Key**:
   - You’ll need a valid API key from the [Google Maps Platform](https://developers.google.com/maps/documentation/distance-matrix/get-api-key).

---

## **Installation**

### **1. Clone the Repository**
```bash
git clone https://github.com/m3lmark/road-trip-calculator.git
cd road-trip-calculator
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Set Up API Key**
- Create a `.env` file in the root directory:
  ```bash
  touch .env
  ```
- Add your Google Maps API key to the `.env` file:
  ```plaintext
  GOOGLE_API_KEY="your-google-api-key-here"
  ```

### **4. Set Up ChromeDriver**
Ensure ChromeDriver is installed and accessible. You can install it via:
- [WebDriver Manager](https://pypi.org/project/webdriver-manager/)
- Or by downloading directly from the [ChromeDriver site](https://chromedriver.chromium.org/downloads).

Update the `PATH` variable or provide the executable path directly in the script.

---

## **Usage**

### **Run the Script**
Run the program from the terminal:
```bash
python road_trip.py
```

### **Input Details**
- **Fuel Type**: Select from regular, mid-grade, premium, or diesel.
- **MPG**: Enter your vehicle's average fuel efficiency.
- **Stops**: Input the number of stops and their zip codes.

### **Output**
The program will display:
- Distances between stops (crow-fly and driving).
- Gas prices for the destination state.
- Estimated fuel cost for each segment.
- Total driving distance and overall trip cost.

---


## **Notes**
- **State Gas Prices**: Data is scraped from AAA’s official website. Ensure it is accessible during runtime.
- **API Key**: Keep your Google Maps API key private. Avoid sharing or committing it to public repositories.
- **Accuracy**: This tool provides estimates. Actual costs may vary depending on traffic, road conditions, and local gas price fluctuations.

---

## **Contributing**
Feel free to fork this repository and submit pull requests for improvements or additional features. Suggestions and feedback are welcome!

---

## **License**
This project is licensed under the MIT License. See the LICENSE file for details.

---

## **Acknowledgments**
- **AAA Gas Prices**: [State Gas Price Averages](https://gasprices.aaa.com/state-gas-price-averages/)
- **Google Maps Platform**: [Distance Matrix API](https://developers.google.com/maps/documentation/distance-matrix/overview)

Happy road-tripping! 🛣️
