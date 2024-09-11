import re
import os
import time
import urllib.parse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, StringVar, IntVar

def extract_contact_info(text):
    """Extracts phone numbers and emails from text."""
    phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}')
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

    phones = phone_pattern.findall(text)
    emails = email_pattern.findall(text)

    phone_number = phones[0] if phones else 'N/A'
    email_address = emails[0] if emails else 'N/A'

    return phone_number, email_address

def google_dork_search_location(keyword, location, num_results=10):
    search_results = []
    query = f"site:instagram.com {keyword} {location}"
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num_results}"

    # Set up the Selenium driver with options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920x1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(3)  # Allow time for the page to load

        results = driver.find_elements(By.CLASS_NAME, 'g')

        for result in results:
            try:
                link_element = result.find_element(By.TAG_NAME, 'a')
                link = link_element.get_attribute('href')
                if "instagram.com" in link:
                    title_element = result.find_element(By.TAG_NAME, 'h3')
                    title = title_element.text if title_element else 'No title'

                    snippet_element = result.find_element(By.CLASS_NAME, 'VwiC3b')
                    snippet_text = snippet_element.text if snippet_element else ''

                    phone_number, email_address = extract_contact_info(snippet_text)

                    search_results.append({
                        'title': title,
                        'link': link,
                        'phone': phone_number,
                        'email': email_address
                    })
            except Exception as e:
                print(f"Error parsing result: {e}")

    finally:
        driver.quit()

    return search_results

def save_results(search_results, keyword, location, file_type='csv'):
    if not search_results:
        messagebox.showinfo("No Results", f"No results to save for {keyword} in {location}.")
        return
    
    directory = filedialog.askdirectory(title="Select Directory to Save Results")
    if not directory:
        return  # User canceled the operation
    
    safe_keyword = keyword.replace(" ", "_")
    safe_location = location.replace(" ", "_")
    filename = f"{directory}/{safe_keyword}_{safe_location}.{file_type}"

    df = pd.DataFrame(search_results)
    
    if file_type == 'csv':
        df.to_csv(filename, index=False)
    else:
        df.to_excel(filename, index=False)
    
    messagebox.showinfo("Results Saved", f"Results for {keyword} in {location} saved to {filename}")

def start_dorking():
    keyword = keyword_var.get()
    location = location_var.get()
    file_type = 'csv' if file_type_var.get() == 1 else 'xlsx'
    
    if not keyword or not location:
        messagebox.showwarning("Input Error", "Please enter both a keyword and a location.")
        return
    
    results = google_dork_search_location(keyword, location)
    save_results(results, keyword, location, file_type)

# Create the main window
app = tk.Tk()
app.title("Instagram Dorking Tool")
app.geometry("400x250")

# Use ttk styles for modern look
style = ttk.Style()
style.configure('TLabel', font=('Arial', 10))
style.configure('TButton', font=('Arial', 10), foreground='blue')
style.configure('TRadiobutton', font=('Arial', 10))

# Create a frame for content
frame = ttk.Frame(app, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Create input fields and labels
ttk.Label(frame, text="Keyword:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
keyword_var = StringVar()
ttk.Entry(frame, textvariable=keyword_var, width=30).grid(row=0, column=1, padx=10, pady=5)

ttk.Label(frame, text="Location:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
location_var = StringVar()
ttk.Entry(frame, textvariable=location_var, width=30).grid(row=1, column=1, padx=10, pady=5)

# Create radio buttons for file type selection
file_type_var = IntVar(value=1)
ttk.Radiobutton(frame, text="CSV", variable=file_type_var, value=1).grid(row=2, column=0, padx=10, pady=5)
ttk.Radiobutton(frame, text="Excel", variable=file_type_var, value=2).grid(row=2, column=1, padx=10, pady=5)

# Create a button to start the search
ttk.Button(frame, text="Start Dorking", command=start_dorking).grid(row=3, column=0, columnspan=2, pady=20)

# Run the application
app.mainloop()
