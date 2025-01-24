from googlesearch import search
from groq import Groq # Groq Library to use its API.
from json import load,dump # Importing functions to read and write JSON files.
import datetime # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values # Importing dotenv_values to read environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve specific environment variables for username, assistant name, and API Key.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client using the Groq API Key
client = Groq(api_key=GroqAPIKey)

# Design the system instructions for the chatbot
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Try to load the chatlog from the JSON file, or create an empty one if it doesn't exist.
try:
    with open(r"Data\ChatLog.json",'r') as f:
        messages = load(f) # Load existing messages from the chat log.         
except FileNotFoundError:
    # If the file doesn't exist, create an empty JSON file to store chat Logs.
    with open(r"Data\ChatLog.json",'w') as f:
        dump([],f)

# Function to perform a Google search and format the results.
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    lines = Answer.split('\n') # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()] # Remove empty lines.
    modified_answer = '\n'.join(non_empty_lines) # Join the cleaned lines back together.
    return modified_answer

# Predefined chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role":"system","content":System},
    {"role":"user","content":"Hi"},
    {"role":"assistant","content":"Hello, how can i help you?"}
]

# Function to get the real-time information like current date and time.
def Information():
    data = ""
    current_date_time = datetime.datetime.now() # Get the current date and time
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    seconds = current_date_time.strftime("%S")
    data += f"Use this Real-Time information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{seconds} seconds.\n"
    return data

# Function to handle real-time speech and response generation.
def RealTimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load the chat log from the JSON file.
    with open(r"Data\ChatLog.json",'r') as f:
        messages = load(f)
    messages.append({"role":"user","content":f"{prompt}"})

    # Add Google search results to the system chatbot messages.
    SystemChatBot.append({"role":"system","content": GoogleSearch(prompt)})

    # Generate a response using the Groq client.
    completion = client.chat.completions.create(
        model="llama3-70b-8192",    # Specify the AI model to use.
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages, # Include system instructions, real time info and chat history.
        temperature=0.7,  # Adjust response randomness (higher means more random).
        max_tokens=2048,    # Limit the maximum tokens in the response.
        top_p=1,    # Use nucleus sampling to control diversity.
        stream=True, # Enable streaming response.
        stop=None   # Allow the model to determine when to stop.
    )

    
    Answer = "" # Initialize an empty string to store the AI's response.

    # Concatenate responses chunks from the streaming output.
    for chunk in completion:
        if chunk.choices[0].delta.content:  # Check if there's content in the current chunk.
            Answer += chunk.choices[0].delta.content    # Append the content to the answer.
    
    # Clean up the response
    Answer = Answer.replace("</s>","") 
    messages.append({"role":"assistant","content": Answer})

    # Save the updated chatlog back to the JSON file.
    with open(r"Data\ChatLog.json",'w') as f:
        dump(messages, f, indent=4)
    
    # Remove the most recent system message from the chatbot conversation.
    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

# Main entry point of the program for interactive querying.
if __name__ == '__main__':
    while True:
        prompt = input("Enter your query: ")
        print(RealTimeSearchEngine(prompt=prompt))