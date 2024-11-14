import requests
import pandas as pd
import boto3
from datetime import datetime
from io import StringIO


# Step 1: Fetch data from the API
def fetch_data(api_url, params):
    # Requesting data
    response = requests.get(api_url, params=params)
    data = response.json()
    
    if response.status_code == 200:
        return response.json()  # or response.text for raw content
    else:
        raise Exception("API request failed with status code " + str(response.status_code))
    
# Selecting relevant fields and transforming to a DataFrame
def transform_data(data):
    filtered_data = []
    for time, values in data.items():
        # Extract only the necessary fields
        filtered_data.append({
            "timestamp": time,
            "open": values["1. open"],
            "high": values["2. high"],
            "low": values["3. low"],
            "close": values["4. close"],
            "volume": values["5. volume"]
        })
    
    # Convert the filtered data into a DataFrame
    df = pd.DataFrame(filtered_data)
    return df


# Step 3: Save the Data to a CSV file in memory (using StringIO)
def save_to_csv(df):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer.getvalue()

# Step 4: Upload to S3
def upload_to_s3(bucket_name, file_content, file_name):
    s3 = boto3.client('s3')  # Ensure you have AWS credentials set up
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
    print(f'File {file_name} uploaded to S3 bucket {bucket_name}.')




# API URL and Key (Replace with actual URL and API Key)
api_url = "https://www.alphavantage.co/query"
api_key = "getfromportal"
params = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": "IBM",
    "interval": "5min",
    "apikey": api_key
}

bucket_name = "my-bucket-for-my-project"
file_name = f"stock_price_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"

# Fetch, transform, and upload the data
try:
    # Step 1: Fetch data from the API
    data = fetch_data(api_url, params)
    time_series = data['Time Series (5min)']

    # Step 2: Transform the data
    transformed_data = transform_data(time_series)

    # Step 3: Save the data to CSV
    file_content = save_to_csv(transformed_data)

    # Step 4: Upload to S3
    upload_to_s3(bucket_name, file_content, file_name)

except Exception as e:
    print(f"An error occurred: {e}")

