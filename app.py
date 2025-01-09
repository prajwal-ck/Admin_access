import os
import requests
import pandas as pd
import json 
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse
import uvicorn
app = FastAPI()
# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize the LLM model
model = GoogleGenerativeAI(model="gemini-pro", temperature=0.2)

# record_id = '63690673-ebd7-4d35-bebf-b1ab563d81ea'
Fecth_one = "https://sandbox.appsteer.io/services/mobile/SubmittedRecord?recordId={record_id}&timezone=Asia/Calcutta"
HEADERS = {
 "X-AUTH-TOKEN":"d0accf3f-5f92-41c6-bb8b-c54b9c8d3896",
 "Content-Type": "application/json"
}

def fetch_data(record_id):
    try:
        fetch_url = f"{Fecth_one}/{record_id}"
        response = requests.get(fetch_url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            req_data = data['UserFormDataRequest']['UserFormData']['FormDataRequest']['FormData'][-3]['value'][0]
            # print(req_data)
            return req_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return []
        
def classify_access_request(request_text):
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


def process_record(record_id, Status):
    """
    Process the record by sending a POST request with updated data.
    """
    url = f"{Fecth_one}/update"
    fetch = fetch_data()
    Status = classify_access_request(fetch)
    # url = "https://sandbox.appsteer.io/services/mobile/SaveUserForm"
    payload = json.dumps({
                    "UserFormDataRequest": {
                        "UserFormData": {
                        "FormDataRequest": {
                            "FormData": [
                            {
                                "FormViewID": 5675,
                                "HeaderID": 7965,
                                "FieldID": 50484,
                                "FieldLabel":"Status",
                                "value": [Status],
                                "UIType": 0,
                                "UserFormData": None,
                                "FieldIdentifier": "Status",
                                "FieldUUID": "6095fd6a-c5fc-4d1d-aeb2-c0291b5a1f5d",
                                "HeaderUUID": "d6739ea2-51e7-4948-a25e-4699d217bd5e",
                                "ViewUUID": "7313719e-b19f-40f6-8546-93bdaee89837"
                            }
                            ],
                            "ViewData": [
                            {
                                "CaptureTime": "2025-01-07 04:55:30",
                                "FormViewID": 5675,
                                "Latitude": "",
                                "Longitude": ""
                            }
                            ]
                        },
                        "RecordID": record_id,
                        "ListDisplayFields": None,
                        "FormID": 2979,
                        "ProfileUUID": None,
                        "Moment": "2025-01-07 04:55:50",
                        "MenuId": 0,
                        "DeviceId": None,
                        "version": "00.00.001",
                        "RecordCurrStatus": 0,
                        "FormUUID": "d92c0300-7208-4c88-9042-297a076ddd02",
                        "isUTC": True,
                        "TimeZone": "Asia/Calcutta",
                        "Offset": 19800
                        }
                    }
                    })          

    response = requests.request("POST", url, headers=HEADERS, data=payload)
    return response.text

def main():
    try:
        fetch = fetch_data()
        Status = classify_access_request(fetch)
         # Process the record
        result = process_record(record_id, Status)
        return result
    except Exception as e:
        error_response = {"message": f"An error occurred: {e}"}
        print(json.dumps(error_response, indent=4))
        return error_response 
    

@app.get("/{encoded_record_id}")
def handle_record(encoded_record_id: str = Path(..., description="The encoded record ID in format [\"record_id\"]")): 
     try:
        # Fetch data using the provided record_id
        fetched_data = fetch_data(record_id)
        if not fetched_data:
            return JSONResponse(
                content={"message": "Failed to fetch data for the record ID."},
                status_code=400,
            )

        # Classify the request status
        status = classify_access_request(fetched_data)

        # Process the record with the classified status
        result = process_record(record_id, status)
        return JSONResponse(content={"message": "Record processed successfully.", "result": result})
     except Exception as e:
        return JSONResponse(
            content={"message": "An error occurred.", "error": str(e)},
            status_code=500,
        )


if __name__ == "__main__":
    # Run the Uvicorn server to serve the FastAPI app
    uvicorn.run(app)
