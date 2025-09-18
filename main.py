import streamlit as st
import os
from dotenv import load_dotenv

# --- Load Environment Variables ---
# This MUST be the first thing to run to ensure the API key is available.
load_dotenv()

# --- Import project modules ---
# These are imported after loading the .env file.
from scrape import scrape_website, extract_body_content, clean_body_content, split_dom_content
from parse import parse_with_huggingface
# --- Streamlit App ---

st.title("🤖 AI Web Scraper")
st.write("This tool scrapes a website, then uses Google's Gemini Pro to extract specific information based on your request.")

# Initialize session state variables if they don't exist
if "dom_content" not in st.session_state:
    st.session_state.dom_content = ""
if "parsed_result" not in st.session_state:
    st.session_state.parsed_result = ""


# --- Step 1: Scrape the Website ---
url = st.text_input("Enter a Website URL to Scrape")

if st.button("Scrape Website"):
    if url:
        with st.spinner(f"Scraping {url}..."):
            try:
                dom_content = scrape_website(url)
                body_content = extract_body_content(dom_content)
                cleaned_content = clean_body_content(body_content)

                # Store content in session state
                st.session_state.dom_content = cleaned_content
                st.session_state.parsed_result = "" # Clear previous results
                
                st.success("Scraping completed successfully!")
                print("\n✅ Scraping completed. Cleaned content preview:\n")
                print(cleaned_content[:2000])

            except Exception as e:
                st.error(f"An error occurred during scraping: {e}")
    else:
        st.warning("Please enter a URL to scrape.")

# Display the scraped content if it exists
if st.session_state.dom_content:
    with st.expander("View Scraped Website Content"):
        st.text_area("Scraped Content", st.session_state.dom_content, height=300)

    # --- Step 2: Parse the Content with AI ---
    st.header("Extract Information with AI")
    parse_description = st.text_area(
        "Describe what you want to extract from the text above", 
        placeholder="e.g., 'Extract all the job titles and their locations', 'List the names of all the speakers', 'Get the product names and their prices'"
    )

    if st.button("Extract Information"):
        if not parse_description:
            st.warning("Please describe what you want to extract.")
        else:
            with st.spinner("Parsing the content with Gemini... This may take a moment."):
                try:
                    # Split content into chunks (ready for AI processing)
                    dom_chunks = split_dom_content(st.session_state.dom_content)
                    st.write(f"Content has been split into {len(dom_chunks)} chunk(s) for analysis.")
                    
                    # Call the Gemini parsing function from parse.py
                    result = parse_with_huggingface(dom_chunks, parse_description)
                    st.session_state.parsed_result = result
                    
                    st.success("Extraction complete!")

                except Exception as e:
                    st.error(f"An error occurred during parsing: {e}")

# --- Step 3: Display the Final Result ---
if st.session_state.parsed_result:
    st.header("Extracted Information")
    st.text_area("Result", st.session_state.parsed_result, height=400)