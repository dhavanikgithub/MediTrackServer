import requests
API_URL = 'https://leavemanagementuvpce.000webhostapp.com/leave_management_system/auth.php'
TIMEOUT_SECONDS = 30
# Define the headers with the content type
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

def get_user_data():
    # Define the form data as a dictionary
    form_data = {
        "function_name": "leave_get_user_info",
        "enrollment": "2101202022"
    }
    response = requests.post(API_URL, headers=headers, data=form_data,timeout=TIMEOUT_SECONDS)
    if response.status_code == 200:
        api_data = response.json()  # Parse JSON response
        return api_data
    return f"Request failed with status code: {response.text}"
