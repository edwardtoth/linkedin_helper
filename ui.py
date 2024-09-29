"""This script creates the Streamlit user interface."""
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space


def streamlit_config():
    """Streamlit Configuration Setup"""
    st.set_page_config(page_title='LinkedIn Helper', layout="wide")
    page_background_color = """
    <style>
    [data-testid="stHeader"] 
    {
    background: rgba(0,0,0,0);
    }
    </style>
    """
    st.markdown(page_background_color, unsafe_allow_html=True)

    # title and position
    st.markdown(f'<h1 style="text-align: center;">LinkedIn Job Helper </h1>',
                unsafe_allow_html=True)
    
    # Add a description about the application's purpose
    st.markdown(f'''<p style="text-align: left;">
                    <strong>This application helps in </strong>:
                    <ol>
                        <li>Understanding desired skills for a particular job</li>
                        <li>Providing likely interview questions</li>
                        <li>Preparing questions for the interviewer</li>
                    </ol>
                    </p>''', unsafe_allow_html=True)
    # GPT-4o Mini 
    st.markdown(f'''<p style="text-align: left;">
                        <strong>How This Application Works </strong>:
                        <ol>
                            <li>Extract data from LinkedIn given a URL</li>
                            <li>Identify the most relevant sentences using TF-IDF and cosine similarity</li>
                            <li>Send various prompts to OpenAI's GPT-3.5 Turbo (chosen for its cost-effectiveness, though it may not be the most advanced)</li>
                        </ol>
                        </p>''', unsafe_allow_html=True)
    
    st.markdown(f'''<p style="text-align: left;">
                            <strong>Future Enhancements (Coming Soon)</strong>:
                            <ul>
                                <li>Upload your own resume</li>
                                <li>Compare your resume with required skills and recommend relevant skills or courses</li>
                                <li>Evaluate the likelihood of matching a job based on your resume</li>
                            </ul>
                            </p>''', unsafe_allow_html=True)


def get_job_input():
    add_vertical_space(2)
    with st.form(key='job_scraper'):
        add_vertical_space(1)
        job_url = st.text_input(label='LinkedIn Job Url')
        add_vertical_space(1)
        submit = st.form_submit_button(label='Submit')
        add_vertical_space(1)
    return job_url, submit


def display_data_userinterface(df_final):
    # Display the Data in User Interface
    add_vertical_space(1)
    if df_final.shape[0] !=1:
        raise ValueError('DataFrame should have only 1 row')
    
    if df_final is not None:
        st.markdown(f'<h3 style="color: orange;">Job Posting Details : </h3>', unsafe_allow_html=True)
        st.write(f"Company Name : {df_final['Company Name'][0]}")
        st.write(f"Job Title    : {df_final['Job Title'][0]}")
        st.write(f"Location     : {df_final['Location'][0]}")
        with st.expander(label='Full Job Description'):
            st.write(df_final['Description'][0])
            
        add_vertical_space(3)
        # Examples
        if 'Skills' not in df_final:
            df_final['Skills'] = """
            - Gen AI
            - Product Management
            """
        if 'Interview Questions' not in df_final:
            df_final['Interview'] = """
            - Tell me about yourself.
            - What are your strengths and weaknesses?
            """
        if 'Questions for Interviewer' not in df_final:
            df_final['Questions for Interviewer'] = """
            - How would you describe the working culture?
            - What is the team like and who do you work with most frequently?
            """
        st.markdown(f'<h4 style="color: orange;">Recommendations [by GPT-3.5 Turbo]: </h4>', unsafe_allow_html=True)
        with st.expander(label='Recommended Skills'):
            st.markdown(df_final['Skills'][0])

        with st.expander(label='Expected Interview Questions'):
            st.markdown(f"""
            {df_final['Interview Questions'][0]}
            """)

        with st.expander(label='Questions for Interviewer'):
            st.markdown(f"""
            **Questions for Interviewer:**
            {df_final['Questions for Interviewer'][0]}
            """)
                
    else:
        st.markdown(f'<h5 style="text-align: center;color: orange;">No Matching Jobs Found</h5>', 
                            unsafe_allow_html=True)

                
# def parse_job_description(file_path):
#     with open(file_path, 'r') as file:
#         content = file.read()
    
#     # Define patterns to extract information
#     patterns = {
#         'Company Name': r'Company Name\s*:\s*(.*?)\nJob Title',
#         'Job Title': r'Job Title\s*:\s*(.*)\nLocation',
#         'Location': r'Location\s*:\s*(.*)\nWebsite',
#         'Website URL':  r'Website URL\s*:\s*(.*?)\n+Job Description',
#         'Description': r'Job Description:\s*(.*?)(?:$)',
#     }

#     # Extract information using regular expressions
#     extracted_info = {}
#     for key, pattern in patterns.items():
#         match = re.search(pattern, content, re.DOTALL)
#         if match:
#             extracted_info[key] = match.group(1).strip()
    
#     df = pd.DataFrame([extracted_info])
#     return df
