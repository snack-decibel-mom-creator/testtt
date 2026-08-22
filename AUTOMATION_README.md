# Faculty Forgot Password Automation

## Summary

This automation system processes faculty institution IDs to trigger forgot password functionality on the faculty portal.

## Files Created/Modified

1. **parse_faculty_data.py** - Parses HTML file to extract faculty names and institution IDs
2. **faculty_institution_ids.csv** - CSV file with 521 faculty entries (497 valid institution IDs)
3. **faculty_automation.py** - Main automation script updated to read from CSV and process IDs
4. **test_single_faculty.py** - Test script for single faculty ID with screenshots
5. **screenshots/** - Directory containing test screenshots

## Extraction Results

- **Total faculty entries**: 521
- **Valid institution IDs**: 497
- **Empty/invalid institution IDs**: 24

## Test Results

✅ **Test with ID 16F5-1568 completed successfully**
- Faculty portal loaded successfully
- Faculty ID entered correctly
- Forgot password link found and clicked using selector: `a:has-text("Forgot")`
- Screenshots captured before and after click
- Both screenshots saved in screenshots/ directory

## Automation Configuration

### Current Settings in faculty_automation.py:
- **test_mode**: False (ready for full automation)
- **take_screenshots**: False (disabled for performance in full automation)
- **cycles_per_group**: 1 (process each group once for efficiency)
- **group_size**: 5 (process 5 IDs in parallel)
- **max_workers**: 5 (maximum concurrent browser instances)

### To Enable Test Mode:
```python
test_mode = True  # Set to True for testing
take_screenshots = True  # Enable screenshots for testing
```

## How to Run

### Full Automation (All 497 valid IDs):
```bash
python faculty_automation.py
```

### Test with Single ID:
1. Edit faculty_automation.py:
   - Set `test_mode = True`
   - Set `take_screenshots = True` (optional)
2. Run:
```bash
python faculty_automation.py
```

### Test with Specific ID:
```bash
python test_single_faculty.py
```
(Edit test_id in the script if needed)

## Automation Process

1. **Load Faculty IDs**: Reads institution IDs from faculty_institution_ids.csv
2. **Group Processing**: Splits IDs into groups of 5
3. **Parallel Processing**: Processes 5 IDs simultaneously using thread pool
4. **Browser Automation**: 
   - Opens faculty portal
   - Enters institution ID in username field
   - Clicks forgot password link
   - Takes screenshot (if enabled)
5. **Retry Logic**: Attempts each ID up to 3 times with exponential backoff
6. **Results Tracking**: Saves intermediate and final results to files

## Output Files

- **faculty_automation_results.txt** - Final results with status for each ID
- **faculty_automation_results_temp.txt** - Intermediate results during processing
- **screenshots/** - Directory for screenshots (if enabled)

## Estimated Time

With 497 valid IDs:
- Groups: ~100 groups of 5 IDs each
- Cycles per group: 1
- Total operations: 497
- Estimated time: ~2-3 hours (depending on network speed and server response)

## Customization

### Change Number of Parallel Workers:
Edit faculty_automation.py, line 171:
```python
max_workers = min(len(batch), 5)  # Change 5 to desired number
```

### Change Group Size:
Edit faculty_automation.py, line 224:
```python
group_size = 5  # Change to desired group size
```

### Enable Screenshots for Full Automation:
Edit faculty_automation.py, line 237:
```python
take_screenshots = True  # Enable screenshots
```

## Notes

- The automation uses headless browser mode for performance
- Multiple selector strategies are used to find the forgot password link
- Random delays are added between operations to avoid overwhelming the server
- All results are logged with timestamps for troubleshooting
- The system automatically handles empty/invalid institution IDs