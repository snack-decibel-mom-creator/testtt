def generate_roll_numbers():
    """Generate roll numbers from 247Z1A0401 to 247Z1A04Z9, 247Z1A0501 to 247Z1A05Z9, 247Z1A6601 to 247Z1A66Z9, 247Z1A6701 to 247Z1A67Z9, and 257Z1A0401 to 257Z1A04ZZ, 257Z1A0501 to 257Z1A05ZZ, 257Z1A6601 to 257Z1A66ZZ, 257Z1A6701 to 257Z1A67ZZ"""
    roll_numbers = []
    
    # First character: 0-9, then A-Z
    first_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # Second character: 0-9 only for 247 series, A-Z for 257 series beyond Z9
    second_chars_numeric = "0123456789"
    second_chars_alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # Series identifiers: 04, 05, 66, and 67
    series = ["04", "05", "66", "67"]
    # Prefix identifiers: 247 and 257
    prefixes = ["247", "257"]
    
    # Go through all combinations for each prefix and series
    for prefix in prefixes:
        for series_id in series:
            # For 247 series: stop at Z9
            if prefix == "247":
                for first_char in first_chars:
                    for second_char in second_chars_numeric:
                        suffix = f"{first_char}{second_char}"
                        roll_number = f"{prefix}Z1A{series_id}{suffix}"
                        
                        # Only add if we're starting from 01 or later
                        if suffix >= "01":
                            roll_numbers.append(roll_number)
                        
                        # Stop at Z9 for this series
                        if suffix == "Z9":
                            break
            # For 257 series: continue to ZZ
            else:
                # First part: 01 to Z9
                for first_char in first_chars:
                    for second_char in second_chars_numeric:
                        suffix = f"{first_char}{second_char}"
                        roll_number = f"{prefix}Z1A{series_id}{suffix}"
                        
                        # Only add if we're starting from 01 or later
                        if suffix >= "01":
                            roll_numbers.append(roll_number)
                
                # Second part: AA to ZZ
                for first_char in second_chars_alpha:
                    for second_char in second_chars_alpha:
                        suffix = f"{first_char}{second_char}"
                        roll_number = f"{prefix}Z1A{series_id}{suffix}"
                        roll_numbers.append(roll_number)
    
    return roll_numbers

def main():
    print("Generating roll numbers from 247Z1A (to Z9) and 257Z1A (to ZZ) series with 04, 05, 66, 67 identifiers...")
    roll_numbers = generate_roll_numbers()
    print(f"Generated {len(roll_numbers)} roll numbers")
    
    # Save to text file
    with open('roll_numbers.txt', 'w') as f:
        for roll_number in roll_numbers:
            f.write(f"{roll_number}\n")
    
    print("Roll numbers saved to roll_numbers.txt")
    
    # Display first 10 and last 10 for verification
    print("\nFirst 10 roll numbers:")
    for i in range(min(10, len(roll_numbers))):
        print(f"  {roll_numbers[i]}")
    
    print("\nLast 10 roll numbers:")
    for i in range(max(0, len(roll_numbers)-10), len(roll_numbers)):
        print(f"  {roll_numbers[i]}")

if __name__ == "__main__":
    main()
