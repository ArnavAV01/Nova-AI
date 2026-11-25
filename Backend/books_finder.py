from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from book_mover import *
import requests
import time
import sys

def book_search_and_download(book_name):
    # Set Chrome options to ignore SSL errors
    chrome_options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--headless")  # Optional: run in headless mode

    # Initialize the WebDriver
    driver = webdriver.Chrome(service=Service("C:\Windows\chromedriver.exe"), options=chrome_options)
    driver.get("https://www.pdfdrive.com/")
    
    try:
        # Locate the search box and perform the search
        search_box = driver.find_element(By.ID, "q")
        search_box.send_keys(book_name)
        search_box.send_keys(Keys.RETURN)

        driver.implicitly_wait(10)
        search_results_url = driver.current_url
        # first_result = driver.find_element(By.CSS_SELECTOR, ".files-new li a")
        # page_url = first_result.get_attribute("href")
        r = requests.get(search_results_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        results = soup.find_all('li')
        # print(results)
        # sys.exit(0)

        max_page_count = 0
        top_result_anchor = None
        book_found = False

        for result in results:
            # Extract the page count
            page_count_elem = result.find('span', class_='fi-pagecount')
            
            if page_count_elem is not None:
                page_count_text = page_count_elem.get_text(strip=True)  # Extract text and remove whitespace
                
                if page_count_text:
                    try:
                        page_count = int(page_count_text.split()[0])  # Extract the numeric part
                        
                        # Find the book title
                        title_elem = result.find('a', class_='ai-search')
                        if title_elem:
                            title_text = " ".join([b_tag.get_text(strip=True) for b_tag in title_elem.find_all('b')])
                            
                            # Compare and find the result with the maximum page count
                            if book_name.lower() in title_text.lower():
                                if page_count > max_page_count:
                                    max_page_count = page_count
                                    top_result_anchor = result.find('a')
                                    book_found = True
                    except ValueError:
                        print(f"Error parsing page count: {page_count_text}")
                else:
                    print("Page count text is empty")
            else:
                # print("Page count not found!")
                pass
        
        if book_found and top_result_anchor:
            # Get the href of the anchor tag for the top result
            book_url = "https://www.pdfdrive.com/" + top_result_anchor.get('href')
            print(f"Maximum page count: {max_page_count}")
            print(f"Opening {book_name}..........")

            try:
                # Navigate to the book page
                driver.get(book_url)
                
                # Wait for the page to load completely
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                # BeautifulSoup logic for initial check
                r = requests.get(driver.current_url)
                soup2 = BeautifulSoup(r.content, 'html.parser')
                download_btn = soup2.find(id='download-button-link')

                if download_btn:
                    print("Download button already available. Initiating download...")

                    # Directly click the download button
                    dlink = "https://www.pdfdrive.com/" + download_btn.get('href')
                    driver.get(dlink)

                    # Wait for the actual PDF download button to appear and click it
                    d_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'download.pdf')]"))
                    )
                    d_btn_text = d_btn.text.strip()
                    if d_btn_text == "Download ( PDF )":
                        print("Direct Download (PDF) button available. Initiating download...")
                        d_btn.click()
                        print("Download initiated successfully.")
                    else:
                        print(f"Download button found, but it's not for PDF (text: {d_btn_text}). Checking dropdown...")
                        
                        # If "Download ( PDF )" is not directly available, look for it in the dropdown
                        dropdown_toggle = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-primary.btn-user.dropdown-toggle"))
                        )
                        dropdown_toggle.click()

                        # Select "Download ( PDF )" from the dropdown
                        pdf_option = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Download ( PDF )')]"))
                        )
                        pdf_option.click()
                        print("Download (PDF) option selected from the dropdown.")

                        print("Download initiated successfully.")
                else:
                    print("Download button not found. Process failed.")

            except Exception as e:
                print(f"An error occurred: {e}")

        else:
            print("Book not found or due to some problem the process execution was not successful.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if book_found:            
            # Wait for the download to complete
            if wait_for_download_completion():
                driver.quit()  # Quit the driver after download is finished
                destination_dir = r"C:\Users\ASUS\Desktop\small project\available books"
                move_todays_downloaded_pdf(destination_dir=destination_dir)  # Move the downloaded PDF
                print("Moved Successfully!")
            else:
                print("Download did not complete in the expected time.")
                driver.quit()
        else:
            driver.quit()

if __name__ == '__main__':
    book_name = input("Enter the name of the book you want to read: ")
    book_search_and_download(book_name)

