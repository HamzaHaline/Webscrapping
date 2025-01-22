from datetime import datetime

# Function to convert a date from DD/MM/YYYY to YYYY-MM-DD
def convert_date_format(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: {date_str}")
        return None

# Function to read the input file, reformat dates, and save the output
def reformat_dates(input_file, output_file):
    try:
        with open(input_file, "r") as infile, open(output_file, "w") as outfile:
            lines = infile.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                try:
                    # Parse the line into components
                    departure_date, origin, destination = line.split(",")
                    # Convert the date format
                    reformatted_date = convert_date_format(departure_date)
                    if not reformatted_date:
                        continue  # Skip lines with invalid dates

                    # Write the reformatted line to the output file
                    outfile.write(f"{reformatted_date},{origin},{destination}\n")
                except ValueError:
                    print(f"Invalid line format: {line}")
                    continue

        print(f"Reformatted dates saved to {output_file}")

    except FileNotFoundError:
        print(f"Input file {input_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main script
if __name__ == "__main__":
    input_file = "api.txt"  # Input file with original dates
    output_file = "api_reformatted.txt"  # Output file with reformatted dates

    reformat_dates(input_file, output_file)