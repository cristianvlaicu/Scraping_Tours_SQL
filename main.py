import requests
import selectorlib
import os
import smtplib, ssl
import time

# URL of the website to scrape
URL = "http://programmer100.pythonanywhere.com/tours/"
# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}


def scrape(url):
    """Scrape the page source from the given URL."""
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def extract(source):
    """Extract the relevant data from the page source using selectorlib."""
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


def send_email(message):
    """Send an email with the given message."""
    host = "smtp.gmail.com"
    port = 465

    username = "lordbeilish13@gmail.com"  # Replace with your email address
    password = os.getenv("password")  # Retrieve password from environment variables
    receiver = "dkelnumero1@gmail.com"  # Replace with the recipient's email address
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)
    print("Email was sent!")


def store(extracted):
    """Store the extracted data in a text file."""
    with open("data.txt", "a") as file:
        file.write(extracted + "\n")


def read(extracted):
    """Read the contents of the data file."""
    with open("data.txt", "r") as file:
        return file.read()


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)  # Scrape the website
        extracted = extract(scraped)  # Extract relevant data
        print(extracted)
        content = read(extracted)  # Read existing data from file

        # Construct the email message
        message = f"""\
Subject: Events open:


Hey, new event was found! {extracted}
        """

        # Check if a new event was found and send an email if it's new
        if extracted != "No upcoming tours":
            if extracted not in content:
                store(extracted)  # Store the new event data
                send_email(message=message)  # Send an email notification

        time.sleep(2)  # Wait for 2 seconds before scraping again