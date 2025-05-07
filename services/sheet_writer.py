import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
from config.env import GSPREAD_SERVICE_ACCOUNT_JSON

def get_google_sheet():
    """Initialize and return Google Sheet client"""
    try:
        # Parse the JSON string from environment variable
        credentials_dict = json.loads(GSPREAD_SERVICE_ACCOUNT_JSON)
        
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        # Create credentials
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credentials_dict, scope)
        
        # Authorize the client
        client = gspread.authorize(credentials)
        
        # Open the spreadsheet (you'll need to share it with the service account email)
        sheet = client.open("Orders").worksheet("Orders")
        
        return sheet
    except Exception as e:
        print(f"Error initializing Google Sheet: {str(e)}")
        raise

def save_order_to_sheet(user_id: str, order_data: dict):
    """
    Save order data to Google Sheet
    
    Args:
        user_id (str): LINE user ID
        order_data (dict): Order information including flavor, quantity, and customer details
    """
    try:
        # Get the sheet
        sheet = get_google_sheet()
        
        # Prepare row data
        row_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
            user_id,                                       # User ID
            order_data.get('flavor', ''),                 # Flavor
            order_data.get('quantity', ''),               # Quantity
            order_data.get('customer_info', {}).get('name', ''),    # Name
            order_data.get('customer_info', {}).get('phone', ''),   # Phone
            order_data.get('customer_info', {}).get('address', '')  # Address
        ]
        
        # Append the row
        sheet.append_row(row_data)
        
        return True
    except Exception as e:
        print(f"Error saving order to sheet: {str(e)}")
        return False

def initialize_sheet():
    """Initialize the sheet with headers if it doesn't exist"""
    try:
        sheet = get_google_sheet()
        
        # Check if headers exist
        headers = sheet.row_values(1)
        if not headers:
            # Add headers
            header_row = [
                "Timestamp",
                "User ID",
                "Flavor",
                "Quantity",
                "Name",
                "Phone",
                "Address"
            ]
            sheet.append_row(header_row)
            
        return True
    except Exception as e:
        print(f"Error initializing sheet headers: {str(e)}")
        return False 