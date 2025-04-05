import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from io import BytesIO
from urllib.parse import urlparse

# Setup driver
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Scraping function
def scrape_website(url):
    try:
        driver = setup_driver()
        driver.get(url)

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
        all_links = [a.get_attribute("href") for a in driver.find_elements(By.TAG_NAME, "a") if a.get_attribute("href")]

        filtered_links = [link for link in all_links if is_valid_link(link, url)][:5]

        lead_data = []
        for link in filtered_links:
            driver.get(link)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "p")))
            title = driver.title
            content = " ".join([p.text for p in driver.find_elements(By.TAG_NAME, "p") if p.text][:3])
            lead_data.append({"Page Title": title, "Link": link, "Lead Content": content})

        driver.quit()
        return pd.DataFrame(lead_data)
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# Validasi link internal & relevan
def is_valid_link(link, base_url):
    if not link.startswith("http"):
        return False
    base_domain = urlparse(base_url).netloc
    link_domain = urlparse(link).netloc
    return base_domain in link_domain

# Main UI
def main():
    st.set_page_config(page_title="Metamorphosis Scraper", page_icon="🔍", layout="wide")
    st.markdown(
        """
        <style>
        .main {background-color: #f8f9fa;}
        h1, .stTextInput>div>div>input, .stButton>button, .stDownloadButton>button {
            border-radius: 10px;
        }
        .stButton>button {
            width: 100%;
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }
        .stDownloadButton>button {
            width: 100%;
            background-color: #28a745;
            color: white;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🔍 Metamorphosis Web Scraper")
    st.write("Generate business lead data by extracting key content from target websites.")

    url = st.text_input("🌐 Enter a website URL to scrape:", "https://example.com")

    if st.button("🚀 Start Scraping"):
        if url:
            with st.spinner("Scraping... Please wait."):
                result_df = scrape_website(url)
                if result_df is not None and not result_df.empty:
                    st.success("✅ Scraping complete!")
                    st.dataframe(result_df)

                    csv = BytesIO()
                    result_df.to_csv(csv, index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv.getvalue(),
                        file_name="leads.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("⚠️ No lead data found. Try another URL.")
        else:
            st.error("Please input a valid URL.")

if __name__ == "__main__":
    main()
