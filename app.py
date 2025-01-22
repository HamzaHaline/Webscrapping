# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
from geopy.distance import geodesic
from datetime import datetime

# Load models and preprocessors
classic_model = joblib.load('best_xgb_model.pkl')
eco_model = joblib.load('best_xgb_model_with_emissions.pkl')
classic_preprocessor = joblib.load('classic_preprocessor.pkl')
eco_preprocessor = joblib.load('eco_preprocessor.pkl')
airline_columns = joblib.load('airline_columns.pkl')  # List of airline columns

# Airport coordinates for distance calculations
airport_coordinates = {
    'LHR': (51.4700, -0.4543),  # London Heathrow, United Kingdom
    'JFK': (40.6413, -73.7781),  # John F. Kennedy International, New York, USA
    'HND': (35.5494, 139.7798),  # Tokyo Haneda, Japan
    'DXB': (25.2532, 55.3657),  # Dubai International, United Arab Emirates
    'SIN': (1.3644, 103.9915),  # Singapore Changi, Singapore
    'SYD': (-33.9399, 151.1753),  # Sydney Kingsford Smith, Australia
    'GRU': (-23.4356, -46.4731),  # São Paulo-Guarulhos, Brazil
    'PEK': (40.0799, 116.6031),  # Beijing Capital International, China
    'JNB': (-26.1338, 28.2420),  # O.R. Tambo International, Johannesburg, South Africa
    'LAX': (33.9416, -118.4085),  # Los Angeles International, USA
    'FRA': (50.0379, 8.5622),  # Frankfurt am Main Airport, Germany
    'AMS': (52.3105, 4.7683),  # Amsterdam Airport Schiphol, Netherlands
    'MAD': (40.4722, -3.5638),  # Adolfo Suárez Madrid–Barajas, Spain
    'FCO': (41.7999, 12.2462),  # Leonardo da Vinci–Fiumicino Airport, Rome, Italy
    'IST': (41.2753, 28.7519),  # Istanbul Airport, Turkey
    'MEX': (19.4361, -99.0719),  # Mexico City International Airport, Mexico
    'YYZ': (43.6777, -79.6248),  # Toronto Pearson International Airport, Canada
    'BOM': (19.0896, 72.8656),  # Chhatrapati Shivaji Maharaj International Airport, Mumbai, India
    'ICN': (37.4602, 126.4407),  # Incheon International Airport, Seoul, South Korea
    'BKK': (13.6900, 100.7501),  # Suvarnabhumi Airport, Bangkok, Thailand
}

airport_coordinates.update({
    'CDG': (49.0097, 2.5479),   # Paris Charles de Gaulle
    'ORY': (48.7231, 2.3798),   # Paris Orly
})

# Helper functions
def calculate_distance(origin, destination):
    if origin in airport_coordinates and destination in airport_coordinates:
        return geodesic(airport_coordinates[origin], airport_coordinates[destination]).kilometers
    return 0

def calculate_emissions(distance, stops):
    base_emissions = distance * 0.115  # kg CO2 per km
    stop_penalty = stops * 50          # kg CO2 per stop
    return base_emissions + stop_penalty

def one_hot_encode_airlines(airlines):
    """
    Create a one-hot encoded dataframe for the specified airlines.
    """
    one_hot = {f"Airline: {airline}": 0 for airline in airline_columns}
    for airline in airlines:
        if f"Airline: {airline}" in one_hot:
            one_hot[f"Airline: {airline}"] = 1
    return pd.DataFrame([one_hot])

def preprocess_input(input_data, model_type):
    """
    Preprocess input data for the selected model (classic or eco-friendly).
    """
    preprocessor = classic_preprocessor if model_type == "Classic Model" else eco_preprocessor
    return preprocessor.transform(input_data)

# Streamlit app layout
st.title("Flight Price Prediction App")
st.sidebar.title("Options")

# Sidebar for selecting the model
model_choice = st.sidebar.selectbox("Choose Prediction Model", ["Classic Model", "Eco-Friendly Model"])

# User inputs
st.header("Enter Flight Details")
origin = st.selectbox("Origin Airport (Only ORY/CDG Supported)", ["ORY", "CDG"])
destination = st.selectbox("Destination Airport", list(airport_coordinates.keys()))
stops = st.slider("Number of Stops", 0, 3, 0)
duration = st.number_input("Flight Duration (minutes)", min_value=30, max_value=1440, step=10)
seat_type = st.selectbox("Seat Type", ["Economy", "Premium Economy", "Business", "First Class"])

# Date input
date = st.date_input("Date of Flight")
day = date.day
month = date.month
weekday = date.weekday()

# Multi-carrier input
multi_carrier = st.checkbox("Is this a multi-carrier flight?")

# Airline input
st.subheader("Specify Airlines for Each Leg of the Journey")
airlines = []
for i in range(stops + 1):  # Include all legs (stops + final destination)
    airline = st.text_input(f"Airline for Leg {i + 1}", key=f"airline_leg_{i}")
    if airline:
        airlines.append(airline)

# Derived inputs
distance = calculate_distance(origin, destination)
emissions = calculate_emissions(distance, stops)

# Make predictions
if st.button("Predict"):
    # Prepare input features
    input_data = {
        "Stops": [stops],
        "Duration (mins)": [duration],
        "Origin": [origin],
        "Destination": [destination],
        "Seat Type (Grouped)": [seat_type],
        "Distance (km)": [distance],
        "Carbon Emissions (kg CO2)": [emissions],
        "Day": [day],
        "Month": [month],
        "Weekday": [weekday],
        "Multi-Carrier": [int(multi_carrier)]
    }
    input_df = pd.DataFrame(input_data)

    # Add one-hot encoded airline data
    airline_encoded = one_hot_encode_airlines(airlines)
    input_df = pd.concat([input_df, airline_encoded], axis=1)

    # Ensure all expected columns are present
    for col in airline_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    # Preprocess input
    input_preprocessed = preprocess_input(input_df, model_choice)

    # Make prediction
    if model_choice == "Classic Model":
        prediction = classic_model.predict(input_preprocessed)
        st.success(f"Predicted Price: ${prediction[0]:.2f}")
    elif model_choice == "Eco-Friendly Model":
        prediction = eco_model.predict(input_preprocessed)
        st.success(f"Predicted Price: ${prediction[0][0]:.2f}")
        st.info(f"EcoScore: {prediction[0][1]:.2f}")
        st.info(f"Carbon Emissions: {emissions:.2f} kg CO2")
