import re
import csv

def parse_faculty_html(file_path):
    """Parse the faculty HTML file to extract faculty names and institution IDs"""
    
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Pattern to find faculty entries
    # Each faculty entry starts with <span>NAME</span> and contains Institution-ID
    faculty_data = []
    
    # Find all faculty entries by looking for span tags with names
    name_pattern = r'<span>([^<]+)</span>'
    names = re.findall(name_pattern, html_content)
    
    # For each name, find the associated institution ID
    for name in names:
        # Clean up the name
        clean_name = name.strip()
        if not clean_name or len(clean_name) < 3:
            continue
            
        # Find the institution ID for this faculty member
        # Look for Institution-ID pattern after the name
        name_index = html_content.find(f'<span>{name}</span>')
        if name_index == -1:
            continue
            
        # Look for Institution-ID in the next 3000 characters after the name (increased search area)
        search_area = html_content[name_index:name_index + 3000]
        inst_id_pattern = r'<td>Institution-ID</td>\s*<td[^>]*>([^<]*)</td>'
        inst_match = re.search(inst_id_pattern, search_area)
        
        if inst_match:
            inst_id = inst_match.group(1).strip()
            # Add all entries, even if institution ID is empty or '-'
            faculty_data.append({
                'name': clean_name,
                'institution_id': inst_id if inst_id else ''
            })
    
    return faculty_data

def create_csv(faculty_data, output_file):
    """Create a CSV file with faculty names and institution IDs"""
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'institution_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for faculty in faculty_data:
            writer.writerow(faculty)
    
    # Statistics
    valid_ids = [f for f in faculty_data if f['institution_id'] and f['institution_id'] != '-']
    empty_ids = [f for f in faculty_data if not f['institution_id'] or f['institution_id'] == '-']
    
    print(f"CSV file created: {output_file}")
    print(f"Total faculty entries: {len(faculty_data)}")
    print(f"Valid institution IDs: {len(valid_ids)}")
    print(f"Empty/invalid institution IDs: {len(empty_ids)}")

if __name__ == "__main__":
    input_file = "raw code of faculty institute ids.txt"
    output_file = "faculty_institution_ids.csv"
    
    print("Parsing faculty HTML file...")
    faculty_data = parse_faculty_html(input_file)
    
    print(f"Found {len(faculty_data)} faculty entries with institution IDs")
    
    print("\nSample data:")
    for i, faculty in enumerate(faculty_data[:5]):
        print(f"{i+1}. {faculty['name']} - {faculty['institution_id']}")
    
    print("\nCreating CSV file...")
    create_csv(faculty_data, output_file)
    
    print("Done!")