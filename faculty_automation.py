from playwright.sync_api import sync_playwright
import concurrent.futures
import time
from datetime import datetime
import random
import os
import csv
from pathlib import Path

def print_action(action, faculty_id=None):
    """Print action with timestamp and faculty ID"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if faculty_id:
        print(f"[{timestamp}] [{faculty_id}] {action}")
    else:
        print(f"[{timestamp}] {action}")

def get_faculty_ids():
    """
    Get faculty IDs from the CSV file created from faculty data
    Reads faculty_institution_ids.csv and returns institution IDs
    """
    faculty_ids = []
    
    try:
        with open('faculty_institution_ids.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                inst_id = row['institution_id'].strip()
                # Only add non-empty institution IDs
                if inst_id and inst_id != '-':
                    faculty_ids.append(inst_id)
        
        print_action(f"Loaded {len(faculty_ids)} faculty institution IDs from CSV file")
        
    except FileNotFoundError:
        print_action("Error: faculty_institution_ids.csv file not found")
        print_action("Please run parse_faculty_data.py first to generate the CSV file")
    except Exception as e:
        print_action(f"Error reading CSV file: {str(e)}")
    
    return faculty_ids

def process_single_faculty_id(faculty_id, max_retries=3, take_screenshot=False):
    """Process forgot password for a single faculty ID with retry logic"""
    result = {
        'faculty_id': faculty_id,
        'success': False,
        'message': '',
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'attempts': 0
    }
    
    for attempt in range(max_retries):
        result['attempts'] = attempt + 1
        try:
            with sync_playwright() as p:
                # Launch browser in headless mode with optimized settings
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
                    # Navigate to the faculty portal and wait for load
                    url = "https://nnrg.beessoftware.cloud/CloudilyaUnited"
                    print_action(f"Opening faculty portal... (Attempt {attempt + 1}/{max_retries})", faculty_id)
                    
                    # Set longer timeout for page load
                    page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    
                    # Wait for network to be idle with longer timeout
                    try:
                        page.wait_for_load_state('networkidle', timeout=30000)
                    except:
                        # If networkidle fails, continue anyway as page might be functional
                        pass
                    
                    print_action("Faculty portal loaded", faculty_id)
                    
                    # Add small random delay to avoid overwhelming server
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    # Find and enter faculty ID in username field
                    print_action(f"Entering faculty ID: {faculty_id}", faculty_id)
                    username_field = page.locator('#txt_UserName')
                    username_field.wait_for(state='visible', timeout=15000)
                    username_field.fill(faculty_id)
                    print_action("Faculty ID entered", faculty_id)
                    
                    # Small delay before clicking
                    time.sleep(random.uniform(0.3, 0.8))
                    
                    # Click forgot password link
                    print_action("Clicking forgot password", faculty_id)
                    # Try multiple selectors for forgot password link
                    selectors = [
                        'a:has-text("Forgot")',
                        '#lbl_forgotpassword',
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
                                print_action(f"Found forgot password link with selector: {selector}", faculty_id)
                                forgot_element = element
                                break
                        except:
                            continue
                    
                    if forgot_element:
                        forgot_element.click()
                        print_action("Forgot password clicked", faculty_id)
                    else:
                        raise Exception("Could not find forgot password link with any selector")
                    
                    # Wait a moment for the click to register
                    page.wait_for_timeout(2000)
                    
                    # Take screenshot if requested
                    if take_screenshot:
                        # Create screenshots directory if it doesn't exist
                        screenshot_dir = Path("screenshots")
                        screenshot_dir.mkdir(exist_ok=True)
                        
                        # Generate screenshot filename with timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = screenshot_dir / f"{faculty_id}_{timestamp}.png"
                        
                        print_action(f"Taking screenshot: {screenshot_path}", faculty_id)
                        page.screenshot(path=str(screenshot_path), full_page=True)
                        print_action("Screenshot saved", faculty_id)
                    
                    result['message'] = "Completed successfully"
                    result['success'] = True
                    break  # Success - exit retry loop
                        
                except Exception as e:
                    error_msg = str(e)
                    result['message'] = f"Error (Attempt {attempt + 1}/{max_retries}): {error_msg}"
                    print_action(f"Error (Attempt {attempt + 1}/{max_retries}): {error_msg}", faculty_id)
                    
                    if attempt < max_retries - 1:
                        # Wait before retry with exponential backoff
                        wait_time = (2 ** attempt) * random.uniform(1, 3)
                        print_action(f"Retrying in {wait_time:.1f}s...", faculty_id)
                        time.sleep(wait_time)
                    else:
                        result['success'] = False
                        
                finally:
                    browser.close()
                    print_action("Browser closed", faculty_id)
                    
        except Exception as e:
            error_msg = str(e)
            result['message'] = f"Browser error (Attempt {attempt + 1}/{max_retries}): {error_msg}"
            print_action(f"Browser error (Attempt {attempt + 1}/{max_retries}): {error_msg}", faculty_id)
            
            if attempt < max_retries - 1:
                # Wait before retry with exponential backoff
                wait_time = (2 ** attempt) * random.uniform(1, 3)
                print_action(f"Retrying in {wait_time:.1f}s...", faculty_id)
                time.sleep(wait_time)
            else:
                result['success'] = False
    
    return result

def process_batch(batch, batch_num, take_screenshot=False):
    """Process a batch of faculty IDs with optimized parallel processing"""
    print_action(f"=== Starting Batch {batch_num} ===")
    print_action(f"Processing {len(batch)} faculty IDs in parallel")
    
    results = []
    # Use exactly 5 workers or the batch size if smaller
    max_workers = min(len(batch), 5)  # Max 5 concurrent workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks at once
        future_to_faculty = {executor.submit(process_single_faculty_id, faculty, take_screenshot=take_screenshot): faculty for faculty in batch}
        
        # Process as they complete for immediate feedback
        for future in concurrent.futures.as_completed(future_to_faculty):
            faculty = future_to_faculty[future]
            try:
                result = future.result()
                results.append(result)
                status = "✅" if result['success'] else "❌"
                attempt_info = f" (Attempt {result['attempts']})" if 'attempts' in result else ""
                print_action(f"{status} {faculty}{attempt_info} - {result['message']}", faculty)
            except Exception as e:
                print_action(f"❌ {faculty} - Exception: {str(e)}", faculty)
                results.append({
                    'faculty_id': faculty,
                    'success': False,
                    'message': f"Exception: {str(e)}",
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'attempts': 1
                })
    
    # Summary for this batch
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    avg_attempts = sum(r.get('attempts', 1) for r in results) / len(results) if results else 1
    print_action(f"=== Batch {batch_num} Complete: {successful} successful, {failed} failed (avg {avg_attempts:.1f} attempts) ===")
    
    return results

def main():
    start_time = time.time()
    print_action("Starting Faculty Forgot Password Automation")
    print_action("Getting faculty IDs from portal")
    
    # Get faculty IDs using the function you'll provide
    faculty_ids = get_faculty_ids()
    print_action(f"Generated {len(faculty_ids)} faculty IDs")
    
    # Configuration
    test_mode = False  # Set to True for testing with single ID, False for full automation
    test_id = "16F5-1568"  # ID to test with (only used if test_mode = True)
    take_screenshots = False  # Set to True to take screenshots after forgot password click (disabled for full automation)
    
    # For testing, use just the specified ID
    if test_mode:
        faculty_ids = [test_id]  # Test with single ID
        print_action(f"TEST MODE: Processing single faculty ID: {test_id}")
        print_action(f"Screenshots enabled: {take_screenshots}")
    
    # Split into groups of 5 faculty IDs
    group_size = 5
    groups = [faculty_ids[i:i + group_size] for i in range(0, len(faculty_ids), group_size)]
    
    print_action(f"Split into {len(groups)} groups of {group_size} faculty IDs each")
    
    # Process each group 5 times for full automation (repeat each faculty ID 5 times per group)
    cycles_per_group = 5
    all_results = {}
    
    for group_num, group in enumerate(groups, 1):
        print_action(f"=== STARTING GROUP {group_num} of {len(groups)} ===")
        print_action(f"Processing faculty IDs: {group}")
        
        # Process this group 5 times
        for cycle_num in range(1, cycles_per_group + 1):
            print_action(f"--- Cycle {cycle_num} of {cycles_per_group} for Group {group_num} ---")
            
            # Process the 5 faculty IDs in this group
            batch_results = process_batch(group, group_num, take_screenshot=take_screenshots)
            
            # Update results dictionary (keep the best result for each faculty ID)
            for result in batch_results:
                faculty = result['faculty_id']
                if faculty not in all_results or result['success']:
                    all_results[faculty] = result
            
            # Progress update
            successful_so_far = sum(1 for r in all_results.values() if r['success'])
            progress_percent = (successful_so_far / len(faculty_ids)) * 100
            print_action(f"Overall Progress: {successful_so_far}/{len(faculty_ids)} successful ({progress_percent:.1f}%)")
            
            # Save intermediate results after each cycle
            with open('faculty_automation_results_temp.txt', 'w') as f:
                f.write("Faculty ID,Status,Message,Timestamp,Attempts,Group,Cycle\n")
                for faculty, result in all_results.items():
                    status = "SUCCESS" if result['success'] else "FAILED"
                    attempts = result.get('attempts', 1)
                    f.write(f"{faculty},{status},{result['message']},{result['timestamp']},{attempts},{group_num},{cycle_num}\n")
            print_action("Intermediate results saved")
            
            # Add delay between cycles
            if cycle_num < cycles_per_group:
                delay = random.uniform(2, 5)
                print_action(f"Waiting {delay:.1f}s before next cycle...")
                time.sleep(delay)
        
        # Summary for this group
        group_successful = sum(1 for faculty in group if faculty in all_results and all_results[faculty]['success'])
        print_action(f"=== GROUP {group_num} COMPLETE: {group_successful}/{len(group)} successful ===")
        
        # Add delay between groups
        if group_num < len(groups):
            group_delay = random.uniform(5, 10)
            print_action(f"Waiting {group_delay:.1f}s before next group...")
            time.sleep(group_delay)
    
    # Convert results dictionary to list for final processing
    final_results = list(all_results.values())
    
    # Final summary
    end_time = time.time()
    total_time = end_time - start_time
    print_action("=== ALL GROUPS COMPLETE ===")
    total_successful = sum(1 for r in final_results if r['success'])
    total_failed = len(final_results) - total_successful
    print_action(f"Total: {len(final_results)} faculty IDs processed")
    print_action(f"Successful: {total_successful}")
    print_action(f"Failed: {total_failed}")
    print_action(f"Success Rate: {(total_successful/len(final_results)*100):.1f}%")
    if len(final_results) > 0:
        print_action(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print_action(f"Average time per faculty ID: {total_time/len(final_results):.2f} seconds")
    
    # Save results to file
    with open('faculty_automation_results.txt', 'w') as f:
        f.write("Faculty ID,Status,Message,Timestamp,Attempts\n")
        for result in final_results:
            status = "SUCCESS" if result['success'] else "FAILED"
            attempts = result.get('attempts', 1)
            f.write(f"{result['faculty_id']},{status},{result['message']},{result['timestamp']},{attempts}\n")
    
    print_action("Results saved to faculty_automation_results.txt")

if __name__ == "__main__":
    main()
