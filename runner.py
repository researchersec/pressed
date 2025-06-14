import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def get_flaresolverr_session(url, retries=3):
    """Request a session from FlareSolverr to bypass Cloudflare."""
    flaresolverr_url = "http://localhost:8191/v1"
    payload = {
        "cmd": "request.get",
        "url": url,
        "maxTimeout": 180000,  # Increased to 180 seconds
        "returnOnlyCookies": False,
        "render": "full"
    }
    
    session = requests.Session()
    retries = Retry(total=retries, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    
    try:
        response = session.post(flaresolverr_url, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "ok":
            print("FlareSolverr solution received:", json.dumps(data.get("solution"), indent=2))
            return data.get("solution")
        else:
            print(f"FlareSolverr error: {data.get('message')}")
            return None
    except Exception as e:
        print(f"Failed to get FlareSolverr session: {e}")
        return None

def click_team_link(url):
    driver = None
    try:
        # Get FlareSolverr session
        solution = get_flaresolverr_session(url)
        if not solution:
            print("Could not bypass Cloudflare with FlareSolverr")
            return None

        # Set up Chrome options
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--enable-unsafe-swiftshader")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(f"--user-agent={solution['userAgent']}")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        # Initialize the driver
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)

        # Set cookies
        driver.get("https://www.hltv.org")  # Navigate to domain first
        for cookie in solution.get("cookies", []):
            selenium_cookie = {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie.get("domain", ".hltv.org"),
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", True),
                "httpOnly": cookie.get("httpOnly", False),
                "sameSite": cookie.get("sameSite", "Lax")
            }
            try:
                driver.add_cookie(selenium_cookie)
                print(f"Added cookie: {cookie['name']}")
            except Exception as e:
                print(f"Failed to add cookie {cookie['name']}: {e}")

        # Navigate to the page
        driver.get(url)

        # Wait for JavaScript to load
        WebDriverWait(driver, 60).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Get and print the page source for debugging
        soup = BeautifulSoup(driver.page_source, "html.parser")
        print("=== Page Source for Debugging ===")
        print(soup.prettify()[:2000])  # Truncated for brevity

        # Save page source to a file
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        # Check if the target element exists
        elements = driver.find_elements(By.XPATH, '//div[contains(@class, "pick-a-winner-team") and contains(@class, "team2") and contains(@class, "canvote")]')
        if not elements:
            print("No matching elements found for XPath")
            return None

        # Wait for the element to be clickable
        wait = WebDriverWait(driver, 60)
        team_link = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            '//div[contains(@class, "pick-a-winner-team") and contains(@class, "team2") and contains(@class, "canvote")]'
        )))

        # Scroll to element and click using JavaScript
        driver.execute_script("arguments[0].scrollIntoView(true);", team_link)
        driver.execute_script("arguments[0].click();", team_link)
        print("Clicked the team link")

        # Wait briefly to ensure the click action completes
        time.sleep(2)

        # Get the page source after clicking
        soup_after_click = BeautifulSoup(driver.page_source, "html.parser")

        # Save page source after click
        with open("debug_page_after_click.html", "w", encoding="utf-8") as f:
            f.write(soup_after_click.prettify())

        return soup_after_click

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        if driver:
            driver.quit()

# Specific URL for the match
url = "https://www.hltv.org/matches/2382847/big-vs-ex-permitta-dach-masters-season-3-finals"
result = click_team_link(url)
if result:
    print("Successfully clicked the 'ex-Permitta' link and retrieved page source")
else:
    print("Failed to click the link")
