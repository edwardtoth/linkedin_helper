# LinkedIn Job Helper 
By providing a LinkedIn job url, this application helps in:
- Understanding Desired Skills: Identify the skills required for a particular job.
- Providing Likely Interview Questions: Generate potential interview questions.
- Preparing Questions for the Interviewer: Suggest questions you can ask during the interview.

## Instructions

1. **Install Requirements**:
```
pip install -r requirements.txt
```
2. **Install Playwright: Open your terminal and run**:
```
playwright install
```
3. **Create OpenAI Configuration: Create a file named openai.json with the following content**:
```
{
  "OPENAI_API_KEY": "your_openai_api_key_here"
}
```
4. Run the Application: Start the Streamlit application by running:
```
streamlit run app.py
```
5. Using the UI (Local Host):
- Provide a job URL in the format `https://www.linkedin.com/jobs/view/{job_id}`.
- LinkedIn can detect bots so you may need to click submit again. In that case, a message will pop up `LinkedIn is asking for sign in. Click on "Submit" again.`.
- It takes some time due to the scraping setup and sending prompts to a GPT model.

## Packages Used
1. `playwright` extracts job data from LinkedIn using a provided URL 
2. `sklearn` to find the most relevant sentences using TF-IDF and cosine similarity with keywords in the job descriptions
3. `langchain`'s `ChatOpenAI`:
    - Sends various prompts to OpenAI's GPT-3.5 Turbo for analysis and suggestions
    - GPT-3.5 Turbo is chosen for its cost-effectiveness, though it may not be the most advanced model
4. `streamlit` creates a User Interface 
5.  `chromadb` for storing previous linkedin url and return the result

