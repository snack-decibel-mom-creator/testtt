from playwright.sync_api import sync_playwright
import time

def print_action(action):
    """Print action with timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {action}")

def main():
    print_action("Starting Playwright automation...")
    
    with sync_playwright() as p:
        # Launch browser in headless mode with specific options
        print_action("Launching Chromium browser...")
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        
        try:
            # Navigate to the website
            url = "https://nnrg.beessoftware.cloud/studentselfservice"
            print_action(f"Navigating to: {url}")
            page.goto(url)
            
            # Wait for page to load
            print_action("Waiting for page to load...")
            page.wait_for_load_state('networkidle')
            print_action("Page loaded successfully")
            
            # Print page title
            page_title = page.title()
            print_action(f"Page title: {page_title}")
            
            # First, let's try clicking forgot password BEFORE entering credentials
            print_action("Attempting to click forgot password link FIRST (before entering credentials)...")
            form_appeared = False
            try:
                forgot_password_link_first = page.locator('#lbl_forgotpassword')
                if forgot_password_link_first.is_visible():
                    forgot_password_link_first.click()
                    print_action("Successfully clicked forgot password link (first attempt)")
                    time.sleep(3)
                    
                    # Check if form appeared
                    if page.locator('#ForgetPassWordlogin').is_visible():
                        print_action("SUCCESS! Forgot password form appeared when clicked first!")
                        form_appeared = True
                        # Skip the rest since we succeeded
                        print_action("Skipping credential entry since form appeared")
                    else:
                        print_action("Forgot password form did not appear when clicked first")
                        print_action("Proceeding with credential entry and second attempt...")
                        
                        # Now enter credentials
                        print_action("Looking for username field...")
                        username_field = page.locator('#txt_UserName')
                        if username_field.is_visible():
                            print_action("Found username field: txt_UserName")
                            
                            roll_number = "237Z1A0501"
                            print_action(f"Entering roll number: {roll_number}")
                            username_field.fill(roll_number)
                            print_action(f"Successfully entered: {roll_number}")
                            
                            # Verify the value was entered
                            entered_value = username_field.input_value()
                            print_action(f"Verified entered value: {entered_value}")
                            
                            # Also try to find and fill password field (even if empty)
                            print_action("Looking for password field...")
                            password_field = page.locator('#txt_Password')
                            if password_field.is_visible():
                                print_action("Found password field: txt_Password")
                                # Enter a dummy password to satisfy validation
                                dummy_password = "dummy123"
                                print_action(f"Entering dummy password: {dummy_password}")
                                password_field.fill(dummy_password)
                                print_action("Successfully entered dummy password")
                            else:
                                print_action("Password field not found")
                        else:
                            print_action("Username field not found or not visible")
            except Exception as e:
                print_action(f"First attempt failed: {e}, proceeding with credential entry first...")
                
                # Enter credentials first
                print_action("Looking for username field...")
                username_field = page.locator('#txt_UserName')
                if username_field.is_visible():
                    print_action("Found username field: txt_UserName")
                    
                    roll_number = "237Z1A0501"
                    print_action(f"Entering roll number: {roll_number}")
                    username_field.fill(roll_number)
                    print_action(f"Successfully entered: {roll_number}")
                    
                    # Verify the value was entered
                    entered_value = username_field.input_value()
                    print_action(f"Verified entered value: {entered_value}")
                    
                    # Also try to find and fill password field (even if empty)
                    print_action("Looking for password field...")
                    password_field = page.locator('#txt_Password')
                    if password_field.is_visible():
                        print_action("Found password field: txt_Password")
                        # Enter a dummy password to satisfy validation
                        dummy_password = "dummy123"
                        print_action(f"Entering dummy password: {dummy_password}")
                        password_field.fill(dummy_password)
                        print_action("Successfully entered dummy password")
                    else:
                        print_action("Password field not found")
                else:
                    print_action("Username field not found or not visible")
            
            # Find and click forgot password link (second attempt if needed)
            if not form_appeared:
                print_action("Looking for forgot password link...")
                forgot_password_link = page.locator('#lbl_forgotpassword')
                if forgot_password_link.is_visible():
                    print_action("Found forgot password link: lbl_forgotpassword")
                    
                    # Try different click methods
                    print_action("Attempting to click forgot password link...")
                    try:
                        # Try regular click first
                        forgot_password_link.click()
                        print_action("Successfully clicked forgot password link (regular click)")
                    except Exception as e:
                        print_action(f"Regular click failed: {e}, trying force click...")
                        try:
                            forgot_password_link.click(force=True)
                            print_action("Successfully clicked forgot password link (force click)")
                        except Exception as e2:
                            print_action(f"Force click failed: {e2}, trying JavaScript click...")
                            try:
                                page.evaluate("document.getElementById('lbl_forgotpassword').click()")
                                print_action("Successfully clicked forgot password link (JavaScript click)")
                            except Exception as e3:
                                print_action(f"JavaScript click failed: {e3}")
                    
                    # Wait for the forgot password form to appear
                    print_action("Waiting for forgot password form to load...")
                    time.sleep(5)
                    
                    # Take a screenshot to see what's on the page
                    screenshot_path = "/workspaces/testtt/after_click.png"
                    page.screenshot(path=screenshot_path)
                    print_action(f"Screenshot saved after click: {screenshot_path}")
                    
                    # Print the current page content to debug
                    print_action(f"Current page URL: {page.url}")
                    
                    # Look for any changes in the page
                    print_action("Checking for any visible changes...")
                    
                    # Check for any error messages
                    try:
                        error_elements = page.locator('[class*="error"], [class*="Error"], [id*="error"], [id*="Error"], [class*="danger"], [class*="Danger"]')
                        if error_elements.count() > 0:
                            print_action(f"Found {error_elements.count()} error-related elements")
                            for i in range(error_elements.count()):
                                try:
                                    error_text = error_elements.nth(i).text_content()
                                    error_id = error_elements.nth(i).get_attribute('id')
                                    error_class = error_elements.nth(i).get_attribute('class')
                                    if error_text and error_text.strip():
                                        print_action(f"Error message {i+1}: ID={error_id}, Class={error_class}, Text={error_text.strip()}")
                                    elif error_elements.nth(i).is_visible():
                                        print_action(f"Visible error element {i+1}: ID={error_id}, Class={error_class} (no text content)")
                                except Exception as e:
                                    print_action(f"Error reading element {i+1}: {e}")
                    except Exception as e:
                        print_action(f"No error elements found: {e}")
                    
                    # Try to find any element that might indicate the forgot password process started
                    try:
                        any_forgot_element = page.locator('[id*="forget"], [id*="Forget"], [id*="forgot"], [id*="Forgot"]').first
                        if any_forgot_element.is_visible():
                            print_action(f"Found forgot-related element: {any_forgot_element.get_attribute('id')}")
                    except:
                        print_action("No forgot-related elements found")
                    
                    # Check if there are any modals or overlays
                    try:
                        modals = page.locator('[class*="modal"], [class*="Modal"], [class*="overlay"], [class*="Overlay"], [id*="modal"], [id*="Modal"]')
                        if modals.count() > 0:
                            print_action(f"Found {modals.count()} modal/overlay elements")
                            for i in range(modals.count()):
                                try:
                                    modal_id = modals.nth(i).get_attribute('id')
                                    modal_class = modals.nth(i).get_attribute('class')
                                    is_visible = modals.nth(i).is_visible()
                                    print_action(f"Modal {i+1}: ID={modal_id}, Class={modal_class}, Visible={is_visible}")
                                    if is_visible:
                                        try:
                                            modal_text = modals.nth(i).text_content()
                                            if modal_text and modal_text.strip():
                                                print_action(f"Modal {i+1} text: {modal_text.strip()[:100]}")  # First 100 chars
                                        except:
                                            pass
                                except Exception as e:
                                    print_action(f"Error reading modal {i+1}: {e}")
                    except Exception as e:
                        print_action(f"No modal elements found: {e}")
                    
                    # Check for any validation messages
                    try:
                        validation_elements = page.locator('span.text-danger, [class*="text-danger"], [id*="span_"]')
                        if validation_elements.count() > 0:
                            print_action(f"Found {validation_elements.count()} validation elements")
                            for i in range(validation_elements.count()):
                                try:
                                    validation_text = validation_elements.nth(i).text_content()
                                    validation_id = validation_elements.nth(i).get_attribute('id')
                                    if validation_text and validation_text.strip():
                                        print_action(f"Validation {i+1}: ID={validation_id}, Text={validation_text.strip()}")
                                except:
                                    pass
                    except:
                        print_action("No validation elements found")
                    
                    # Check if forgot password form is visible
                    try:
                        forgot_password_form = page.locator('#ForgetPassWordlogin')
                        if forgot_password_form.is_visible():
                            print_action("Forgot password form is now visible!")
                            
                            # Take a screenshot for debugging
                            screenshot_path = "/workspaces/testtt/forgot_password_page.png"
                            page.screenshot(path=screenshot_path)
                            print_action(f"Screenshot saved to: {screenshot_path}")
                            
                            # Print the URL to confirm we're on the right page
                            current_url = page.url
                            print_action(f"Current URL: {current_url}")
                            
                            # Look for form fields in the forgot password section
                            print_action("Looking for forgot password form fields...")
                            
                            try:
                                password_field = page.locator('#ForgetPassWordPassword')
                                if password_field.is_visible():
                                    print_action("Found password field: ForgetPassWordPassword")
                            except:
                                print_action("Password field not found")
                            
                            try:
                                confirm_password_field = page.locator('#ForgetPassWordConfirmpassword')
                                if confirm_password_field.is_visible():
                                    print_action("Found confirm password field: ForgetPassWordConfirmpassword")
                            except:
                                print_action("Confirm password field not found")
                            
                            try:
                                submit_button = page.locator('#btn_ForgotLogin')
                                if submit_button.is_visible():
                                    print_action("Found submit button: btn_ForgotLogin")
                            except:
                                print_action("Submit button not found")
                        else:
                            print_action("Forgot password form is not visible")
                    except Exception as e:
                        print_action(f"Error checking for forgot password form: {e}")
            else:
                print_action("Form already appeared, skipping second attempt")
            
            # Wait a bit more to see the result
            print_action("Waiting 3 seconds to observe the result...")
            time.sleep(3)
            
            print_action("Automation completed successfully!")
            
        except Exception as e:
            print_action(f"Error occurred: {e}")
            
        finally:
            # Close the browser
            print_action("Closing browser...")
            browser.close()
            print_action("Browser closed")

if __name__ == "__main__":
    main()