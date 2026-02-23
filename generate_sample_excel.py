import pandas as pd
import numpy as np
import os

def create_sample_excel():
    # Create a simple dataset
    data = {
        'Project': ['Project A', 'Project A', 'Project B', 'Project B', 'Project C'],
        'Status': ['Done', 'In Progress', 'Done', 'To Do', 'Done'],
        'Assignee': ['Alice', 'Bob', 'Charlie', 'Alice', 'Bob'],
        'Story Points': [5, 3, 8, 2, 5]
    }
    df = pd.DataFrame(data)

    # Create a mock pivot table structure (what JIRA might output)
    pivot_data = [
        ["", "", "", ""],
        ["JIRA Issue Report - March 2026", "", "", ""],
        ["", "", "", ""],
        ["Status Summary Pivot", "", "", ""],  # This is our pivot heading
        ["Assignee", "Done", "In Progress", "To Do"],
        ["Alice", 5, 0, 2],
        ["Bob", 5, 3, 0],
        ["Charlie", 8, 0, 0],
        ["Grand Total", 18, 3, 2],
        ["", "", "", ""],
        ["Another Pivot Table", "", "", ""],
        ["Project", "Total Points", "", ""],
        ["Project A", 8, "", ""],
        ["Project B", 10, "", ""],
        ["Project C", 5, "", ""]
    ]
    
    pivot_df = pd.DataFrame(pivot_data)

    # Save to Excel
    file_path = os.path.join(os.path.dirname(__file__), "sample_jira_report.xlsx")
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Raw Data', index=False)
        pivot_df.to_excel(writer, sheet_name='Pivot Sheets', index=False, header=False)
        
    print(f"Sample Excel file created at: {file_path}")

if __name__ == "__main__":
    create_sample_excel()
