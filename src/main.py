from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader

from chains import Chain
from utils import clean_text

import streamlit as st 

pdf_file_path = 'data/temp.pdf'

def create_streamlit_app(llm):
    st.title("📧 Job Email Generator")
    url_input = st.text_input("Enter the job URL:")
    pdf_uploader = st.file_uploader("Upload the PDF resume", type="pdf")
    

    if st.button("Submit"):
        if not url_input or not pdf_uploader:
            st.warning('URL is empty or file not uploaded', icon="⚠️")
            return
            
        st.info('URL is being processed ...', icon="ℹ️")
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
        except Exception as e:
            st.error(f"Error processing URL with LangChain: {str(e)}")
            return
        else:
            job_info = llm.extract_job_info(data)
        
        st.info('pdf if being processed ...', icon="ℹ️")
        try:
            with open(pdf_file_path, "wb") as f:
                f.write(pdf_uploader.read())
                
            loader = PyPDFLoader(pdf_file_path)
            docs = loader.load()
            pdf_content = ""
            for doc in docs:
                pdf_content += doc.page_content
        except Exception as e:
            st.error(f"Error processing PDF with LangChain: {str(e)}")
            return
        else:
            resume_info = llm.extract_resume_info(pdf_content)
            # st.text_area("Extracted info from the resume", resume_info, height=300)
            
        email = llm.write_email(job_info, resume_info)
        st.code(email, language='markdown')
            

if __name__ == '__main__':
    
    llm = Chain()
    st.set_page_config(layout="wide", page_title="Job Email Generator", page_icon="📧")
    create_streamlit_app(llm)
    
            