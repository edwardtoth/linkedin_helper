import re
import pandas as pd
import asyncio
import random
import logging
from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(level=logging.INFO)

class LinkedInScraper:
    @staticmethod
    async def playwright_setup():
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        logging.info("Playwright setup complete.")
        return playwright, page

    @staticmethod
    async def open_url(page, url):
        while True:
            try:
                validate_job_url(url)
                await page.goto(url, wait_until="networkidle")  # Wait until network is idle
                logging.info(f"Successfully opened url: {url}")
                return
            except Exception as e:
                logging.warning(f"Error occurred while opening {url}: {e}. Retrying...")


    @staticmethod
    async def simulate_human_behavior(page, x=100, y=200, min_time=2, max_time=5):
        """LinkedIn can detect a bot and asks you to sign in. To overcome that, 
        simulate human behavior with a random delay and mouse click.
        """
        delay = random.uniform(min_time, max_time)
        logging.info(f"Delaying for {delay:.2f} seconds.")
        await asyncio.sleep(delay)
        await page.hover('button[aria-label="Share"]')
        await page.mouse.click(x, y)
        logging.info(f"Clicked at coordinates: ({x}, {y}).")
        
        
    @staticmethod
    async def scrap_company_data(page):
        await page.wait_for_load_state("networkidle")  # Ensure the page is fully loaded
        # Avoid bot detection by simulating human behavior
        LinkedInScraper.simulate_human_behavior(page)
        title_element = await page.title()
        logging.info(f"Page title: {title_element}")
        if (title_element == '') | ('sign up' in title_element.lower()):
            logging.error("LinkedIn is asking for sign in. Click on `Submit` again.")
            raise Exception("LinkedIn is asking for sign in. Click on `Submit` again.")
        
        div_element = await page.query_selector('div.show-more-less-html__markup')
        job_content = await div_element.text_content() if div_element else 'Description Not Found'
        job_details = extract_job_details(title_element)
        df = pd.DataFrame([job_details], columns=['Company Name', 'Job Title', 'Location'])
        df['Description'] = job_content
        df = df.dropna().reset_index(drop=True)
        logging.info("Company data scraped successfully.")
        return df
    
    
def extract_job_details(title_text):
    """Extracts company name, job title, and location from the title text.
    Assuming that the title text is in the format:
    {Company} hiring {Job Position} in {Location}
    This is true for job urls in this format:
    https://www.LinkedIn.com/jobs/view/{job_id}
    """
    pattern = r'^(.*?)\s+hiring\s+(.*?)\s+in\s+(.*?),\s+.*\| LinkedIn$'
    match = re.search(pattern, title_text)
    
    if match:
        company_name, job_title, location = match.groups()
        return [company_name, job_title, location]
    return []


def validate_job_url(url):
    """Job URL must be in the format https://www.linkedin.com/jobs/view/{job_id}
    raise error if the URL is invalid."""
    if not re.match(r'^https://www.linkedin.com/jobs/view/\d+/?$', url):
        raise ValueError("Invalid LinkedIn Job URL. Please provide in format https://www.linkedin.com/jobs/view/{job_id}")
    return url
