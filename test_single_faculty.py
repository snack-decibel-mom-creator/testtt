from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path
import time

def test_single_faculty_with_screenshot(faculty_id):
    """Test a single faculty ID with screenshot after forgot password click"""
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting test for faculty ID: {faculty_id}")
    
    try:
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-zygote',
                    '--disable-extensions',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            page = browser.new_page()
            
            try:
                # Navigate to the faculty portal
                url = "https://nnrg.beessoftware.cloud/CloudilyaUnited"
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Opening faculty portal...")
                
                page.goto(url, wait_until='domcontentloaded', timeout=60000)
                
                try:
                    page.wait_for_load_state('networkidle', timeout=30000)
                except:
                    pass
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Faculty portal loaded")
                
                # Enter faculty ID
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Entering faculty ID: {faculty_id}")
                username_field = page.locator('#txt_UserName')
                username_field.wait_for(state='visible', timeout=15000)
                username_field.fill(faculty_id)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Faculty ID entered")
                
                time.sleep(1)
                
                # Take screenshot before clicking forgot password to see the page
                screenshot_dir = Path("screenshots")
                screenshot_dir.mkdir(exist_ok=True)
                timestamp_before = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_before = screenshot_dir / f"{faculty_id}_before_click_{timestamp_before}.png"
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Taking screenshot before click: {screenshot_before}")
                page.screenshot(path=str(screenshot_before), full_page=True)
                
                # Try to find forgot password link - try different selectors
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Looking for forgot password link...")
                
                # Try multiple possible selectors
                selectors = [
                    '#lbl_forgotpassword',
                    'a:has-text("Forgot")',
                    'a:has-text("Password")',
                    '[id*="forgot"]',
                    '[id*="Forgot"]',
                    'text=Forgot Password'
                ]
                
                forgot_element = None
                for selector in selectors:
                    try:
                        element = page.locator(selector)
                        if element.count() > 0:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Found element with selector: {selector}")
                            forgot_element = element
                            break
                    except:
                        continue
                
                if forgot_element:
                    forgot_element.click()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Forgot password clicked")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Could not find forgot password link with any selector")
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Taking screenshot of current page state...")
                    page.screenshot(path=str(screenshot_dir / f"{faculty_id}_error_state_{timestamp_before}.png"), full_page=True)
                    raise Exception("Could not find forgot password link")
                
                # Wait for the click to register
                page.wait_for_timeout(3000)
                
                # Take screenshot after the click
                timestamp_after = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_after = screenshot_dir / f"{faculty_id}_after_click_{timestamp_after}.png"
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Taking screenshot after click: {screenshot_after}")
                page.screenshot(path=str(screenshot_after), full_page=True)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Screenshot saved successfully")
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Test completed successfully")
                return True, screenshot_after
                
            except Exception as e:
                error_msg = str(e)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Error during test: {error_msg}")
                return False, error_msg
                
            finally:
                browser.close()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Browser closed")
                
    except Exception as e:
        error_msg = str(e)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Browser error: {error_msg}")
        return False, error_msg

if __name__ == "__main__":
    test_id = "16F5-1568"
    print(f"Testing faculty ID: {test_id}")
    print("=" * 50)
    
    success, result = test_single_faculty_with_screenshot(test_id)
    
    print("=" * 50)
    if success:
        print(f"✅ Test successful! Screenshot saved: {result}")
    else:
        print(f"❌ Test failed: {result}")