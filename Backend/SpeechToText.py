import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import mtranslate as mt
# from googletrans import Translator
from langdetect import detect

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Get the input language setting from the environment variables.
InputLanguage = env_vars.get("InputLanguage")

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code with the input language from the environment variables.
HtmlCode = str(HtmlCode).replace("recognition.lang = '';",f"recognition.lang = '{InputLanguage}';")

# write the modified HTML code to a file.
with open(r"Data\Voice.html",'w') as f:
    f.write(HtmlCode)

# Get the current working directory
current_dir = os.getcwd()

# Generate the file path for the HTML file.
Link = f"{current_dir}/Data/Voice.html"

# Set Chrome options for the WebDriver.
chrome_option = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.84 Safari/537.36"
chrome_option.add_argument(f"user-agent={user_agent}")
chrome_option.add_argument("--use-fake-ui-for-media-stream")
chrome_option.add_argument("--use-fake-device-for-media-stream")
chrome_option.add_argument("--headless=new")  # Corrected syntax for headless mode.

# Initialize the Chrome WebDriver using the ChromeDriverManager.
driver_path = r"C:/Windows/chromedriver.exe"
# Check if ChromeDriver exists
if os.path.exists(driver_path):  # If driver is already downloaded
    # print("Using existing ChromeDriver...")
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_option)
else:  # Dynamically install ChromeDriver if not found
    print("ChromeDriver not found. Installing it dynamically...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_option)

# Define the path for temporary files.
TempDirPath = rf"{current_dir}/Frontend/Files"

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    try:
        with open(rf'{TempDirPath}/Status.data', 'w', encoding='utf-8') as file:
            file.write(Status)
        print(f"Status written: {Status}")  # Debugging line to confirm writing
    except Exception as e:
        print(f"Error while writing status: {e}")  # Handle any issues that occur during writing

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "when", "where", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    # Check if the query is likely a question
    if any(word+" " in query_words for word in question_words):
        # Ensure it ends with a question mark
        if new_query[-1] not in ['?', '.', '!']:
            new_query += "?"
        elif new_query[-1] in ['.', '!']:
            new_query = new_query[:-1] + "?"
    else:
        # For non-questions, ensure it ends with a period
        if new_query[-1] not in ['.', '!', '?']:
            new_query += "."
    
    return new_query.capitalize()


# Function to translate text into English using the mtranslate library
def UniversalTranslator(Text):
    # translator = Translator()
    # try:
    #     translated = translator.translate(Text, dest=target_lang)
    #     return translated.text
    # except Exception as e:
    #     print(f"Error during translation: {e}")
    #     return None
    try:
        english_translation = mt.translate(Text, "en", "auto")
        return english_translation.capitalize()
    except Exception as e:
        print(f"Sorry am having issues right now, could not understand what you said.\n{e}")
        return ""

# Function to detect the language of a given text.
# Explicitely required because the default system is not able to detect the languague well.
def detect_language(text):
    try:
        language = detect(text)
        return language
    except Exception as e:
        return None

# Function to perform speech recognition using the WebDriver.
def SpeechRecognition():
    driver.get("file:///" + Link)
    driver.find_element(By.ID, value="start").click()
    start_time = time.time()

    while True:
        try:
            Text = driver.find_element(By.ID, value="output").text
            
            if Text:
                driver.find_element(By.ID, value="end").click()
                # Check if the input language is English

                detected = detect_language(Text)
                if detected == 'en':
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating....")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            pass

        # Break after 10 seconds if no text is found.
        if time.time() - start_time > 25:
            break

if __name__ == '__main__':
    while True:
        try:
            Text = SpeechRecognition()
            print(Text)
        except Exception as e:
            print(f"Error in main loop: {e}")