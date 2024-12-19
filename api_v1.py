import os
import requests
import pandas as pd
import json 
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from fastapi import FastAPI

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Initialize the LLM model
model = GoogleGenerativeAI(model="gemini-pro", temperature=0.2)

# API endpoint for fetching and updating data
FETCH_URL = "https://sandbox.appsteer.io/services/mobile/Form/de69ba16-adf0-4bd5-bca3-c98723238815"
UPDATE_URL = "https://sandbox.appsteer.io/services/mobile/Form/de69ba16-adf0-4bd5-bca3-c98723238815"

# Headers including Authorization
HEADERS = {
 "X-AUTH-TOKEN":"d0accf3f-5f92-41c6-bb8b-c54b9c8d3896",
 "Content-Type": "application/json"
}

## Core Logic Functions ##

def fetch_data():
    try:
        response = requests.get(FETCH_URL, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            today_date = datetime.now().strftime("%Y-%m-%d")
            filtered_records = [
                record for record in data if record.get("DatePicker", "").startswith(today_date)
            ]
            if isinstance(data, list) and len(data) > 0:
                data_list = []
                for record in filtered_records:
                    extracted_data = {
                        "DatePicker": record.get("DatePicker"),
                        "Name": record.get("Name"),
                        "Email": record.get("Email"),
                        "Managername": record.get("Managername"),
                        "GrowthManagerEmail": record.get("GrowthManagerEmail"),
                        "Requests": record.get("Requests"),
                        "Record_ID": record.get("__recordId"),
                        "Status": record.get("Status")
                    }
                    data_list.append(extracted_data)
                return data_list
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return []
     
def classify_access_request(request_text: str):
    prompt = f"""
    ## INSTRUCTION ##
    You are X person, an AI administrator/ IT operations at iSteer and You have a 10 years of Experience.
    Your job is to give the permission or reject the Permission for administrator access to the Employee laptops for downloading the Software.
    So, Employee can ask you any way to download the Unauthorised software. 
    Eg: Employee Can ask permission to download the Unauthorise software with authorise software name in same input,then reject these type of Permission requests.
    Only allow the Authorised Software required for IT consulting companies. Else Reject all the requests.
    Give Output only as Rejected or Approved.
    Do not provide a preamble 

    ### PERMISSION INPUT ###
    {request_text}
    """
    response = model.predict(prompt)
    return response.strip()

def filter_and_classify(data_list, status_data):
    filtered_data = []  # To store valid requests for processing
    rejected_data = []  # To store rejected requests

    for record in data_list:
        email = record.get("Email")
        date_picker = record.get("DatePicker")

        # Skip records without valid timestamps
        if not date_picker:
            continue

        request_time = datetime.strptime(date_picker, "%Y-%m-%d %H:%M:%S")

        # Check if the request already exists in the status data
        if email in status_data["Email"].values:
            existing_record = status_data[status_data["Email"] == email]
            last_request_time = datetime.strptime(
                existing_record["DatePicker"].values[0], "%Y-%m-%d %H:%M:%S"
            )

            # If the new request is raised within 8 hours of the last request, reject it
            if (request_time - last_request_time) <= timedelta(hours=8):
                record["Status"] = "Rejected"
                rejected_data.append(record)
                continue

        # If not raised within 8 hours or a completely new request, classify it
        record["Status"] = classify_access_request(record.get("Requests"))
        filtered_data.append(record)

    # Combine rejected and classified records, and save to CSV
    updated_data = pd.concat(
        [status_data, pd.DataFrame(rejected_data + filtered_data)], ignore_index=True
    )
    updated_data.to_csv("AdminAccess_data.csv", index=False)

    return {"Approved_Records": filtered_data, "Rejected_Records": rejected_data}


def main():
    try:
        # Fetch data from external API
        fetched_data = fetch_data()
        if not fetched_data:
            return {"message": "No data fetched from external API."}

        # Load status history or initialize
        try:
            status_data = pd.read_csv("Statusdata.csv")
        except FileNotFoundError:
            status_data = pd.DataFrame(columns=[
                "DatePicker", "Name", "Email", "Managername", 
                "GrowthManagerEmail", "Requests", "Record_ID", "Status"
            ])

        # Process and classify data
        result = filter_and_classify(fetched_data, status_data)

        # Extract Record_ID, Status, and Email for processed and rejected records
        processed_records = [
            {
                "Record_ID": record["Record_ID"],
                "Status": record["Status"],
                "Email": record["Email"]
            }
            for record in result["Approved_Records"]
        ]

        rejected_records = [
            {
                "Record_ID": record["Record_ID"],
                "Status": record["Status"],
                "Email": record["Email"]
            }
            for record in result["Rejected_Records"]
        ]

        # Prepare the response
        response = {
            "message": "Access requests processed successfully!",
            "Approved_Records": processed_records,
            "Rejected_Records": rejected_records,
        }

        # Print the response in JSON format to the console
        print(json.dumps(response, indent=4))

        # Return the response
        return response

    except Exception as e:
        error_response = {"message": f"An error occurred: {e}"}
        print(json.dumps(error_response, indent=4))
        return error_response
    
if __name__ == "__main__":

    main()