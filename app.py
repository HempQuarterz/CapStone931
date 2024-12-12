import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from PyPDF2 import PdfReader
from docx import Document


# Model and Agent tools
llm = ChatGroq(api_key=st.secrets.get("GROQ_API_KEY"))
search = TavilySearchResults(max_results=2)
parser = StrOutputParser()
# tools = [search] # add tools to the list

def parse_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def parse_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text
    return text

def parse_uploaded_file(uploaded_file):
    file_content = ""
    if uploaded_file.type == "application/pdf":
        file_content = parse_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        file_content = parse_docx(uploaded_file)
    return file_content



# Page Header
st.title("Sales Assist Agent")
st.markdown("Assistant Agent Powered by Groq.")

# Data collection/inputs
with st.form("company_info", clear_on_submit=True):

    product_name = st.text_input("**Product Name** (What product are you selling?):",
        value = "HempTech Bioplastics"
        )
    
    company_url = st.text_input(
        "**Company URL** (The URL of the company you are targeting):",
        value="https://www.unilever.com/"
    )
    
    product_category = st.text_input(
        "**Product Category** (e.g., 'Data Warehousing' or 'Cloud Data Platform'):",
        value="Sustainable Packaging"
    )
    
    competitors_url = st.text_input("**Competitors URL**",
        value="https://www.ecopacksolutions.com, https://www.bioflexpackaging.com"
)
    
    value_proposition = st.text_input(
        "**Value Proposition** (A sentence summarizing the product’s value):",
        value="Eco-friendly, biodegradable bioplastics for industrial use."
    )
    
    target_customer = st.text_input(
        "**Target Customer** (Name of the person you are trying to sell to.) :",
        value="Richard Slater"
    )
    
    uploaded_file = st.file_uploader(
    "Upload Product Overview Document (PDF or DOCX):",
    type=["pdf", "docx"]
)


    # For the llm insights result
    company_insights = ""

    # Data process
    if st.form_submit_button("Generate Insights"):
        if product_name and company_url:
            with st.spinner("Processing..."):
            # Use search tool to get Company Information
                company_information = search.invoke(company_url)
                
                
    



            # TODO: Create prompt <=================
            prompt = f"""
            You are a sales assistant agent for HempQuarterz, specializing in industrial hemp products.
            Your task is to provide insights for selling HempTech Bioplastics, a biodegradable, eco-friendly packaging solution.    
            
            Analyze the following inputs:
            Company URL: {company_url}
            Product name: {product_name}
            Product Category: {product_category}
            Competitors: {competitors_url}
            Value Proposition: {value_proposition}
            Target Customer: {target_customer}
            
            Instructions:
            1. Summarize Unilever's strategy related to sustainability or bioplastics.
            2. Identify any partnerships or mentions of competitors like EcoPack Solutions and BioFlex Packaging.
            3. Provide key leadership insights, including relevant decision-makers and their roles.
            4. Suggest how HempTech Bioplastics can be positioned as the ideal choice for Unilever's sustainability goals.

            Output your response in the following format:
            **Company Strategy**: [Provide a detailed summary]
            **Competitor Mentions**: [Summarize any relevant information]
            **Leadership Insights**: [List decision-makers and their relevance]
            **Positioning Tips**: [Provide recommendations for pitching HempTech Bioplastics]
            """

            # Prompt Template
            prompt_template = ChatPromptTemplate([("system", prompt)])

            # Chain
            chain = prompt_template | llm | parser

            # Result/Insights
            company_insights = chain.invoke(
                {
                    "company_information": company_information,
                    "product_name": product_name,
                    "competitors_url": competitors_url,
                    "product_category": product_category,
                    "value_proposition": value_proposition,
                    "target_customer": target_customer,
                    "company_url": company_url
                }
            )
            

# Display the insights
if company_insights:
    with st.container():
        st.markdown("### Generated Insights")
        st.markdown(f"**Product Name:** {product_name}")
        st.markdown(f"**Target Company:** {company_url}")
        st.markdown(f"**Competitors:** {competitors_url}")    
        st.write(company_insights)
        