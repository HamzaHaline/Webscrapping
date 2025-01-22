import datetime


paris_airports = ['CDG', 'ORY']


destination_airports = [
    'LHR',  # London Heathrow, United Kingdom
    'JFK',  # John F. Kennedy International, New York, USA
    'HND',  # Tokyo Haneda, Japan
    'DXB',  # Dubai International, United Arab Emirates
    'SIN',  # Singapore Changi, Singapore
    'SYD',  # Sydney Kingsford Smith, Australia
    'GRU',  # São Paulo-Guarulhos, Brazil
    'PEK',  # Beijing Capital International, China
    'JNB',  # O.R. Tambo International, Johannesburg, South Africa
    'LAX',  # Los Angeles International, USA
    'FRA',  # Frankfurt am Main Airport, Germany
    'AMS',  # Amsterdam Airport Schiphol, Netherlands
    'MAD',  # Adolfo Suárez Madrid–Barajas, Spain
    'FCO',  # Leonardo da Vinci–Fiumicino Airport, Rome, Italy
    'IST',  # Istanbul Airport, Turkey
    'MEX',  # Mexico City International Airport, Mexico
    'YYZ',  # Toronto Pearson International Airport, Canada
    'BOM',  # Chhatrapati Shivaji Maharaj International Airport, Mumbai, India
    'ICN',  # Incheon International Airport, Seoul, South Korea
    'BKK',  # Suvarnabhumi Airport, Bangkok, Thailand
]


start_date = datetime.date(2025, 2, 1)  
end_date = datetime.date(2025, 4, 30)  


date_list = [
    (start_date + datetime.timedelta(days=x)).strftime('%d/%m/%Y')
    for x in range((end_date - start_date).days + 1)
]


flight_entries = []
for date in date_list:
    for origin in paris_airports:
        for destination in destination_airports:
            flight_entries.append(f"{date},{origin},{destination}")


with open('kayakParisinput2.txt', 'w') as file:
    for entry in flight_entries:
        file.write(entry + '\n')

print(f"Generated {len(flight_entries)} flight entries in 'kayakinput.txt'.")
