import requests
import selectorlib
import os
import smtplib, ssl
import time
import sqlite3

# URL of the website to scrape
URL = "http://programmer100.pythonanywhere.com/tours/"

# Headers to use in the request to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}

# Connect to the SQLite database
connection = sqlite3.connect("data.db")


def scrape(url):
    """Scrape the page source from the given URL."""
    response = requests.get(
        url, headers=HEADERS
    )  # Send a GET request with the specified headers
    source = response.text  # Get the HTML content of the page
    return source


def extract(source):
    """Extract the relevant data from the page source using selectorlib."""
    extractor = selectorlib.Extractor.from_yaml_file(
        "extract.yaml"
    )  # Load the extraction rules from a YAML file
    value = extractor.extract(source)[
        "tours"
    ]  # Extract the 'tours' field from the HTML
    return value


def send_email(message):
    """Send an email with the given message."""
    host = "smtp.gmail.com"  # SMTP server
    port = 465  # Port for SSL

    username = "lordbeilish13@gmail.com"  # Sender email address
    password = os.getenv(
        "password"
    )  # Get the password from environment variables
    receiver = "dkelnumero1@gmail.com"  # Recipient email address
    context = ssl.create_default_context()  # Create a secure SSL context

    with smtplib.SMTP_SSL(
        host, port, context=context
    ) as server:  # Connect to the SMTP server using SSL
        server.login(username, password)  # Login with the credentials
        server.sendmail(username, receiver, message)  # Send the email
    print("Email was sent!")


def store(extracted):
    """Store the extracted data in the database."""
    row = extracted.split(",")  # Split the extracted string into a list
    row = [
        item.strip() for item in row
    ]  # Remove leading/trailing whitespace from each item
    cursor = (
        connection.cursor()
    )  # Create a cursor object to interact with the database
    cursor.execute(
        "INSERT INTO events VALUES(?,?,?)", row
    )  # Insert the data into the 'events' table
    connection.commit()  # Commit the changes to the database


def read(extracted):
    """Read data from the database."""
    row = extracted.split(",")  # Split the extracted string into a list
    row = [
        item.strip() for item in row
    ]  # Remove leading/trailing whitespace from each item
    band, city, date = row  # Unpack the list into individual variables
    cursor = (
        connection.cursor()
    )  # Create a cursor object to interact with the database
    cursor.execute(
        "SELECT * FROM events WHERE band=? AND city=? AND date=?",
        (band, city, date),
    )  # Select rows matching the criteria
    rows = cursor.fetchall()  # Fetch all matching rows
    print(rows)
    return rows


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)  # Scrape the website
        extracted = extract(scraped)  # Extract data from the HTML
        print(extracted)

        # Create the email message
        message = f"""\
Subject: Events open:


Hey, new event was found! {extracted}
        """

        if extracted != "No upcoming tours":  # Check if any events were found
            row = read(
                extracted
            )  # Check if the event already exists in the database
            if not row:  # If the event is new
                store(extracted)  # Store the event in the database
                send_email(message=message)  # Send an email notification
        time.sleep(1)  # Wait for 1 second before scraping again
