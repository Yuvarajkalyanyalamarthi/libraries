import pandas as pd

# 1. Create a sample DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Age': [25, 30, 35, 40],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston'],
    'Salary': [70000, 80000, 90000, 100000]
}

df = pd.DataFrame(data)

print("--- 1. Original DataFrame ---")
print(df)
print("\n")
file_path_alt = r"C:\Users\HP\Downloads\students_with_inter_marks_eamcet.csv"

try:
    df = pd.read_csv(file_path_alt)
    print("--- File Loaded Successfully (using forward slashes) ---")
    print(df.head())

except FileNotFoundError:
    print(f"Error: File not found at path: {file_path_alt}")
except Exception as e:
    print(f"An error occurred: {e}")
    