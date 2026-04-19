# Planwise
PLANWISE is a smart desktop application that helps travelers generate a personalized packing list based on their trip details. It uses real-time APIs, intelligent logic, and user inputs to recommend what to pack while ensuring baggage limits are not exceeded.
The application is built using Python (Tkinter GUI) and integrates external APIs to provide a smarter travel planning experience.

🚀 Key Features
🎯 Personalized Packing List
Generates packing items based on:
Gender
Duration of stay
Travel purpose
Destination weather

🌦️ Weather Integration
Uses OpenWeather API to:
Fetch real-time temperature
Determine travel season
Adjust packing recommendations accordingly
🌍 Smart Country Selection
Fetches country list dynamically via API
Autocomplete-enabled dropdown for better UX
✈️ Airline Baggage Analysis
Supports multiple airlines and classes
Calculates:
Checked baggage allowance
Carry-on limits
Compares with estimated luggage weight
⚖️ Weight Estimation & Alerts
Estimates total luggage weight
Provides:
✅ Safe packing confirmation
⚠️ Overweight warnings
🧳 Categorized Packing Lists

Automatically organizes items into:

Carry-On Bag
Checked Baggage
Categories like:
Documents
Clothing
Electronics
Seasonal items
Purpose-specific items
📤 Export Feature
Export packing list as a .txt file

🧠 How It Works

The system follows this workflow:

User inputs travel details
Fetches:
Country data
Weather information
Applies intelligent rules to:
Generate packing items
Adjust based on season & purpose
Estimates baggage weight
Compares with airline limits
Displays final packing plan

📄 Core implementation:

⚙️ Technologies Used
🐍 Python
🖼️ Tkinter (GUI)
🌐 Requests (API calls)
📊 JSON processing
🧵 Threading (for smooth UI experience)
🔌 APIs Used
🌍 RestCountries API – Fetch country list
🌦️ OpenWeather API – Weather data

🛠️ Installation & Setup
Clone the repository:
git clone https://github.com/your-username/planwise.git
Navigate to project folder:
cd planwise
Install dependencies:
pip install requests
Run the application:
python main.py

📊 Example Use Case
User selects:
Destination: Germany
Duration: 2 weeks
Purpose: Vacation
Airline: Lufthansa

👉 PLANWISE will:

Detect weather (e.g., winter)
Suggest warm clothing
Add travel essentials
Estimate luggage weight
Check airline baggage limits

🧠 Future Improvements
🌐 Web or mobile version
🤖 AI-based recommendation system
📱 Integration with travel booking platforms
📊 More accurate weight prediction
🧾 PDF export option

👨‍💻 Author
Tushar Pareek
