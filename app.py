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


# File Parsing Functions
def parse_pdf(file):
    reader = PdfReader(file)
    text = ""
    return "".join(page.extract_text() for page in reader.pages)

def parse_docx(file):
    doc = Document(file)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    
def parse_uploaded_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return parse_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return parse_docx(uploaded_file)
    return ""
    

# Initialize session state for insights
if "company_insights" not in st.session_state:
    st.session_state["company_insights"] = ""

if "insights_generated" not in st.session_state:
    st.session_state["insights_generated"] = False


# Page Header
st.title("Sales Assist Agent")
st.markdown("Assistant Agent Powered by Groq.")


# Data collection/inputs
with st.form("company_info", clear_on_submit=True):

    product_name = st.text_input("**Product Name** (What product are you selling?):",)
    
    company_url = st.text_input(
        "**Company URL** (The URL of the company you are targeting):")
    
    product_category = st.text_input(
        "**Product Category** (e.g., 'Data Warehousing' or 'Cloud Data Platform'):")
    
    competitors_url = st.text_input("**Competitors URL**")
    
    value_proposition = st.text_input(
        "**Value Proposition** (A sentence summarizing the product’s value):")
    
    target_customer = st.text_input(
        "**Target Customer** (Name of the person you are trying to sell to.) :")
    
    uploaded_file = st.file_uploader(
    "Upload Product Overview Document (PDF or DOCX):",
    type=["pdf", "docx"])
    
    submitted = st.form_submit_button("Generate Insights")

# Handle form submission
if submitted:
    required_fields = [product_name, company_url, product_category, value_proposition, target_customer]
    if all(required_fields):
        with st.spinner("Processing..."):
                # Clear previous insights
            st.session_state["company_insights"] = ""
            st.session_state["insights_generated"] = False
            
            # Fetch company information if company_url is provided
            company_information = search.invoke(company_url) if company_url else ""
            
            # Parse uploaded file if provided
            file_content = parse_uploaded_file(uploaded_file) if uploaded_file else ""
            
        
            # Create Prompt 
            prompt = f"""
            You are a sales assistant agent, specializing in providing insights to sales representatives.   
            
            Analyze the following inputs:
            Company URL: {company_url}
            Product name: {product_name}
            Product Category: {product_category}
            Competitors: {competitors_url}
            Value Proposition: {value_proposition}
            Target Customer: {target_customer}
            """
            
            if file_content:
                prompt += f"\nUploaded Document Content: {file_content}\n"
            prompt += """
            Instructions:
            1. Summarize the target company's strategy relevant to the provided product category.
            2. Identify any partnerships or mentions of the specified competitors and their relevance to the product.
            3. Provide insights into key leadership or decision-makers at the target company who might influence purchasing decisions.
            4. Suggest how the product can be positioned as an ideal choice to meet the target company’s needs and goals.
            
            Output your response in the following format:
            **Company Strategy**: [Provide a detailed summary based on available information.]
            **Competitor Mentions**: [Summarize any relevant information about competitors.]
            **Leadership Insights**: [List decision-makers and their relevance.]
            **Positioning Tips**: [Provide recommendations for positioning the product effectively.]
            """
        
            try:
                # Use LLM to generate insights
                prompt_template = ChatPromptTemplate([("system", prompt)])
                chain = prompt_template | llm | parser
                insights = chain.invoke({
                "company_url": company_url,
                "product_name": product_name,
                "competitors_url": competitors_url,
                "product_category": product_category,
                "value_proposition": value_proposition,
                "target_customer": target_customer
            })
            
            # Store new insights in session state
                st.session_state["company_insights"] = insights
                st.session_state["insights_generated"] = True
            except Exception as e:
                st.error(f"Failed to generate insights: {e}")
            
    else:
        st.error("Please fill in all required fields.")
    
    
# Display the insights
if st.session_state["insights_generated"]:
        st.markdown("### Generated Insights")
        st.markdown(f"**Product Name:** {product_name}")
        st.markdown(f"**Target Company:** {company_url}")
        st.markdown(f"**Competitors:** {competitors_url}")    
        st.write(st.session_state["company_insights"])
                

