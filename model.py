import weather
from datetime import datetime

# modules imported for model
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# --------------------------------------------------- code for model deployment -----------------------------------------------------------

global X_train
# change filepath accordingly
X_train = pd.read_csv("model_files/X_train.csv")

# Scale the features using StandardScaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)

# change file path accordingly
loaded_model = pickle.load(open('model_files/SolarHourXGBmodel.sav', 'rb'))

#Inputs(In sequence) : Hour,	Day,	Month,	Year,	batteryLevel,	weather_code_encoded,	sunshine_duration_hours,    precipitation (mm),   soil_temperature_0_to_7cm (°F),	 vapour_pressure_deficit (kPa).

# ------------------------------------------------- code for model deployment ends ----------------------------------------------------------------

# Function to parse timestamp and extract components
# print('model_loaded_successfully')


def parse_timestamp(timestamp):
    dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M')
    date_str = dt.strftime('%Y-%m-%d')
    return date_str, dt.hour


def xgb_model(latitude, longitude, date, initial_battery_percentage=0):

    data = weather.getWeatherData(latitude, longitude, date)
    # print(data)

    # Extract hourly data
    hourly_data = data['hourly']

    # -------------------------------------------------- api data to numpy array conversion -------------------------------------------------
    # code for converting the api data into a numpy array that can be passes to the model

    # Convert lists to numpy arrays
    time = np.array(hourly_data['time'])
    precipitation = np.array(hourly_data['precipitation'])
    weather_code = np.array(hourly_data['weather_code'])
    vapour_pressure_deficit = np.array(hourly_data['vapour_pressure_deficit'])
    soil_temperature_6cm = np.array(hourly_data['soil_temperature_6cm'])

    # Ordinal encoding of weather_code
    encoding_dict = {0: 0, 1: 1, 2: 2, 3: 3, 45: 4, 48:5, 51: 6, 53: 7, 55: 8, 56:9, 57:10, 61: 11, 63: 12, 65: 13, 66:14, 67:15, 71:16, 73:17, 75:18, 77:19, 80:20, 81:21, 82:22, 85:23, 86:24, 95:25, 96:26, 99:27}

    # Apply the encoding to the 'weather_code' column
    encoded_weather_code = np.array([encoding_dict[code] for code in weather_code])

    # Combine arrays into a 2D numpy array
    hourly_np = np.column_stack((time, precipitation, encoded_weather_code, vapour_pressure_deficit, soil_temperature_6cm))

    #print(hourly_np)

    # Apply the function to each row of the hourly numpy array
    parsed_np = np.array([parse_timestamp(row[0]) + tuple(row[1:]) for row in hourly_np])

    #print(parsed_np)

    # Convert hourly_np data to DataFrame
    hourly_df = pd.DataFrame(parsed_np)

    daily_data = data['daily']
    #print(daily_data)

    # Convert lists to numpy arrays
    date = np.array(daily_data['time'])
    sunshine_duration_seconds = np.array(daily_data['sunshine_duration'])
    sunrise = np.array(daily_data['sunrise'])
    sunset = np.array(daily_data['sunset'])

    sunrise_time = datetime.strptime(sunrise[0], '%Y-%m-%dT%H:%M')
    # Extract the hour from the datetime object
    sunrise_hour = sunrise_time.hour

    sunset_time = datetime.strptime(sunset[0], '%Y-%m-%dT%H:%M')
    # Extract the hour from the datetime object
    sunset_hour = sunset_time.hour
    #print(sunrise_hour)
    #print(sunset_hour)

    # Convert sunshine duration from seconds to hours
    sunshine_duration = sunshine_duration_seconds / 3600

    # Combine arrays into a 2D numpy array
    daily_np = np.column_stack((date, sunshine_duration))

    #print(daily_np)

    # Convert daily data to DataFrame
    daily_df = pd.DataFrame(daily_np)

    # Merge hourly and daily data on the date column
    merged_df = pd.merge(hourly_df, daily_df, left_on=hourly_df[0], right_on=daily_df[0],)


    # Drop duplicate date column
    merged_df.drop(columns=['key_0'], inplace=True)

    # Convert merged DataFrame to numpy array
    merged_np = merged_df.to_numpy()

    #print(merged_np)

    # Extracting year, month, and day
    year_month_day = np.array([date.split('-') for date in merged_np[:, 0]])

    # Convert elements to integers
    year_month_day = year_month_day.astype(int)

    # Concatenate year, month, day with other data
    result = np.concatenate((year_month_day, merged_np[:, 1:]), axis=1)

    #print(result)

    # Define the desired order of columns
    column_order = [3, 2, 1, 0, 5 , 9, 4, 6, 7, 8]  # New order of columns: index 2 -> index 0 -> index 1 -> index 3

    # Rearrange columns using numpy array indexing and concatenation
    reordered_np = result[:, column_order]

    #print("Reordered numpy array:")
    #print(reordered_np)

    # Remove the last column
    api_data = reordered_np[:, :-1]
        
    # Convert specific columns to int and float
    api_data[:, 0:5] = api_data[:, 0:5].astype(int)  # Convert column 0 to int
    api_data[:, 5:9] = api_data[:, 5:9].astype(float)  # Convert columns 3 and 4 to float

    # Filter rows based on the condition
    final_api_data = api_data[(api_data[:, 0] >= sunrise_hour) & (api_data[:, 0] <= sunset_hour)]

    #print(final_api_data)

    # Initialize an empty array to store the predicted results
    predicted_results = [initial_battery_percentage]
    # Iterate through each row of input_data
    for row in final_api_data:

        # Add initial battery percentage at the 4th position
        row_with_battery = np.insert(row, 4, initial_battery_percentage)

        # Convert the row to numpy array and reshape
        input_row = np.array(row_with_battery).reshape(1, -1)

        # Standardize the input data
        std_data = scaler.transform(input_row)

        # Predict using the loaded model
        predicted_result = loaded_model.predict(std_data)

        if predicted_result[0] < 0 :
            predicted_result[0] = 0

        # Update initial battery percentage for next iteration
        initial_battery_percentage += predicted_result[0]
        initial_battery_percentage = min(100, initial_battery_percentage)
        # Append the predicted result to the list
        predicted_results.append(initial_battery_percentage)
    # Convert the list of predicted results to a numpy array
    predicted_results_array = predicted_results

    # this array can be used for lamp duration visualisation
    # print(predicted_results_array)

    return {
        'total_increase': min(100,initial_battery_percentage),
        'sunrise_hour': sunrise_hour,
        'sunset_hour': sunset_hour,
        'predicted_results_array': predicted_results_array
        }


