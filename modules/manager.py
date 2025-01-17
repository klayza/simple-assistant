import os
from datetime import datetime
import sys

from dotenv import load_dotenv
sys.path.append("../simple-assistant")
load_dotenv()
# from ai import plain_ai_response


# Will check if the user has done their meditation or whatever in the done_history.txt
def check_done():
    today = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists("./data/done_history.txt"):
        return False
    
    with open("./data/done_history.txt", "r") as file:
        done_history = file.readlines()
        return today in (line.strip() for line in done_history)

# Initialize the file if it doesn't exist
def init():
    if not os.path.exists("./data"):
        os.makedirs("./data")
    if not os.path.exists("./data/done_history.txt"):
        with open("./data/done_history.txt", "w") as file:
            file.write("")  # Create an empty file

# Mark today's date as done
def mark_done():
    today = datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists("./data/done_history.txt"):
        init()
    
    with open("./data/done_history.txt", "a") as file:
        file.write(f"{today}\n")
    
    return "Today complete."


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Check if done, and if not, send an email saying you lose $5
def final_check():
    from ai import plain_ai_response
    
    if check_done():
        return

    # Generate the response messages
    # message = plain_ai_response("Tell the user that they suck and failed to complete their daily task", "system")
    # email_message = plain_ai_response("Write a poorly spelt email to your boss saying that that their employee failed to complete their daily task and that they suck a lot.", "system")
    email_message = "deez"
    message = "done"

    
    print(email_message)  # Debugging

    # Email configuration
    sender_email = os.getenv("SENDER_EMAIL")  # Replace with your email
    recipient_email = os.getenv("RECIPIENT_EMAIL") # Replace with your boss's email
    password = os.getenv("GMAIL_KEY")  # Use an app-specific password if required
    
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Clayton Failed"
        msg.attach(MIMEText(email_message, 'plain'))
        
        # Connect to the SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Replace with your SMTP server
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
    
    return message


if __name__ == "__main__":
    final_check()