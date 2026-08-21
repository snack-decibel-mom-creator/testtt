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

def main():
    print("Generating roll numbers from 247Z1A0501 to 247Z1A05Z9 and 247Z1A6601 to 247Z1A66Z9...")
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
