# scrape.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_website(website):
    print("Opening local Chrome browser...")
    
    options = Options()
    # options.add_argument("--headless")  # optional
    driver = webdriver.Chrome(options=options)

    driver.get(website)

    print("You have 30 seconds to solve any CAPTCHA manually...")

    try:
        # Wait for the body of the page to be present, for a maximum of 30 seconds
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print("Scraping page content...")
        html = driver.page_source
    
    except Exception as e:
        print(f"An error occurred while waiting for the page to load: {e}")
        html = ""

    finally:
        driver.quit()
        
    return html


def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    return str(body_content) if body_content else ""


def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    return cleaned_content


# --- CHANGED LINE ---
# Increased max_length to reduce the number of API calls. Gemini Pro can handle this.
def split_dom_content(dom_content, max_length=10000):
    """Splits the content into chunks. Gemini can handle large chunks."""
    return [dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)]