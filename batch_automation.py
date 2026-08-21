from playwright.sync_api import sync_playwright
import concurrent.futures
import time
from datetime import datetime

def print_action(action, username=None):
    """Print action with timestamp and username"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if username:
        print(f"[{timestamp}] [{username}] {action}")
    else:
        print(f"[{timestamp}] {action}")

def generate_roll_numbers():
    """Generate roll numbers from 247Z1A0501 to 247Z1A05Z9"""
    roll_numbers = []
    
    # Generate from 01 to Z9 (hexadecimal style: 0-9, A-Z)
    hex_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # Go through all combinations starting from 01
    for first_char in hex_chars:
        for second_char in hex_chars:
            suffix = f"{first_char}{second_char}"
            roll_number = f"247Z1A05{suffix}"
            
            # Only add if we're starting from 01 or later
            if suffix >= "01":
                roll_numbers.append(roll_number)
            
            # Stop at Z9
            if suffix == "Z9":
                return roll_numbers
    
    return roll_numbers

def process_single_roll_number(roll_number):
    """Process forgot password for a single roll number - simplified and faster"""
    result = {
        'roll_number': roll_number,
        'success': False,
        'message': '',
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    
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
                    '--disable-extensions'
                ]
            )
            page = browser.new_page()
            
            try:
                # Navigate to the website and wait for load
                url = "https://nnrg.beessoftware.cloud/studentselfservice"
                print_action(f"Opening link...", roll_number)
                page.goto(url, wait_until='domcontentloaded')
                page.wait_for_load_state('networkidle')
                print_action("Page loaded", roll_number)
                
                # Find and enter roll number in username field
                print_action(f"Entering roll number: {roll_number}", roll_number)
                username_field = page.locator('#txt_UserName')
                username_field.wait_for(state='visible', timeout=10000)
                username_field.fill(roll_number)
                print_action("Roll number entered", roll_number)
                
                # Click forgot password link
                print_action("Clicking forgot password", roll_number)
                forgot_password_link = page.locator('#lbl_forgotpassword')
                forgot_password_link.wait_for(state='visible', timeout=5000)
                forgot_password_link.click()
                print_action("Forgot password clicked", roll_number)
                
                # Wait a moment for the click to register
                page.wait_for_timeout(1000)
                
                result['message'] = "Completed successfully"
                result['success'] = True
                    
            except Exception as e:
                result['message'] = f"Error: {str(e)}"
                result['success'] = False
                print_action(f"Error: {str(e)}", roll_number)
                
            finally:
                browser.close()
                print_action("Browser closed", roll_number)
                
    except Exception as e:
        result['message'] = f"Browser error: {str(e)}"
        result['success'] = False
        print_action(f"Browser error: {str(e)}", roll_number)
    
    return result

def process_batch(batch, batch_num):
    """Process a batch of roll numbers with optimized parallel processing"""
    print_action(f"=== Starting Batch {batch_num} ===")
    print_action(f"Processing {len(batch)} roll numbers in parallel")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as executor:
        # Submit all tasks at once for maximum parallelism
        future_to_roll = {executor.submit(process_single_roll_number, roll): roll for roll in batch}
        
        # Process as they complete for immediate feedback
        for future in concurrent.futures.as_completed(future_to_roll):
            roll = future_to_roll[future]
            try:
                result = future.result()
                results.append(result)
                status = "✅" if result['success'] else "❌"
                print_action(f"{status} {roll} - {result['message']}", roll)
            except Exception as e:
                print_action(f"❌ {roll} - Exception: {str(e)}", roll)
                results.append({
                    'roll_number': roll,
                    'success': False,
                    'message': f"Exception: {str(e)}",
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
    
    # Summary for this batch
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    print_action(f"=== Batch {batch_num} Complete: {successful} successful, {failed} failed ===")
    
    return results

def main():
    start_time = time.time()
    print_action("Starting Batch Forgot Password Automation")
    print_action("Generating roll numbers from 247Z1A0501 to 247Z1A05Z9")
    
    # Generate roll numbers
    roll_numbers = generate_roll_numbers()
    print_action(f"Generated {len(roll_numbers)} roll numbers")
    
    # For testing, let's use just first 5 roll numbers
    test_mode = False  # Set to False for full automation (run 3 - very fast)
    if test_mode:
        roll_numbers = roll_numbers[:5]
        print_action(f"TEST MODE: Processing first {len(roll_numbers)} roll numbers only")
    
    # Split into batches of 50 for maximum speed (run 3 - very fast)
    batch_size = 50
    batches = [roll_numbers[i:i + batch_size] for i in range(0, len(roll_numbers), batch_size)]
    
    print_action(f"Split into {len(batches)} batches (max {batch_size} roll numbers each)")
    
    # Process each batch
    all_results = []
    try:
        for i, batch in enumerate(batches, 1):
            print_action(f"Starting batch {i} of {len(batches)}")
            batch_results = process_batch(batch, i)
            all_results.extend(batch_results)
            
            # Progress update
            processed_so_far = len(all_results)
            progress_percent = (processed_so_far / len(roll_numbers)) * 100
            print_action(f"Progress: {processed_so_far}/{len(roll_numbers)} ({progress_percent:.1f}%)")
            
            # Save intermediate results less frequently for speed
            if i % 10 == 0:  # Save every 10 batches
                with open('/workspaces/testtt/automation_results_temp.txt', 'w') as f:
                    f.write("Roll Number,Status,Message,Timestamp\n")
                    for result in all_results:
                        status = "SUCCESS" if result['success'] else "FAILED"
                        f.write(f"{result['roll_number']},{status},{result['message']},{result['timestamp']}\n")
                print_action("Intermediate results saved")
            
            # No delay between batches for maximum speed
            if i < len(batches):
                print_action("Starting next batch immediately...")
    except KeyboardInterrupt:
        print_action("!!! PROCESSING INTERRUPTED BY USER !!!")
        print_action(f"Processed {len(all_results)} roll numbers before interruption")
        print_action("Saving partial results...")
    
    # Final summary
    end_time = time.time()
    total_time = end_time - start_time
    print_action("=== PROCESSING COMPLETE ===")
    total_successful = sum(1 for r in all_results if r['success'])
    total_failed = len(all_results) - total_successful
    print_action(f"Total: {len(all_results)} roll numbers processed")
    print_action(f"Successful: {total_successful}")
    print_action(f"Failed: {total_failed}")
    if len(all_results) > 0:
        print_action(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print_action(f"Average time per roll number: {total_time/len(all_results):.2f} seconds")
    
    # Save results to file
    with open('/workspaces/testtt/automation_results.txt', 'w') as f:
        f.write("Roll Number,Status,Message,Timestamp\n")
        for result in all_results:
            status = "SUCCESS" if result['success'] else "FAILED"
            f.write(f"{result['roll_number']},{status},{result['message']},{result['timestamp']}\n")
    
    print_action("Results saved to /workspaces/testtt/automation_results.txt")

if __name__ == "__main__":
    main()