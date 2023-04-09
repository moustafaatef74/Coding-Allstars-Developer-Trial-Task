import csv
import random

def read_first_elements(filename: str) -> list:
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader) # skip the first line
        values = [row[0] for row in reader]
        random_values = random.sample(values, 5)
        return random_values
print(read_first_elements("data.csv"))