import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from urllib.parse import urljoin

# Regex patterns for email & phone
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"
PHONE_REGEX = r"\+?\d[\d\-\s]{7,}\d"

# Pages to check for contact info
CONTACT_PATHS = ["/contact", "/contact-us", "/about", "/about-us", "/support"]

def extract_contact_info(url):
    """Try to get email/phone from a given page URL"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers, timeout=5).text
        email = re.search(EMAIL_REGEX, html)
        phone = re.search(PHONE_REGEX, html)
        return (email.group(0) if email else None,
                phone.group(0) if phone else None)
    except:
        return (None, None)

def scrape_saved_results(file_path, output_file="business_leads.xlsx"):
    # Load saved Google search HTML
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    businesses = []

    results = soup.select(".tF2Cxc")
    print(f"Found {len(results)} results")

    for idx, result in enumerate(results, start=1):
        # Business name
        name = result.select_one("h3").text if result.select_one("h3") else "N/A"
        
        # Website (or mark as 'No website')
        link_tag = result.select_one("a")
        link = link_tag["href"] if link_tag else None
        website_status = link if (link and link.startswith("http")) else "No website"

        # Description snippet
        snippet = result.select_one(".VwiC3b")
        snippet_text = snippet.text if snippet else "N/A"

        email, phone = None, None

        if website_status != "No website":
            # Try homepage first
            email, phone = extract_contact_info(link)

            # If nothing found → check common contact pages
            if not email and not phone:
                for path in CONTACT_PATHS:
                    test_url = urljoin(link, path)
                    c_email, c_phone = extract_contact_info(test_url)
                    if c_email or c_phone:
                        email, phone = c_email, c_phone
                        break

        businesses.append({
            "Name": name,
            "Website": website_status,
            "Email": email,
            "Phone": phone,
            "Snippet": snippet_text
        })

        print(f"[{idx}] {name} | {website_status} | Email: {email} | Phone: {phone}")
        time.sleep(1)  # Slow down to avoid blocks

    # Save results
    df = pd.DataFrame(businesses)
    df.to_excel(output_file, index=False)
    print(f"\n✅ Saved {len(businesses)} businesses to {output_file}")


# Example usage:
scrape_saved_results("results.html")
