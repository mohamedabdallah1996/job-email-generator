from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import Dict

import os

load_dotenv()

class Chain:
    def __init__(self):
        self._llm =  ChatGroq(temperature=0, model_name="llama-3.1-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))

    def extract_job_info(self, page_data: str) -> Dict:
        extract_job_prompt = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE OFFERING JOB:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job posting information and return them in JSON format containing the
            following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### NOTE
            Don't consider featured jobs or similar jobs ads as part of the job posting.
            ### VALID JSON (NO PREAMBLE):
            """
        )

        extract_job_chain = extract_job_prompt | self._llm
        extracted_job_str = extract_job_chain.invoke(input={"page_data": page_data})
        json_parser = JsonOutputParser()
        extracted_job_json = json_parser.parse(extracted_job_str.content)
        return extracted_job_json
    
    def extract_resume_info(self, page_data: str) -> Dict:
        extract_resume_prompt = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE OFFERING JOB:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from a pdf resume.
            Your job is to extract the important information from this resume and return them in JSON format containing the
            following keys: `name`, `role`, `experience`, `skills` and `education`.
            you can add some key informations if existed such as `projects` and `tools`
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )

        extract_resume_chain = extract_resume_prompt | self._llm
        extracted_resume_str = extract_resume_chain.invoke(input={"page_data": page_data})
        json_parser = JsonOutputParser()
        extracted_resume_json = json_parser.parse(extracted_resume_str.content)
        return extracted_resume_json
    
    def write_email(self, job_info: str, resume_info: str) -> Dict:
        email_prompt = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### RESUME:
            {resume}

            ### INSTRUCTION:
            Please write a professional email applying for the above job, ensuring the email is not too long or too short.
            Mention key skills and experiences from the above resume that align with the job requirements in the posting.
            The tone should be formal but engaging. Include a brief introduction, key qualifications, and a polite closing,
            with a request for an interview or further discussion. Make sure to highlight only relevant skills and experiences,
            and make it tailored to the job role. Don't mention all the skills or experiences in the resume. Just be relevent to the
            job description.
            Do not provide a preamble.
            ### NOTE
            Your name is the person's name in the resume.
            ### EMAIL (NO PREAMBLE):

            """
            )

        email_chain = email_prompt | self._llm
        email_str = email_chain.invoke({"job_description": job_info, "resume": resume_info})
        return email_str.content