import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.add_vertical_space import add_vertical_space
from linkedin_scraper import LinkedInScraper
from ui import get_job_input, display_data_userinterface, streamlit_config
import asyncio
from gpt_model import GPTModel
import warnings
warnings.filterwarnings('ignore')
from chromadb import PersistentClient
import re
import pandas as pd
import json
import logging 
logging.basicConfig(level=logging.INFO)

# Initialize ChromaDB client and create a collection
client = PersistentClient(path="chromadb-cache")
# Check if the collection already exists
collection_name = "job_data"
try:
    collection = client.create_collection(collection_name)
except Exception:
    collection = client.get_collection(collection_name)

async def fetch_job_data(job_url): 
    # Check if job data exists in ChromaDB
    existing_data = await asyncio.to_thread(collection.query, 
                                            query_texts=[job_url], n_results=1,
                                            where={"metadata_field": "is_equal_to_this"})
    json_str = existing_data['documents']
    if json_str != [[]]:
        logging.info(f"Existing_data for url: {job_url}")
        # Return cached data if it exists
        parsed_json = json.loads(json_str[0][0])
        # Convert the parsed JSON to a DataFrame
        df = pd.DataFrame(parsed_json)
        logging.info(f"Existing_data: {  df[['Company Name', 'Job Title', 'Location']] }")
        return df

    # If not in cache, perform scraping
    playwright, page = await LinkedInScraper.playwright_setup()
    try:
        await LinkedInScraper.open_url(page, job_url)
        
        with st.spinner('Retrieving Job Information...'):
            df_final = await LinkedInScraper.scrap_company_data(page)

        with st.spinner('Sending Data to GPT Model...'):
            # Send to GPT Model for Analysis
            df_final = GPTModel.get_likedin_help(df_final)
        
        logging.info(f"Data return from GPT: {df_final}")
        # Store the data in ChromaDB for caching
        job_id = re.search(r'/(\d+)/?', job_url).group(1)
        await asyncio.to_thread(
            collection.add,
            documents=df_final.to_json(orient='records'),
            metadatas=[{"job_url": job_url}],  # Only one metadata entry needed
            ids=[str(job_id)]  # Only one unique ID needed
        )
        return df_final
    finally:
        if page:
            await page.close()
        if playwright:
            await playwright.stop()
            
            
async def run_scraper():
    try:
        # Get the Job URL and Submit Button from the User input
        job_url, submit = get_job_input()
        add_vertical_space(2)
        if submit:
            if job_url:
                df_final = await fetch_job_data(job_url)
                display_data_userinterface(df_final)
            else:
                st.markdown(f'<h5 style="text-align: center;color: orange;">Job URL is Required</h5>', 
                            unsafe_allow_html=True)
    except Exception as e:
        add_vertical_space(2)
        st.markdown(f'<h5 style="text-align: center;color: orange;">{e}</h5>', unsafe_allow_html=True)
    

async def main():
    streamlit_config()
    with st.sidebar:
        add_vertical_space(2)
        option = option_menu(menu_title='', options=['Job Preparation'],
                            icons=['linkedin'])

    # Run the scraper function if the selected option is 'Job Preparation'
    if option == 'Job Preparation':
        await run_scraper()
        
        
if __name__ == '__main__':
    asyncio.run(main())