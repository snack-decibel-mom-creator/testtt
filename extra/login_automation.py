import requests
from bs4 import BeautifulSoup
import time

def print_action(action):
    """Print action with timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {action}")

def main():
    print_action("Starting HTTP request automation...")
    
    # Setup session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        # Navigate to the website
        url = "https://nnrg.beessoftware.cloud/studentselfservice"
        print_action(f"Fetching page: {url}")
        response = session.get(url)
        print_action(f"Response status: {response.status_code}")
        
        # Parse the page
        print_action("Parsing page content...")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the username field
        print_action("Looking for username field...")
        username_field = soup.find('input', {'id': 'txt_UserName'})
        if username_field:
            print_action("Found username field: txt_UserName")
        else:
            print_action("Username field not found")
        
        # Find the forgot password link
        print_action("Looking for forgot password link...")
        forgot_password_link = soup.find('a', {'id': 'lbl_forgotpassword'})
        if forgot_password_link:
            print_action("Found forgot password link: lbl_forgotpassword")
            print_action(f"Link href: {forgot_password_link.get('href', 'N/A')}")
        else:
            print_action("Forgot password link not found")
        
        # Find the login form
        print_action("Looking for login form...")
        login_form = soup.find('form', {'id': 'loginFormElement'})
        if login_form:
            print_action("Found login form: loginFormElement")
            print_action(f"Form action: {login_form.get('action', 'N/A')}")
        else:
            print_action("Login form not found")
        
        # Simulate entering the username
        roll_number = "237Z1A0501"
        print_action(f"Simulating entering roll number: {roll_number}")
        
        # Get form data
        form_data = {}
        if login_form:
            # Get all input fields
            inputs = login_form.find_all('input')
            for input_field in inputs:
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    if name == 'UserName':
                        form_data[name] = roll_number
                    else:
                        form_data[name] = value
                    print_action(f"Form field: {name} = {form_data[name]}")
        
        # Since we can't actually click with requests, we'll show what would happen
        print_action("Simulating forgot password click...")
        print_action("Note: HTTP requests cannot simulate JavaScript clicks")
        print_action("The forgot password functionality likely requires JavaScript execution")
        
        # Try to get the forgot password form directly
        print_action("Attempting to access forgot password endpoint...")
        forgot_url = f"{url}/Login/ForgotPassword"
        print_action(f"Trying: {forgot_url}")
        
        try:
            forgot_response = session.get(forgot_url)
            print_action(f"Forgot password response status: {forgot_response.status_code}")
        except Exception as e:
            print_action(f"Could not access forgot password endpoint: {e}")
        
        print_action("HTTP request automation completed!")
        print_action("Note: Full automation requires browser automation with JavaScript support")
        
    except Exception as e:
        print_action(f"Error occurred: {e}")

if __name__ == "__main__":
    main()