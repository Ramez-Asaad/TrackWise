import os
import csv
import sys
from pymongo.errors import BulkWriteError

# Add the UI directory to the path to access course_db
current_dir = os.path.dirname(os.path.abspath(__file__))
ui_dir = os.path.join(current_dir, 'UI')
if ui_dir not in sys.path:
    sys.path.insert(0, ui_dir)

from course_db import migrate_courses_from_csv, get_all_courses

def update_courses():
    """Update courses in MongoDB from DATA.csv"""
    try:
        # Get the path to DATA.csv
        csv_path = os.path.join(current_dir, 'DATA.csv')
        if not os.path.exists(csv_path):
            print(f"Error: Could not find {csv_path}")
            sys.exit(1)
        
        print(f"Updating courses from {csv_path}...")
        
        # Use the existing migration function
        success = migrate_courses_from_csv(csv_path)
        
        if success:
            # Verify the update
            courses = get_all_courses()
            print(f"\nVerification:")
            print(f"Total courses in database: {len(courses)}")
            print("\nSample of courses:")
            for course in courses[:5]:  # Show first 5 courses
                print(f"- {course['course_code']}: {course['course_name']}")
        else:
            print("Failed to update courses.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    update_courses() 