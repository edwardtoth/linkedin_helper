from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import Document
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

KEYWORDS = "skills, experience, responsibilities"
SKILLS_PROMPT = '''Act as a friendly interviewer.
                Summarize the recommended skills? Provide as bullet list.
                '''

INTERVIEW_QUESTIONS_PROMPT = '''Act as a friendly interviewer.
                What questions are you likely to ask from this job description?
                Provide question and one-line answer in a numbered list with grouped subtitles.
                '''

QUESTIONS_FOR_INTERVIEWER_PROMPT = '''Act as an interviewee.
                                   What questions should I prepare for the job interviewer? 
                                   Provide as numbered list with grouped subtitles.'''

class GPTModel:
    def openai(chunks, prompt):
        # Open and read the api key file
        with open('openai.json', 'r') as file:
            data = json.load(file)
        openai_api_key = data.get('OPENAI_API_KEY', None)
        
        if openai_api_key is None:
            raise ValueError('OpenAI API Key is Required')

        # compares the query and chunks, enabling the selection of the top '3' most similar chunks based on their similarity scores.
        docs  = compute_embeddings_and_search(chunks, KEYWORDS)
        # llm = ChatOpenAI(model='gpt-4o-mini', api_key=openai_api_key)
        llm = ChatOpenAI(model='gpt-3.5-turbo', api_key=openai_api_key)

        # question-answering (QA) pipeline, making use of the load_qa_chain function
        chain = load_qa_chain(llm=llm, chain_type='stuff')

        response = chain.run(input_documents=docs, question=prompt)
        return response
    
    @st.cache_data
    def get_likedin_help(df):
        chunks = df['Description'].values[0].split('\n')
        df['Skills'] = GPTModel.openai(chunks, SKILLS_PROMPT)
        df['Interview Questions'] = GPTModel.openai(chunks, INTERVIEW_QUESTIONS_PROMPT)
        df['Questions for Interviewer'] = GPTModel.openai(chunks, QUESTIONS_FOR_INTERVIEWER_PROMPT)
        return df
    

# Function to compute embeddings and perform similarity search using scikit-learn
def compute_embeddings_and_search(chunks, prompt):
    # Create a TfidfVectorizer to convert text data to numerical vectors
    vectorizer = TfidfVectorizer()
    # Fit and transform the chunks to create the TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(chunks)
    prompt_vector = vectorizer.transform([prompt])
    # Compute cosine similarity between the prompt and the chunks
    similarities = cosine_similarity(prompt_vector, tfidf_matrix).flatten()
    # Get the indices of the top 3 most similar chunks
    top_k_indices = similarities.argsort()[-3:][::-1]
    # Retrieve the most similar chunks
    docs = [chunks[i] for i in top_k_indices if chunks[i] != '']
    docs = [ Document(page_content=d) for d in docs]
    return docs
