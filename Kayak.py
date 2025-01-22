import time
import random
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Kayak:
    def __init__(self, user_agent):
        try:
            path = "C:\\Users\\User\\Desktop\\ScrapingFlights\\chromedriver.exe"
            self.chromeOptions = Options()
            self.chromeOptions.add_argument(f"user-agent={user_agent}")
            self.chromeOptions.add_argument('--disable-extensions')
            self.chromeOptions.add_argument('--disable-infobars')
            self.chromeOptions.add_argument('--incognito')
            self.chromeOptions.add_argument('--disable-plugins-discovery')
            self.chromeOptions.add_argument('--headless')  # Run in headless mode
            self.chromeOptions.add_argument('--start-maximized')

            service = Service(path)
            self.driver = webdriver.Chrome(service=service, options=self.chromeOptions)
            width = 1200
            height = 1200
            self.driver.set_window_size(width, height)
            self.driver.set_window_position(0, 0)
        except Exception as e:
            print("Problem initializing the Chrome driver:", e)

    def scroll_and_load_flights(self, writer, origin, destination, date):
        """
        Scroll incrementally and load flight containers dynamically while scrolling.
        Write to the CSV file as flights are scraped.
        """
        flight_data_list = []  # Initialize flight_data_list here
        try:
            # Wait until the flight containers are visible
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'Fxw9')]/div"))
            )
            print("Flight containers are now visible.")
            time.sleep(random.uniform(2, 4))  # Pause after loading the containers

            retry_count = 0  # Initialize retry counter

            while True:
                flight_containers = self.driver.find_elements(By.XPATH, "//div[contains(@class,'Fxw9')]/div")
                print(f"Found {len(flight_containers)} flight containers so far.")

                for container in flight_containers[len(flight_data_list):]:  # Process only new containers
                    try:
                        time.sleep(random.uniform(1, 2)) 
                        # Check if the container has a departure time element (to filter out ads)
                        if not container.find_elements(By.XPATH, ".//ol/li/div/div/div[2]/div[1]/span[1]"):
                            print("Skipped an advertisement or invalid container.")
                            continue
                        # Wait for the departure time element
                        departure_time_element = WebDriverWait(container, 10).until(
                            EC.presence_of_element_located((By.XPATH, ".//ol/li/div/div/div[2]/div[1]/span[1]"))
                        )
                        departure_time = departure_time_element.text

                        # Handle arrival time with potential superscript (+1)
                        arrival_time_element = WebDriverWait(container, 10).until(
                            EC.presence_of_element_located((By.XPATH, ".//ol/li/div/div/div[2]/div[1]/span[3]"))
                        )
                        arrival_time = arrival_time_element.text.strip()

                        try:
                            superscript_element = arrival_time_element.find_element(By.XPATH, ".//sup")
                            superscript_text = superscript_element.text.strip()
                            if superscript_text not in arrival_time:
                                arrival_time = f"{arrival_time}{superscript_text}"
                        except Exception:
                            superscript_text = ""

                        arrival_time = arrival_time.replace("\n", "").strip()

                        stops = container.find_element(By.XPATH, ".//ol/li/div/div/div[3]/div[1]/span").text
                        duration = container.find_element(By.XPATH, ".//ol/li/div/div/div[4]/div[1]").text

                        # Generalized XPath for the company name
                        company_name_xpath = "J0g6-operator-text"
                        try:
                            company_name = container.find_element(By.CLASS_NAME, company_name_xpath).text
                        except Exception:
                            company_name = "None"

                        try:
                            stop_airport = container.find_element(By.XPATH, ".//ol/li/div/div/div[3]/div[2]/span/span").text
                        except Exception:
                            stop_airport = "None"

                        # Extract price
                        try:
                            price_element = WebDriverWait(container, 15).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "f8F1-price-text"))
                            )
                            price = price_element.text
                        except Exception:
                            print(f"Did not find price: {price}")
                            price = "N/A"

                        # Extract seat type
                        try:
                            seat_type_element = WebDriverWait(container, 15).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "DOum-name"))
                            )
                            seat_type = seat_type_element.text
                        except Exception:
                            seat_type = "N/A"

                        # Create a flight data dictionary
                        flight_data = {
                            "Date": date,
                            "Origin": origin,
                            "Destination": destination,
                            "Departure Time": departure_time,
                            "Arrival Time": arrival_time,
                            "Stops": stops,
                            "Stop Airport": stop_airport,
                            "Duration": duration,
                            "Company Name": company_name,
                            "Price": price,
                            "Seat Type": seat_type,
                        }

                        # Write to CSV incrementally
                        writer.writerow(flight_data)
                        file.flush()
                        # Add to local flight data list
                        flight_data_list.append(flight_data)

                        # Reset retry counter since progress was made
                        retry_count = 0

                    except Exception as e:
                        print("Error extracting flight details:", e)
                        continue

                # Scroll a bit to load more flights
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(random.uniform(2, 4))  # Pause between scrolls

                # Check if we've reached the bottom of the page
                if len(flight_containers) == len(flight_data_list):
                    print("No more flights to process. Exiting scroll loop.")
                    break

                # Increment retry count if no progress is made
                retry_count += 1
                if retry_count >= 3:  # Exit if retry count exceeds limit
                    print("Skipping current search due to repeated failures.")
                    return

        except Exception as e:
            print("Error during scrolling and loading:", e)

    def login(self, writer, date, origin, destination):
     max_retries = 8  # Limit the number of retries
     retries = 0

     while retries < max_retries:
         try:
             website = f"https://www.kayak.co.uk/flights/{origin}-{destination}/{date}?sort=price_a"
             self.driver.get(website)
             print(f"Opening URL: {website}")

            # Wait for the page to load
             time.sleep(random.uniform(10, 15))

            # Check for the cookie dialog and click "Accept" if it appears
             try:
                 WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div/div[2]/div/div/div[3]/div/div[1]/button[1]"))
                 ).click()
                 print("Cookies accepted.")
                # If cookies are accepted, proceed with scraping
                 self.scroll_and_load_flights(writer, origin, destination, date)
                 return  # Exit after successful scrape
             except Exception:
                 print("No cookie dialog found, possible CAPTCHA detected.")
                 retries += 1

                 if retries < max_retries:
                     print(f"Retrying with a new user agent. Attempt {retries}/{max_retries}...")
                     # Change user agent and reinitialize the driver
                     self.driver.quit()
                     new_user_agent = random.choice(get_fake_agent())
                     print(f"Switching to new User-Agent: {new_user_agent}")
                     self.__init__(new_user_agent)  # Reinitialize with a new user agent
                     time.sleep(random.uniform(20, 40))  # Wait before retrying to avoid detection
                 else:
                     print("Max retries reached. Skipping this search.")
                     return
         except Exception as e:
             print("An error occurred during login:", e)
             traceback.print_exc()
             retries += 1

         finally:
             if retries >= max_retries:
                 print("Skipping to the next search due to repeated failures.")
                 self.driver.quit()



def get_fake_agent():
    return [
        # Windows Chrome User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.64 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36",

        # macOS Chrome and Safari User Agents
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",

        # Linux Firefox User Agents
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:110.0) Gecko/20100101 Firefox/110.0",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.124 Safari/537.36",

        # Windows Edge User Agents
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.64 Safari/537.36 Edg/113.0.1774.35",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36 Edg/112.0.1722.39",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36 Edg/114.0.1823.43",

        # Additional macOS Safari User Agents
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    ]


# Read input data
with open("KayakParisinput2.txt", "r") as file:
    input_data = [line.strip() for line in file.readlines()]

fake_agents = get_fake_agent()

if not fake_agents:
    print("No fake agents found!")

# Open the CSV file for writing incrementalla
with open("flights_detailsParisf2.csv", mode="w", encoding="utf-8", newline="") as file:
    fieldnames = ["Date", "Origin", "Destination", "Departure Time", "Arrival Time", "Stops", "Stop Airport",
                  "Duration", "Company Name", "Price", "Seat Type"]
    writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()

    for words in input_data:
        word = words.split(",")
        # Convert date from dd/mm/yyyy to yyyy-mm-dd
        date_parts = word[0].split("/")
        date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
        origin, destination = word[1], word[2]

        user_agent = random.choice(fake_agents)
        print(f"Using User-Agent: {user_agent}")

        kayak = Kayak(user_agent)
        kayak.login(writer, date, origin, destination)

print("Scraping completed.")
