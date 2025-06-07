from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def click_team_link(url):
    try:
        # Set up Chrome options
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--enable-unsafe-swiftshader")

        # Initialize the driver
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(15)
        driver.set_script_timeout(15)

        # Navigate to the page
        driver.get(url)

        # Get and print the page source for debugging
        soup = BeautifulSoup(driver.page_source, "html.parser")
        print("=== Page Source for Debugging ===")
        print(soup.prettify())

        # Save page source to a file for further inspection
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        # Wait for the element to be clickable
        wait = WebDriverWait(driver, 10)
        team_link = wait.until(EC.element_to_be_clickable((
            By.XPATH, 
            '//div[@class="pick-a-winner-team team2 canvote" and @data-pick-a-winner-team="2"]'
        )))

        # Click the element
        team_link.click()

        # Wait briefly to ensure the click action completes
        time.sleep(2)

        # Get the page source after clicking
        soup_after_click = BeautifulSoup(driver.page_source, "html.parser")

        # Return the soup for further processing if needed
        return soup_after_click

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        driver.quit()

# Specific URL for the match
url = "https://www.hltv.org/matches/2382847/big-vs-ex-permitta-dach-masters-season-3-finals"
result = click_team_link(url)
if result:
    print("Successfully clicked the 'ex-Permitta' link and retrieved page source")
else:
    print("Failed to click the link")
