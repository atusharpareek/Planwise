import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
from datetime import datetime
import threading  # For background API calls to keep UI responsive

# --- Configuration (API Keys - Replace with your actual keys) ---
OPENWEATHER_API_KEY = "8599c5e729e2485698f83819252105"  # Get your key from https://openweathermap.org/api


# --------- Autocomplete Combobox Class --------- #
class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        """Sets the list of items for autocomplete."""
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list
        self.bind('<KeyRelease>', self._check_key)
        self.bind('<FocusOut>', self._validate_input)  # Add validation on focus out

    def _check_key(self, event):
        """Filters the completion list based on user input."""
        value = self.get().lower()
        if value == '':
            data = self._completion_list
        else:
            data = [item for item in self._completion_list if item.lower().startswith(value)]

        if data != list(self['values']):  # Only update values if filtered data is different
            self['values'] = data
            if data and event.keysym not in ('BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down', 'Return', 'Tab'):
                self.event_generate('<Down>')  # Open dropdown, but don't auto-select

    def _validate_input(self, event):
        """Ensures the selected value is from the completion list."""
        current_value = self.get()
        if current_value not in self._completion_list and current_value != "":
            messagebox.showwarning("Invalid Input",
                                   f"Please select a valid item from the list for '{self.cget('textvariable')}'.")
            self.set("")  # Clear invalid input
            self.focus_set()  # Keep focus on the combobox until valid


# --------- API Fetchers --------- #
def get_countries():
    """Fetches all countries from Restcountries API."""
    try:
        response = requests.get("https://restcountries.com/v3.1/all", timeout=10)  # Increased timeout
        response.raise_for_status()
        countries_data = response.json()
        countries = sorted([c['name']['common'] for c in countries_data if 'name' in c and 'common' in c['name']])
        return countries
    except requests.exceptions.RequestException as e:
        print(f"Country API error: {e}")
        messagebox.showerror("API Error",
                             "Could not fetch country data. Using fallback list. Check your internet connection.")
        return ["United States", "Germany", "India", "United Kingdom", "Canada", "Australia", "Brazil", "China",
                "France", "Japan"]


def get_airlines():
    """
    Fetches airlines. PROFESSIONAL NOTE: This should ideally come from a dedicated airline API.
    For demonstration, we use a comprehensive static list.
    A paid API like AviationStack would be used in a production environment.
    """
    # In a professional setting, you'd integrate with an airline API here.
    # Example (pseudo-code for AviationStack):
    # try:
    #     response = requests.get(f"http://api.aviationstack.com/v1/airlines?access_key={AIRLINE_API_KEY}", timeout=10)
    #     response.raise_for_status()
    #     airlines_data = response.json()
    #     airlines = [airline['airline_name'] for airline in airlines_data['data']]
    #     return sorted(airlines)
    # except requests.exceptions.RequestException as e:
    #     print(f"Airline API error: {e}")
    #     messagebox.showwarning("API Warning", "Could not fetch real-time airline data. Using cached list.")

    return [
        "Lufthansa", "Emirates", "Qatar Airways", "British Airways", "Air India",
        "Turkish Airlines", "Singapore Airlines", "Delta Air Lines", "American Airlines",
        "Etihad Airways", "Air France", "KLM Royal Dutch Airlines", "SWISS",
        "ANA - All Nippon Airways", "Japan Airlines", "Korean Air", "Cathay Pacific",
        "Qantas", "Virgin Atlantic", "United Airlines", "Southwest Airlines",
        "Ryanair", "EasyJet", "Spirit Airlines", "IndiGo", "SpiceJet",
        "Vistara", "Air Canada", "LATAM Airlines", "Aeromexico", "SIA", "EVA Air", "Finnair",
        "SAS - Scandinavian Airlines", "Alaska Airlines", "JetBlue Airways", "Wizz Air",
        "Nippon Cargo Airlines", "Korean Air Cargo", "Air China Cargo", "DHL Aviation",
        "FedEx Express", "UPS Airlines", "Silk Way Airlines", "Atlas Air", "Polar Air Cargo",
        "Cargolux", "Kalitta Air", "Saudia Cargo", "Ethiopian Cargo", "Turkish Cargo",
        "Qatar Airways Cargo", "Emirates SkyCargo", "Lufthansa Cargo", "British Airways World Cargo",
        "AirBridgeCargo Airlines", "Aerologic", "China Cargo Airlines", "EVA Air Cargo",
        "Asiana Airlines Cargo", "ANA Cargo"
    ]


def get_destination_weather_info(city_name, travel_month):
    """
    Fetches current weather and a general "season" for a given city and month
    using OpenWeatherMap.
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "8599c5e729e2485698f83819252105":
        print("OpenWeatherMap API key is not set or is default. Using fallback season calculation.")
        return get_season_from_month(travel_month), "N/A", "N/A"  # Fallback

    try:
        # First, get geographic coordinates for the city (using country for broader search)
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={OPENWEATHER_API_KEY}"
        geo_response = requests.get(geo_url, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            print(f"Could not find coordinates for {city_name}. Using fallback season.")
            return get_season_from_month(travel_month), "N/A", "N/A"

        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']

        # Then, get current weather for the coordinates
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}"
        weather_response = requests.get(weather_url, timeout=10)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        temperature = weather_data['main']['temp']
        description = weather_data['weather'][0]['description'].capitalize()

        # Determine season based on temperature (simplified)
        if temperature < 0:
            season = "Extreme Winter (Below Freezing)"
        elif temperature < 10:  # Cold
            season = "Winter"
        elif temperature > 28:  # Hot
            season = "Summer"
        elif 10 <= temperature <= 20:
            season = "Moderate (Cool)"
        else:
            season = "Moderate (Warm)"

        return season, f"{temperature:.1f}°C", description

    except requests.exceptions.RequestException as e:
        print(f"Weather API error for {city_name}: {e}")
        messagebox.showwarning("API Warning",
                               f"Could not fetch real-time weather data for {city_name}. Using fallback season calculation.")
        return get_season_from_month(travel_month), "N/A", "N/A"
    except Exception as e:
        print(f"Error processing weather data for {city_name}: {e}")
        return get_season_from_month(travel_month), "N/A", "N/A"


def get_season_from_month(month):
    """Fallback function to determine season based solely on month (less accurate)."""
    if not month:
        return "Moderate"

    winter_months = ["December", "January", "February"]
    summer_months = ["June", "July", "August"]
    if month in winter_months:
        return "Winter"
    elif month in summer_months:
        return "Summer"
    else:
        return "Moderate"


# --------- Packing List Generator --------- #
# Separated common, male, female, seasonal, and purpose-specific items
# Each item is (item_name, count, bag_type) where bag_type is "C" (Carry-on) or "K" (Checked)
COMMON_ITEMS = {
    "Documents & Valuables": [("Passport & Visa", 1, "C"), ("Travel Insurance Documents", 1, "C"),
                              ("Local Currency / Forex Card", 1, "C"), ("Credit/Debit Cards", 1, "C"),
                              ("Flight & Accommodation Bookings", 1, "C"), ("ID Card / Driver's License", 1, "C")],
    "Electronics & Gadgets": [("Phone & Charger", 1, "C"), ("Power Bank", 1, "C"),
                              ("Universal Travel Adapter", 1, "C")],
    "Health & Personal Care (Carry-on)": [("Essential Prescription Medicines (original packaging)", 1, "C"),
                                          ("Basic First Aid Kit (small)", 1, "C"),
                                          ("Hand Sanitizer (travel size)", 1, "C")],
    "Health & Personal Care (Checked)": [("Shampoo & Conditioner", 1, "K"), ("Body Wash/Soap", 1, "K"),
                                         ("Toothbrush & Toothpaste", 1, "K"), ("Deodorant", 1, "K"),
                                         ("Moisturizer", 1, "K")],
    "Miscellaneous Essentials (Carry-on)": [("Small Backpack/Daypack", 1, "C"), ("Reusable Water Bottle", 1, "C"),
                                            ("Earplugs/Eye Mask", 1, "C")],
    "Miscellaneous Essentials (Checked)": [("Padlocks", 2, "K"), ("Laundry Bag", 1, "K")]
}

MALE_CLOTHING_BASE = [
    ("Shirts (T-shirts/Casual)", 4, "K"), ("Formal Shirts (if needed)", 2, "K"),
    ("Trousers/Jeans", 2, "K"), ("Shorts (if appropriate)", 1, "K"),
    ("Undergarments", 7, "K"), ("Socks", 7, "K"), ("Sleepwear", 1, "K"),
    ("Shaving Kit", 1, "K")
]

FEMALE_CLOTHING_BASE = [
    ("Tops/Blouses", 4, "K"), ("Dresses/Skirts (if preferred)", 2, "K"),
    ("Leggings/Jeans/Trousers", 2, "K"),
    ("Undergarments", 7, "K"), ("Socks/Stockings", 7, "K"), ("Sleepwear", 1, "K"),
    ("Sanitary Products", 7, "K"), ("Makeup Essentials", 1, "K"), ("Hairbrush/Comb", 1, "K")
]

UNSPECIFIED_CLOTHING_BASE = [
    ("Comfortable Tops", 4, "K"), ("Comfortable Bottoms", 2, "K"),
    ("Undergarments", 7, "K"), ("Socks", 7, "K"), ("Sleepwear", 1, "K"),
    ("Basic Toiletries", 1, "K")
]


def generate_packing_list(gender, duration_val, duration_unit, travel_month, purpose, destination_city_info):
    """Generates a comprehensive packing list based on user inputs."""
    try:
        duration = int(duration_val)
    except ValueError:
        duration = 7  # Default to 1 week if duration is invalid

    days = duration * {
        "Days": 1,
        "Weeks": 7,
        "Months": 30,
        "Years": 365
    }.get(duration_unit, 7)

    weather_season, temperature_info, weather_desc = destination_city_info

    # All items will be collected here as (item_name, count, bag_type)
    all_raw_items = []

    # Add common items
    for category, items in COMMON_ITEMS.items():
        all_raw_items.extend(items)

    # Add general footwear
    all_raw_items.append(("Comfortable Walking Shoes", 1, "K"))
    if "Summer" in weather_season or "Moderate" in weather_season:
        all_raw_items.append(("Sandals/Flip-flops", 1, "K"))
        all_raw_items.append(("Sunscreen", 1, "K"))  # Moved here as it's common for warm weather
    elif "Winter" in weather_season or "Freezing" in weather_season:
        all_raw_items.append(("Waterproof Boots", 1, "K"))

    # Gender-specific clothing (scaled by duration in weeks)
    base_clothing_count_weeks = max(days // 7, 1)  # Minimum 1 week's worth

    clothing_base_list = []
    if gender == "Male":
        clothing_base_list = MALE_CLOTHING_BASE
    elif gender == "Female":
        clothing_base_list = FEMALE_CLOTHING_BASE
    else:
        clothing_base_list = UNSPECIFIED_CLOTHING_BASE

    # Scale clothing items and add to all_raw_items
    for item, count, bag_type in clothing_base_list:
        all_raw_items.append((item, max(1, count * base_clothing_count_weeks), bag_type))

    # Seasonal clothing based on weather API info
    seasonal_items = []
    if weather_season == "Extreme Winter (Below Freezing)":
        seasonal_items = [
            ("Extreme Cold Weather Jacket", 1, "K"), ("Heavy Duty Thermal Wear", 2, "K"),
            ("Wool Sweaters/Fleeces", 3, "K"), ("Waterproof & Insulated Boots", 1, "K"),
            ("Winter Gloves/Mittens", 1, "K"), ("Woolen Hat/Balaclava", 1, "K"),
            ("Scarf", 1, "K"), ("Hand/Toe Warmers", 5, "C"), ("Snow Pants (if applicable)", 1, "K")
        ]
    elif weather_season == "Winter":
        seasonal_items = [
            ("Warm Winter Jacket/Coat", 1, "K"), ("Thermal Wear", min(3, base_clothing_count_weeks), "K"),
            ("Sweaters/Fleeces", min(3, base_clothing_count_weeks), "K"),
            ("Gloves", 1, "K"), ("Woolen Cap/Beanie", 1, "K"),
            ("Warm Socks (extra)", max(2, base_clothing_count_weeks * 2), "K")
        ]
    elif weather_season == "Summer":
        seasonal_items = [
            ("Sunglasses", 1, "C"), ("Hat/Cap", 1, "K"),
            ("Lightweight/Breathable Clothes (additional)", base_clothing_count_weeks * 3, "K"),
            ("Swimwear", min(2, base_clothing_count_weeks), "K"),
        ]
    elif "Moderate" in weather_season:  # Includes Cool and Warm
        seasonal_items = [
            ("Light Jacket/Cardigan", 1, "K"),
            ("Umbrella/Compact Raincoat", 1, "C"),
            ("Long-sleeved Shirts", base_clothing_count_weeks * 2, "K")
        ]

    all_raw_items.extend(seasonal_items)

    # Purpose specific items
    purpose_lower = purpose.lower()
    purpose_specific_items = []
    if "study" in purpose_lower or "exchange program" in purpose_lower or "language course" in purpose_lower:
        purpose_specific_items = [
            ("University Admission & Academic Documents", 1, "C"),
            ("Stationery (Notebooks, Pens)", 1, "K"),
            ("Laptop & Accessories (if not already listed)", 1, "C"),
            ("Textbooks/Reading Material", "As needed", "K")
        ]
    elif "business" in purpose_lower or "conference" in purpose_lower:
        purpose_specific_items = [
            ("Business Attire (Suits, Formal Shirts/Blouses)", min(5, base_clothing_count_weeks * 3), "K"),
            ("Formal Shoes", 1, "K"),
            ("Presentation Materials/Documents", "As needed", "C"),
            ("Business Cards", 1, "C")
        ]
    elif "vacation" in purpose_lower or "cultural program" in purpose_lower or "family visit" in purpose_lower or "adventure travel" in purpose_lower or "religious pilgrimage" in purpose_lower:
        purpose_specific_items = [
            ("Camera & Extra Battery/Memory Card", 1, "C"),
            ("Travel Guidebook/Maps", 1, "C"),
        ]
        # Only add if not already covered by general footwear
        if not any("Walking Shoes" in item[0] for item in all_raw_items):
            purpose_specific_items.append(("Comfortable Walking Shoes", 1, "K"))

        if "adventure" in purpose_lower:
            purpose_specific_items.extend([("Hiking Boots", 1, "K"), ("Outdoor Gear", 1, "K")])
        if "religious" in purpose_lower:
            purpose_specific_items.append(("Appropriate Religious Attire", 1, "K"))
    elif "internship" in purpose_lower:
        purpose_specific_items = [
            ("Work-appropriate Clothing", min(5, base_clothing_count_weeks * 3), "K"),
            ("Professional Documents (Resume, Offer Letter)", 1, "C"),
            ("Laptop (if not already listed)", 1, "C")
        ]
    elif "volunteering" in purpose_lower:
        purpose_specific_items = [
            ("Durable Work Clothes", 3, "K"),
            ("Work Gloves", 1, "K"),
            ("Sturdy Footwear", 1, "K"),
            ("Project-specific documents", "As needed", "C")
        ]
    elif "medical travel" in purpose_lower:
        purpose_specific_items = [
            ("Medical Records/History", 1, "C"), ("Comfortable Clothing (loose)", 3, "K"),
            ("Specialist Medications/Supplies", 1, "C")
        ]
    elif "other" in purpose_lower:
        if custom_purpose.get().strip():
            purpose_specific_items.append((custom_purpose.get().title(), 1, "K"))

    all_raw_items.extend(purpose_specific_items)

    # Estimate weight roughly: base + clothes + electronics + misc.
    # PROFESSIONAL NOTE: For better accuracy, assign weights to *each* item.
    est_weight = 5  # Base weight for bag itself + essentials
    est_weight += (days // 7) * 5  # ~5 kg per week of clothes
    est_weight += 3  # Electronics
    est_weight += 2  # Toiletries and shoes

    # Add weight for seasonal items if heavy
    if "Winter" in weather_season or "Freezing" in weather_season:
        est_weight += 5
    elif "Summer" in weather_season:
        est_weight += 1

    # Separating lists for checked and carry-on, and grouping by category for display
    final_packing_lists = {
        "Carry-On Bag": {},
        "Checked Baggage": {}
    }

    # Define a mapping for cleaner display categories
    category_map = {
        "Documents & Valuables": "Important Documents & Valuables",
        "Electronics & Gadgets": "Essential Electronics & Gadgets",
        "Health & Personal Care (Carry-on)": "Health & Personal Care (Carry-On)",
        "Health & Personal Care (Checked)": "Health & Personal Care (Checked)",
        "Miscellaneous Essentials (Carry-on)": "Miscellaneous Essentials (Carry-On)",
        "Miscellaneous Essentials (Checked)": "Miscellaneous Essentials (Checked)",
        "Clothing": "Clothing (Main Luggage)",  # Default for gender-specific clothing
        "Footwear": "Footwear",
        "Seasonal & Weather Specific": "Seasonal & Weather Specific",
        "Purpose-Specific Items": "Purpose-Specific Items",
    }

    # Process all_raw_items to populate final_packing_lists
    for item_name, count, bag_type in all_raw_items:
        # Determine the original category for grouping
        original_category = "Other"

        # Check COMMON_ITEMS
        for cat, items in COMMON_ITEMS.items():
            if any(i[0] == item_name for i in items):
                original_category = cat
                break

        # Check gender-specific clothing
        if original_category == "Other" and any(
                item_name == i[0] for i in MALE_CLOTHING_BASE + FEMALE_CLOTHING_BASE + UNSPECIFIED_CLOTHING_BASE):
            original_category = "Clothing"

        # Check seasonal items (re-generate a temporary list for checking)
        temp_seasonal_items = []
        if weather_season == "Extreme Winter (Below Freezing)":
            temp_seasonal_items = [("Extreme Cold Weather Jacket", 1, "K"), ("Heavy Duty Thermal Wear", 2, "K"),
                                   ("Wool Sweaters/Fleeces", 3, "K"), ("Waterproof & Insulated Boots", 1, "K"),
                                   ("Winter Gloves/Mittens", 1, "K"), ("Woolen Hat/Balaclava", 1, "K"),
                                   ("Scarf", 1, "K"), ("Hand/Toe Warmers", 5, "C"),
                                   ("Snow Pants (if applicable)", 1, "K")]
        elif weather_season == "Winter":
            temp_seasonal_items = [("Warm Winter Jacket/Coat", 1, "K"),
                                   ("Thermal Wear", min(3, base_clothing_count_weeks), "K"),
                                   ("Sweaters/Fleeces", min(3, base_clothing_count_weeks), "K"), ("Gloves", 1, "K"),
                                   ("Woolen Cap/Beanie", 1, "K"),
                                   ("Warm Socks (extra)", max(2, base_clothing_count_weeks * 2), "K")]
        elif weather_season == "Summer":
            temp_seasonal_items = [("Sunglasses", 1, "C"), ("Hat/Cap", 1, "K"),
                                   ("Lightweight/Breathable Clothes (additional)", base_clothing_count_weeks * 3, "K"),
                                   ("Swimwear", min(2, base_clothing_count_weeks), "K")]
        elif "Moderate" in weather_season:
            temp_seasonal_items = [("Light Jacket/Cardigan", 1, "K"), ("Umbrella/Compact Raincoat", 1, "C"),
                                   ("Long-sleeved Shirts", base_clothing_count_weeks * 2, "K")]

        if original_category == "Other" and any(item_name == i[0] for i in temp_seasonal_items):
            original_category = "Seasonal & Weather Specific"

        # Check purpose-specific items (re-generate a temporary list for checking)
        temp_purpose_specific_items = []
        if "study" in purpose_lower or "exchange program" in purpose_lower or "language course" in purpose_lower:
            temp_purpose_specific_items = [("University Admission & Academic Documents", 1, "C"),
                                           ("Stationery (Notebooks, Pens)", 1, "K"),
                                           ("Laptop & Accessories (if not already listed)", 1, "C"),
                                           ("Textbooks/Reading Material", "As needed", "K")]
        elif "business" in purpose_lower or "conference" in purpose_lower:
            temp_purpose_specific_items = [
                ("Business Attire (Suits, Formal Shirts/Blouses)", min(5, base_clothing_count_weeks * 3), "K"),
                ("Formal Shoes", 1, "K"), ("Presentation Materials/Documents", "As needed", "C"),
                ("Business Cards", 1, "C")]
        elif "vacation" in purpose_lower or "cultural program" in purpose_lower or "family visit" in purpose_lower or "adventure travel" in purpose_lower or "religious pilgrimage" in purpose_lower:
            temp_purpose_specific_items = [("Camera & Extra Battery/Memory Card", 1, "C"),
                                           ("Travel Guidebook/Maps", 1, "C")]
            if not any("Walking Shoes" in item[0] for item in all_raw_items):
                temp_purpose_specific_items.append(("Comfortable Walking Shoes", 1, "K"))
            if "adventure" in purpose_lower:
                temp_purpose_specific_items.extend([("Hiking Boots", 1, "K"), ("Outdoor Gear", 1, "K")])
            if "religious" in purpose_lower:
                temp_purpose_specific_items.append(("Appropriate Religious Attire", 1, "K"))
        elif "internship" in purpose_lower:
            temp_purpose_specific_items = [("Work-appropriate Clothing", min(5, base_clothing_count_weeks * 3), "K"),
                                           ("Professional Documents (Resume, Offer Letter)", 1, "C"),
                                           ("Laptop (if not already listed)", 1, "C")]
        elif "volunteering" in purpose_lower:
            temp_purpose_specific_items = [("Durable Work Clothes", 3, "K"), ("Work Gloves", 1, "K"),
                                           ("Sturdy Footwear", 1, "K"),
                                           ("Project-specific documents", "As needed", "C")]
        elif "medical travel" in purpose_lower:
            temp_purpose_specific_items = [("Medical Records/History", 1, "C"),
                                           ("Comfortable Clothing (loose)", 3, "K"),
                                           ("Specialist Medications/Supplies", 1, "C")]
        elif "other" in purpose_lower and custom_purpose.get().strip():
            temp_purpose_specific_items.append((custom_purpose.get().title(), 1, "K"))

        if original_category == "Other" and any(item_name == i[0] for i in temp_purpose_specific_items):
            original_category = "Purpose-Specific Items"

        # Handle Footwear category specifically
        if item_name in ["Comfortable Walking Shoes", "Sandals/Flip-flops", "Waterproof Boots", "Hiking Boots",
                         "Sturdy Footwear", "Formal Shoes"]:
            original_category = "Footwear"

        # Map to display category
        display_category = category_map.get(original_category, "Other Items")

        # Add to the correct bag type's dictionary
        if bag_type == "C":
            final_packing_lists["Carry-On Bag"].setdefault(display_category, []).append((item_name, count))
        elif bag_type == "K":
            final_packing_lists["Checked Baggage"].setdefault(display_category, []).append((item_name, count))

    return final_packing_lists, est_weight, weather_season, temperature_info, weather_desc


# --------- Airline baggage allowances (More detailed data for better analysis) --------- #
# Nested dictionary: Airline -> Class -> (checked_weight_kg, checked_pieces, carry_on_weight_kg, carry_on_pieces)
baggage_rules = {
    "Lufthansa": {"Economy": (23, 1, 8, 1), "Business": (32, 2, 8, 2), "First": (32, 3, 8, 2)},
    "Emirates": {"Economy": (23, 1, 7, 1), "Business": (32, 2, 7, 2), "First": (32, 2, 7, 2)},
    "Qatar Airways": {"Economy": (30, 1, 7, 1), "Business": (40, 2, 15, 1), "First": (50, 2, 15, 1)},
    "Air India": {"Economy": (25, 1, 8, 1), "Business": (35, 2, 12, 1), "First": (40, 2, 12, 1)},
    "British Airways": {"Economy": (23, 1, 23, 1), "Business": (32, 2, 23, 2), "First": (32, 3, 23, 3)},
    "Delta Air Lines": {"Economy": (23, 1, 7, 1), "Business": (32, 2, 7, 1), "First": (32, 3, 7, 1)},
    "American Airlines": {"Economy": (23, 1, 7, 1), "Business": (32, 2, 7, 1), "First": (32, 3, 7, 1)},
    "Etihad Airways": {"Economy": (23, 1, 7, 1), "Business": (32, 2, 12, 1), "First": (32, 2, 12, 1)},
    "Turkish Airlines": {"Economy": (30, 1, 8, 1), "Business": (40, 2, 8, 2), "First": (50, 2, 8, 2)},
    "Singapore Airlines": {"Economy": (30, 1, 7, 1), "Business": (40, 2, 7, 2), "First": (50, 2, 7, 2)},
    "Air France": {"Economy": (23, 1, 12, 1), "Business": (32, 2, 18, 1), "First": (32, 3, 18, 2)},
    "KLM Royal Dutch Airlines": {"Economy": (23, 1, 12, 1), "Business": (32, 2, 18, 1), "First": (32, 3, 18, 2)},
    "SWISS": {"Economy": (23, 1, 8, 1), "Business": (32, 2, 8, 2), "First": (32, 3, 8, 2)},
    "ANA - All Nippon Airways": {"Economy": (23, 1, 10, 1), "Business": (32, 2, 10, 2), "First": (32, 3, 10, 3)},
    "Japan Airlines": {"Economy": (23, 1, 10, 1), "Business": (32, 2, 10, 2), "First": (32, 3, 10, 3)},
    "Korean Air": {"Economy": (23, 1, 10, 1), "Business": (32, 2, 12, 1), "First": (32, 3, 12, 1)},
    "Cathay Pacific": {"Economy": (23, 1, 7, 1), "Business": (32, 2, 10, 1), "First": (32, 3, 15, 1)},
    "Qantas": {"Economy": (23, 1, 7, 1), "Business": (32, 2, 10, 2), "First": (32, 3, 10, 2)},
    "Virgin Atlantic": {"Economy": (23, 1, 10, 1), "Business": (32, 2, 12, 1), "First": (32, 3, 12, 2)},
    "United Airlines": {"Economy": (23, 1, 7, 1), "Business": (32, 2, 7, 1), "First": (32, 3, 7, 1)},
    "Southwest Airlines": {"Economy": (23, 2, 0, 1), "Business": (23, 2, 0, 1), "First": (23, 2, 0, 1)},
    "Ryanair": {"Economy": (10, 0, 10, 1), "Business": (20, 1, 10, 2)},
    "EasyJet": {"Economy": (15, 0, 15, 1), "Business": (23, 1, 15, 1)},
    "Spirit Airlines": {"Economy": (18, 0, 0, 1), "Business": (18, 0, 0, 1)},
    "IndiGo": {"Economy": (15, 1, 7, 1), "Business": (20, 1, 7, 1)},
    "SpiceJet": {"Economy": (15, 1, 7, 1), "Business": (20, 1, 7, 1)},
    "Vistara": {"Economy": (20, 1, 7, 1), "Business": (30, 1, 12, 1)},
    "Air Canada": {"Economy": (23, 1, 10, 1), "Business": (32, 2, 10, 2), "First": (32, 3, 10, 2)},
    "LATAM Airlines": {"Economy": (23, 1, 8, 1), "Business": (32, 2, 16, 1), "First": (32, 3, 16, 2)},
    "Aeromexico": {"Economy": (23, 1, 10, 1), "Business": (32, 2, 10, 2), "First": (32, 3, 10, 2)},
    "EVA Air": {"Economy": (23, 1, 7, 1), "Business": (32, 2, 10, 1), "First": (32, 3, 15, 1)},
    "Finnair": {"Economy": (23, 1, 8, 1), "Business": (32, 2, 10, 1), "First": (32, 3, 10, 1)},
    "SAS - Scandinavian Airlines": {"Economy": (23, 1, 8, 1), "Business": (32, 2, 8, 2), "First": (32, 3, 8, 2)},
    "Alaska Airlines": {"Economy": (23, 1, 7, 1), "Business": (32, 2, 7, 1), "First": (32, 3, 7, 1)},
    "JetBlue Airways": {"Economy": (23, 0, 10, 1), "Business": (23, 1, 15, 1)},
    "Wizz Air": {"Economy": (10, 0, 10, 1), "Business": (20, 1, 10, 2)},
    # Cargo airlines often have different rules, usually defined by freight forwarders/contracts
    "Nippon Cargo Airlines": {"Cargo": (9999, 1, 0, 0)},  # Placeholder for cargo - rules vary greatly
    "Korean Air Cargo": {"Cargo": (9999, 1, 0, 0)},
    "Air China Cargo": {"Cargo": (9999, 1, 0, 0)},
    "DHL Aviation": {"Cargo": (9999, 1, 0, 0)},
    "FedEx Express": {"Cargo": (9999, 1, 0, 0)},
    "UPS Airlines": {"Cargo": (9999, 1, 0, 0)},
}

# --------- GUI Setup --------- #

root = tk.Tk()
root.title("PackWise - Smart Packing Assistant")
root.geometry("750x850")  # Adjusted size
root.resizable(False, False)

# Styling
style = ttk.Style(root)
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 10))
style.configure("TButton", font=("Arial", 10, "bold"))
style.configure("TCombobox", font=("Arial", 10))
style.configure("TEntry", font=("Arial", 10))
style.configure("Header.TLabel", font=("Arial", 22, "bold"), foreground="#1e3a5f")  # Darker blue
style.configure("ResultHeader.TLabel", font=("Arial", 18, "bold"), foreground="#1e3a5f")
style.configure("Category.TLabel", font=("Arial", 11, "bold"), foreground="#4a4a4a")
style.configure("Info.TLabel", font=("Arial", 10), foreground="#333333")
style.configure("Red.TLabel", foreground="red")
style.configure("Green.TLabel", foreground="green")

title_label = ttk.Label(root, text="PackWise", style="Header.TLabel")
title_label.pack(pady=15)

# Notebook (Tabbed Interface)
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True, fill="both", padx=20)

# Input Tab
input_frame = ttk.Frame(notebook, padding="25 25 25 25", relief="flat")
notebook.add(input_frame, text=" ✈️ Your Travel Details ")

# Result Tab (initially empty)
result_frame = ttk.Frame(notebook, padding="25 25 25 25", relief="flat")
notebook.add(result_frame, text=" 📝 Your Packing List ")

# Variables
current_country = tk.StringVar()
destination_country = tk.StringVar()
duration_value = tk.StringVar()
duration_unit = tk.StringVar(value="Weeks")
travel_month = tk.StringVar()
purpose = tk.StringVar()
custom_purpose = tk.StringVar()
airline = tk.StringVar()
gender = tk.StringVar()
travel_class = tk.StringVar(value="Economy")
user_baggage_weight = tk.StringVar()

# Dropdown options
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
duration_units = ["Days", "Weeks", "Months", "Years"]
purpose_options = [
    "Study", "Internship", "Exchange Program", "Vacation", "Business",
    "Conference", "Language Course", "Cultural Program", "Volunteering",
    "Family Visit", "Medical Travel", "Adventure Travel", "Religious Pilgrimage", "Other"
]
gender_options = ["Male", "Female", "Other"]
travel_class_options = ["Economy", "Business", "First", "Cargo"]  # Added Cargo for airline classification


# Load data for comboboxes (run on a thread to avoid UI freeze if API is slow)
def load_initial_data():
    global countries, airlines
    try:
        countries = get_countries()
        airlines = get_airlines()
        # Update comboboxes on the main thread after data is loaded
        root.after(100, lambda: [
            country_combo.set_completion_list(countries),
            destination_combo.set_completion_list(countries),
            airline_combo.set_completion_list(airlines)
        ])
    except Exception as e:
        print(f"Error loading initial data: {e}")
        messagebox.showerror("Initialization Error", "Failed to load country/airline data. Please restart application.")


# Start data loading in a separate thread
threading.Thread(target=load_initial_data).start()


# Helper functions to create widgets
def create_autocomplete(parent_frame, label_text, variable, values, row, col_span=1):
    ttk.Label(parent_frame, text=label_text).grid(row=row, column=0, sticky="w", pady=5, padx=5)
    combo = AutocompleteCombobox(parent_frame, textvariable=variable, width=38)
    combo.set_completion_list(values)  # Set initial empty list until data loads
    combo.grid(row=row, column=1, columnspan=col_span, pady=5, padx=5, sticky="ew")
    return combo


def create_dropdown(parent_frame, label_text, variable, values, row, col_span=1):
    ttk.Label(parent_frame, text=label_text).grid(row=row, column=0, sticky="w", pady=5, padx=5)
    combo = ttk.Combobox(parent_frame, textvariable=variable, values=values, width=38, state="readonly")
    combo.grid(row=row, column=1, columnspan=col_span, pady=5, padx=5, sticky="ew")
    return combo


# Build form fields within input_frame
country_combo = create_autocomplete(input_frame, "Current Country:", current_country, [], 0)
destination_combo = create_autocomplete(input_frame, "Destination Country:", destination_country, [], 1)

# Duration (value + unit)
ttk.Label(input_frame, text="Duration of Stay:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
ttk.Entry(input_frame, textvariable=duration_value, width=19).grid(row=2, column=1, sticky="w", pady=5, padx=5)
ttk.Combobox(input_frame, textvariable=duration_unit, values=duration_units, width=19, state="readonly").grid(row=2,
                                                                                                              column=1,
                                                                                                              sticky="e",
                                                                                                              pady=5,
                                                                                                              padx=5)

create_dropdown(input_frame, "Travel Month:", travel_month, months, 3)
airline_combo = create_autocomplete(input_frame, "Airline:", airline, [], 4)  # Initially empty
create_dropdown(input_frame, "Travel Class:", travel_class, travel_class_options, 5)
create_dropdown(input_frame, "Gender:", gender, gender_options, 6)

# Purpose dropdown with 'Other' option
ttk.Label(input_frame, text="Purpose of Travel:").grid(row=7, column=0, sticky="w", pady=5, padx=5)
purpose_menu = ttk.Combobox(input_frame, textvariable=purpose, values=purpose_options, width=38, state="readonly")
purpose_menu.grid(row=7, column=1, pady=5, padx=5, sticky="ew")

custom_entry_label = ttk.Label(input_frame, text="Specify Purpose:")
custom_entry_label.grid(row=8, column=0, sticky="w", pady=5, padx=5)
custom_entry = ttk.Entry(input_frame, textvariable=custom_purpose, width=38)
custom_entry.grid(row=8, column=1, pady=5, padx=5, sticky="ew")
custom_entry_label.grid_remove()
custom_entry.grid_remove()


def toggle_custom_purpose(event=None):
    if purpose.get() == "Other":
        custom_entry_label.grid()
        custom_entry.grid()
    else:
        custom_entry_label.grid_remove()
        custom_entry.grid_remove()


purpose_menu.bind("<<ComboboxSelected>>", toggle_custom_purpose)
toggle_custom_purpose()

# User baggage weight input (for overall checked baggage)
ttk.Label(input_frame, text="Your Checked Baggage (kg):").grid(row=9, column=0, sticky="w", pady=5, padx=5)
user_baggage_entry = ttk.Entry(input_frame, textvariable=user_baggage_weight, width=38)
user_baggage_entry.grid(row=9, column=1, pady=5, padx=5, sticky="ew")
ttk.Label(input_frame, text="(Leave blank to use airline's standard)").grid(row=10, column=1, sticky="w", padx=5)

# Progress indicator
progress_label = ttk.Label(input_frame, text="", foreground="blue")
progress_label.grid(row=11, columnspan=2, pady=10)


# --------- Submit and Display --------- #
def generate_list_in_background():
    """Starts the packing list generation in a separate thread."""
    progress_label.config(text="Generating list, please wait...", foreground="blue")
    submit_btn.config(state="disabled")
    # Clear previous results before generating new ones
    clear_result_frame()

    threading.Thread(target=_generate_list_task).start()


def _generate_list_task():
    """The actual task to run in a background thread."""
    try:
        # Input validation
        if not destination_country.get() or not duration_value.get().isdigit() or not travel_month.get() \
                or not airline.get() or not gender.get():
            root.after(0, lambda: messagebox.showwarning("Missing Information",
                                                         "Please fill in all required fields (Destination, Duration, Month, Airline, Gender)."))
            return

        final_purpose = custom_purpose.get().strip() if purpose.get() == "Other" else purpose.get().strip()
        if purpose.get() == "Other" and not final_purpose:
            root.after(0, lambda: messagebox.showwarning("Missing Information",
                                                         "Please specify your travel purpose or choose from the list."))
            return

        dest_city = destination_country.get()
        weather_info = get_destination_weather_info(dest_city, travel_month.get())

        packing_lists_separated, est_weight, actual_season, temp_info, weather_desc = generate_packing_list(
            gender.get(), duration_value.get(), duration_unit.get(),
            travel_month.get(), final_purpose, weather_info
        )

        # Get airline baggage allowance by class
        airline_name = airline.get()
        t_class = travel_class.get()

        checked_allowance_per_bag, checked_pieces, carry_on_weight, carry_on_pieces = 23, 1, 8, 1  # Defaults

        if airline_name in baggage_rules and t_class in baggage_rules[airline_name]:
            checked_allowance_per_bag, checked_pieces, carry_on_weight, carry_on_pieces = baggage_rules[airline_name][
                t_class]
        else:
            root.after(0, lambda: messagebox.showinfo("Airline Baggage Info",
                                                      f"Baggage rules for {airline_name} ({t_class}) not found in database. Using standard default rules (23kg checked, 8kg carry-on)."))

        # User's stated baggage allowance
        user_allowance_checked = None
        if user_baggage_weight.get().strip():
            try:
                user_allowance_checked = float(user_baggage_weight.get())
            except ValueError:
                root.after(0, lambda: messagebox.showwarning("Input Error",
                                                             "Invalid baggage weight entered. Please enter a number in kg."))
                return

        total_standard_checked_allowed_weight = checked_allowance_per_bag * checked_pieces
        comparison_allowance = user_allowance_checked if user_allowance_checked is not None else total_standard_checked_allowed_weight

        overweight_warning = ""
        if est_weight > comparison_allowance:
            overweight_warning = f"⚠️ **WARNING: Estimated packing weight ({est_weight:.1f} kg) EXCEEDS** your {'stated' if user_allowance_checked is not None else 'airline standard'} checked baggage allowance ({comparison_allowance:.1f} kg)!"
            if user_allowance_checked is not None and user_allowance_checked < total_standard_checked_allowed_weight:
                overweight_warning += f"\n   (Airline standard for {airline_name} {t_class} is {total_standard_checked_allowed_weight} kg for checked bags.)"
            elif user_allowance_checked is None:
                overweight_warning += f"\n   Consider reducing items or checking airline's paid baggage options."
        else:
            overweight_warning = f"✅ Your estimated packing weight ({est_weight:.1f} kg) fits comfortably within your {'stated' if user_allowance_checked is not None else 'airline standard'} checked baggage allowance ({comparison_allowance:.1f} kg)."

        # Call the display function on the main thread
        root.after(0, lambda: display_results(
            packing_lists_separated, est_weight, airline_name, t_class,
            checked_allowance_per_bag, checked_pieces, carry_on_weight, carry_on_pieces,
            user_allowance_checked, total_standard_checked_allowed_weight,
            overweight_warning, actual_season, temp_info, weather_desc
        ))
    except Exception as e:
        # Fix for NameError: pass 'e' as an argument to the lambda
        root.after(0, lambda err=e: messagebox.showerror("Processing Error",
                                                         f"An unexpected error occurred: {err}\nPlease try again or check your inputs."))
    finally:
        root.after(0, lambda: [progress_label.config(text=""), submit_btn.config(state="normal")])


def clear_result_frame():
    """Clears all widgets from the result frame."""
    for widget in result_frame.winfo_children():
        widget.destroy()


def display_results(packing_lists_separated, est_weight, airline_name, t_class,
                    checked_allowance_per_bag, checked_pieces, carry_on_weight, carry_on_pieces,
                    user_allowance_checked, total_standard_checked_allowed_weight,
                    overweight_warning, actual_season, temp_info, weather_desc):
    """Displays the results in the result tab."""
    clear_result_frame()  # Clear previous content

    # Use a ScrolledText for the packing list to handle long output
    packing_text_widget = tk.Text(result_frame, wrap="word", width=75, height=25, font=("Arial", 10),
                                  padx=10, pady=10, relief="flat", background="#f9f9f9")
    packing_text_widget.pack(padx=10, pady=10, fill="both", expand=True)

    # Configure text tags
    packing_text_widget.tag_configure("header", font=("Arial", 12, "bold"), foreground="#1e3a5f", spacing1=5,
                                      spacing3=5)
    packing_text_widget.tag_configure("subheader", font=("Arial", 11, "bold"), foreground="#333333", spacing1=3,
                                      spacing3=3)
    packing_text_widget.tag_configure("item", font=("Arial", 10), lmargin1=20, lmargin2=20, spacing1=1)
    packing_text_widget.tag_configure("info_bold", font=("Arial", 10, "bold"), foreground="#333333")
    packing_text_widget.tag_configure("warning", foreground="red", font=("Arial", 10, "bold"))
    packing_text_widget.tag_configure("success", foreground="green", font=("Arial", 10, "bold"))
    packing_text_widget.tag_configure("summary_header", font=("Arial", 13, "bold"), foreground="#1e3a5f", spacing1=10,
                                      spacing3=5)

    # Insert content
    packing_text_widget.insert("end", "YOUR SMART PACKING LIST\n\n", "header")

    # Carry-On List
    packing_text_widget.insert("end", "👜 CARRY-ON BAG\n", "subheader")
    if packing_lists_separated["Carry-On Bag"]:
        # Iterate through categories and then items
        for category, items_in_category in packing_lists_separated["Carry-On Bag"].items():
            packing_text_widget.insert("end", f"  • {category}:\n", "info_bold")
            for item_name, count in items_in_category:  # This loop now correctly expects 2-element tuples
                packing_text_widget.insert("end", f"    - {item_name} (x{count})\n", "item")
        packing_text_widget.insert("end", "\n")
    else:
        packing_text_widget.insert("end", "  (No specific items recommended for carry-on beyond essentials)\n\n",
                                   "item")

    # Checked Baggage List
    packing_text_widget.insert("end", "🧳 CHECKED BAGGAGE\n", "subheader")
    if packing_lists_separated["Checked Baggage"]:
        # Iterate through categories and then items
        for category, items_in_category in packing_lists_separated["Checked Baggage"].items():
            packing_text_widget.insert("end", f"  • {category}:\n", "info_bold")
            for item_name, count in items_in_category:  # This loop now correctly expects 2-element tuples
                packing_text_widget.insert("end", f"    - {item_name} (x{count})\n", "item")
        packing_text_widget.insert("end", "\n")
    else:
        packing_text_widget.insert("end", "  (No specific items recommended for checked baggage)\n\n", "item")

    packing_text_widget.insert("end", "--- TRAVEL & BAGGAGE SUMMARY ---\n\n", "summary_header")
    packing_text_widget.insert("end", f"✈️ Airline: {airline_name} | Class: {t_class}\n", "item")
    packing_text_widget.insert("end",
                               f"🌡️ Destination Weather ({destination_country.get()}): {actual_season} ({temp_info}, {weather_desc})\n",
                               "item")
    packing_text_widget.insert("end", f"🎒 Estimated Total Luggage Weight: {est_weight:.1f} kg\n\n", "info_bold")

    packing_text_widget.insert("end",
                               f"🛄 Airline Checked Baggage Allowance: {checked_pieces} piece(s) at {checked_allowance_per_bag} kg each. Total: {total_standard_checked_allowed_weight} kg.\n",
                               "item")
    packing_text_widget.insert("end",
                               f"🧳 Airline Carry-On Allowance: {carry_on_pieces} piece(s) at {carry_on_weight} kg each.\n\n",
                               "item")

    if user_allowance_checked is not None:
        packing_text_widget.insert("end",
                                   f"👤 Your Stated Checked Baggage Allowance: {user_allowance_checked:.1f} kg\n",
                                   "item")

    if "WARNING" in overweight_warning:
        packing_text_widget.insert("end", overweight_warning + "\n", "warning")
    else:
        packing_text_widget.insert("end", overweight_warning + "\n", "success")

    packing_text_widget.config(state="disabled")  # Make text box read-only

    # Add Print/Export buttons
    export_frame = ttk.Frame(result_frame)
    export_frame.pack(pady=10)

    ttk.Button(export_frame, text="Export to Text File",
               command=lambda: export_packing_list(packing_text_widget.get("1.0", "end-1c"))).pack(side="left", padx=5)
    ttk.Button(export_frame, text="Print (Not Implemented)", state="disabled").pack(side="left",
                                                                                    padx=5)  # Printing is OS/platform specific and complex for general Python

    # Switch to the result tab
    notebook.select(result_frame)


def export_packing_list(content):
    """Exports the packing list content to a text file."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        title="Save Packing List"
    )
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                # Remove markdown-like formatting for plain text export
                plain_content = content.replace("**", "").replace("---", "").replace("📂 ", "").replace("🎒 ",
                                                                                                        "").replace(
                    "✈️ ", "").replace("🌡️ ", "").replace("🛄 ", "").replace("🧳 ", "").replace("👤 ", "").replace(
                    "✅ ", "").replace("⚠️ ", "").replace("• ", "")
                f.write(plain_content)
            messagebox.showinfo("Export Successful", f"Packing list saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save file: {e}")


# Submit Button
submit_btn = ttk.Button(input_frame, text="Generate Packing List", command=generate_list_in_background, style="TButton")
submit_btn.grid(row=12, columnspan=2, pady=20)

root.mainloop()