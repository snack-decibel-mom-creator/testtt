from playwright.sync_api import sync_playwright
import concurrent.futures
import time
from datetime import datetime
import random
import os

def print_action(action, username=None):
    """Print action with timestamp and username"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if username:
        print(f"[{timestamp}] [{username}] {action}")
    else:
        print(f"[{timestamp}] {action}")

def generate_roll_numbers():
    """Generate roll numbers from 247Z1A0501 to 247Z1A05Z9 and 247Z1A6601 to 247Z1A66Z9"""
    roll_numbers = []
    
    # First character: 0-9, then A-Z
    first_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # Second character: 0-9 only
    second_chars = "0123456789"
    # Series identifiers: 05 and 66
    series = ["05", "66"]
    
    # Go through all combinations for each series
    for series_id in series:
        for first_char in first_chars:
            for second_char in second_chars:
                suffix = f"{first_char}{second_char}"
                roll_number = f"247Z1A{series_id}{suffix}"
                
                # Only add if we're starting from 01 or later
                if suffix >= "01":
                    roll_numbers.append(roll_number)
                
                # Stop at Z9 for this series
                if suffix == "Z9":
                    break
    
    return roll_numbers

def process_single_roll_number(roll_number, max_retries=3):
    """Process forgot password for a single roll number with retry logic"""
    result = {
        'roll_number': roll_number,
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
                    # Navigate to the website and wait for load
                    url = "https://nnrg.beessoftware.cloud/studentselfservice"
                    print_action(f"Opening link... (Attempt {attempt + 1}/{max_retries})", roll_number)
                    
                    # Set longer timeout for page load
                    page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    
                    # Wait for network to be idle with longer timeout
                    try:
                        page.wait_for_load_state('networkidle', timeout=30000)
                    except:
                        # If networkidle fails, continue anyway as page might be functional
                        pass
                    
                    print_action("Page loaded", roll_number)
                    
                    # Add small random delay to avoid overwhelming server
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    # Find and enter roll number in username field
                    print_action(f"Entering roll number: {roll_number}", roll_number)
                    username_field = page.locator('#txt_UserName')
                    username_field.wait_for(state='visible', timeout=15000)
                    username_field.fill(roll_number)
                    print_action("Roll number entered", roll_number)
                    
                    # Small delay before clicking
                    time.sleep(random.uniform(0.3, 0.8))
                    
                    # Click forgot password link
                    print_action("Clicking forgot password", roll_number)
                    forgot_password_link = page.locator('#lbl_forgotpassword')
                    forgot_password_link.wait_for(state='visible', timeout=10000)
                    forgot_password_link.click()
                    print_action("Forgot password clicked", roll_number)
                    
                    # Wait a moment for the click to register
                    page.wait_for_timeout(2000)
                    
                    result['message'] = "Completed successfully"
                    result['success'] = True
                    break  # Success - exit retry loop
                        
                except Exception as e:
                    error_msg = str(e)
                    result['message'] = f"Error (Attempt {attempt + 1}/{max_retries}): {error_msg}"
                    print_action(f"Error (Attempt {attempt + 1}/{max_retries}): {error_msg}", roll_number)
                    
                    if attempt < max_retries - 1:
                        # Wait before retry with exponential backoff
                        wait_time = (2 ** attempt) * random.uniform(1, 3)
                        print_action(f"Retrying in {wait_time:.1f}s...", roll_number)
                        time.sleep(wait_time)
                    else:
                        result['success'] = False
                        
                finally:
                    browser.close()
                    print_action("Browser closed", roll_number)
                    
        except Exception as e:
            error_msg = str(e)
            result['message'] = f"Browser error (Attempt {attempt + 1}/{max_retries}): {error_msg}"
            print_action(f"Browser error (Attempt {attempt + 1}/{max_retries}): {error_msg}", roll_number)
            
            if attempt < max_retries - 1:
                # Wait before retry with exponential backoff
                wait_time = (2 ** attempt) * random.uniform(1, 3)
                print_action(f"Retrying in {wait_time:.1f}s...", roll_number)
                time.sleep(wait_time)
            else:
                result['success'] = False
    
    return result

def process_batch(batch, batch_num):
    """Process a batch of roll numbers with optimized parallel processing"""
    print_action(f"=== Starting Batch {batch_num} ===")
    print_action(f"Processing {len(batch)} roll numbers in parallel")
    
    results = []
    # Use exactly 5 workers or the batch size if smaller
    max_workers = min(len(batch), 5)  # Max 5 concurrent workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks at once
        future_to_roll = {executor.submit(process_single_roll_number, roll): roll for roll in batch}
        
        # Process as they complete for immediate feedback
        for future in concurrent.futures.as_completed(future_to_roll):
            roll = future_to_roll[future]
            try:
                result = future.result()
                results.append(result)
                status = "✅" if result['success'] else "❌"
                attempt_info = f" (Attempt {result['attempts']})" if 'attempts' in result else ""
                print_action(f"{status} {roll}{attempt_info} - {result['message']}", roll)
            except Exception as e:
                print_action(f"❌ {roll} - Exception: {str(e)}", roll)
                results.append({
                    'roll_number': roll,
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
    print_action("Starting Batch Forgot Password Automation")
    print_action("Generating roll numbers from 247Z1A0501 to 247Z1A05Z9 and 247Z1A6601 to 247Z1A66Z9")
    
    # Generate roll numbers
    roll_numbers = generate_roll_numbers()
    print_action(f"Generated {len(roll_numbers)} roll numbers")
    
    # For testing, let's use just first 5 roll numbers
    test_mode = False  # Set to False for full automation
    if test_mode:
        roll_numbers = roll_numbers[:10]  # Test with 2 groups
        print_action(f"TEST MODE: Processing first {len(roll_numbers)} roll numbers only")
    
    # Split into groups of 5 roll numbers
    group_size = 5
    groups = [roll_numbers[i:i + group_size] for i in range(0, len(roll_numbers), group_size)]
    
    print_action(f"Split into {len(groups)} groups of {group_size} roll numbers each")
    
    # Process each group 5 times before moving to next group
    cycles_per_group = 5
    all_results = {}
    
    for group_num, group in enumerate(groups, 1):
        print_action(f"=== STARTING GROUP {group_num} of {len(groups)} ===")
        print_action(f"Processing roll numbers: {group}")
        
        # Process this group 5 times
        for cycle_num in range(1, cycles_per_group + 1):
            print_action(f"--- Cycle {cycle_num} of {cycles_per_group} for Group {group_num} ---")
            
            # Process the 5 roll numbers in this group
            batch_results = process_batch(group, group_num)
            
            # Update results dictionary (keep the best result for each roll number)
            for result in batch_results:
                roll = result['roll_number']
                if roll not in all_results or result['success']:
                    all_results[roll] = result
            
            # Progress update
            successful_so_far = sum(1 for r in all_results.values() if r['success'])
            progress_percent = (successful_so_far / len(roll_numbers)) * 100
            print_action(f"Overall Progress: {successful_so_far}/{len(roll_numbers)} successful ({progress_percent:.1f}%)")
            
            # Save intermediate results after each cycle
            with open('automation_results_temp.txt', 'w') as f:
                f.write("Roll Number,Status,Message,Timestamp,Attempts,Group,Cycle\n")
                for roll, result in all_results.items():
                    status = "SUCCESS" if result['success'] else "FAILED"
                    attempts = result.get('attempts', 1)
                    f.write(f"{roll},{status},{result['message']},{result['timestamp']},{attempts},{group_num},{cycle_num}\n")
            print_action("Intermediate results saved")
            
            # Add delay between cycles
            if cycle_num < cycles_per_group:
                delay = random.uniform(2, 5)
                print_action(f"Waiting {delay:.1f}s before next cycle...")
                time.sleep(delay)
        
        # Summary for this group
        group_successful = sum(1 for roll in group if roll in all_results and all_results[roll]['success'])
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
    print_action(f"Total: {len(final_results)} roll numbers processed")
    print_action(f"Successful: {total_successful}")
    print_action(f"Failed: {total_failed}")
    print_action(f"Success Rate: {(total_successful/len(final_results)*100):.1f}%")
    if len(final_results) > 0:
        print_action(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print_action(f"Average time per roll number: {total_time/len(final_results):.2f} seconds")
    
    # Save results to file
    with open('automation_results.txt', 'w') as f:
        f.write("Roll Number,Status,Message,Timestamp,Attempts\n")
        for result in final_results:
            status = "SUCCESS" if result['success'] else "FAILED"
            attempts = result.get('attempts', 1)
            f.write(f"{result['roll_number']},{status},{result['message']},{result['timestamp']},{attempts}\n")
    
    print_action("Results saved to automation_results.txt")

if __name__ == "__main__":
    main()