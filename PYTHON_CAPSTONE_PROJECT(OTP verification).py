import random
import smtplib
import tkinter as tk
from tkinter import messagebox
import threading
import os
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Retrieve sensitive data from environment variables
sender_email = os.getenv('EMAIL_ADDRESS')
password = os.getenv('EMAIL_PASSWORD')

# Check if variables are loaded correctly
if sender_email is None or password is None:
    raise ValueError("Environment variables EMAIL_ADDRESS or EMAIL_PASSWORD are not set")

# SMTP server setup
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(sender_email, password)

# Set to store generated OTPs
generated_otps = set()

# Function to generate a unique 6-digit OTP
def generate_unique_otp():
    while True:
        otp = random.randint(100000, 999999)
        if otp not in generated_otps:
            generated_otps.add(otp)
            return otp

# Function to validate email format using regex
def email_verification(receiver_email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(regex, receiver_email):
        return True
    else:
        return False

# Function to send confirmation email
def send_confirmation_email(receiver_email):
    confirmation_code = random.randint(100000, 999999)
    body = f"Dear User,\n\nYour confirmation code is {confirmation_code}. Please enter this code on the website to verify your email address."
    subject = "Email Confirmation"
    message = f'Subject:{subject}\n\n{body}'
    
    server.sendmail(sender_email, receiver_email, message)
    return confirmation_code

# Function to handle OTP submission and email verification
from tkinter import simpledialog
def submit_email():
    global otp, valid_receiver_email, confirmation_code
    receiver_email = email_input.get()
    
    if email_verification(receiver_email):
        confirmation_code = send_confirmation_email(receiver_email)
        valid_receiver_email = receiver_email
        otp = generate_unique_otp()
        messagebox.showinfo("Info", f"Confirmation code has been sent to {receiver_email}")
        
        # Ask user to enter the confirmation code
        entered_code = simpledialog.askstring("Email Confirmation", "Enter the confirmation code sent to your email:")
        if int(entered_code) == confirmation_code:
            messagebox.showinfo("Success", "Email Verified Successfully!")
            send_otp(receiver_email, otp)
            messagebox.showinfo("Info", f"OTP has been sent to {receiver_email}")
        else:
            messagebox.showerror("Error", "Invalid confirmation code. Please try again.")
    else:
        messagebox.showerror("Error", "Invalid email address. Please enter a valid email.")

# Function to send OTP via email
def send_otp(receiver_email, otp):
    body = f"Dear User,\n\nYour OTP is {otp}."
    subject = "OTP Verification using Python"
    message = f'Subject:{subject}\n\n{body}'
    server.sendmail(sender_email, receiver_email, message)

# Function to handle OTP verification
def verify_otp():
    global attempts
    entered_otp = otp_input.get()
    if int(entered_otp) == otp:
        messagebox.showinfo("Success", "OTP Verified Successfully!")
    else:
        attempts -= 1
        if attempts > 0:
            messagebox.showerror("Error", f"Invalid OTP. You have {attempts} attempts left.")
        else:
            messagebox.showerror("Error", "Invalid OTP. No attempts left. Please resend OTP.")
            invalidate_otp()

# Function to handle OTP resend
def resend_otp():
    global otp
    otp = generate_unique_otp()
    send_otp(valid_receiver_email, otp)
    messagebox.showinfo("Info", f"OTP has been resent to {valid_receiver_email}")
    
    # Start the OTP expiration timer
    threading.Timer(60.0, invalidate_otp).start()

# Function to invalidate the OTP after 60 seconds
def invalidate_otp():
    global otp
    otp = None
    messagebox.showinfo("Info", "OTP has expired. Please request a new OTP.")

# GUI setup
root = tk.Tk()
root.title("OTP Verification")
root.geometry("400x300")

# Global attempts variable
attempts = 3

# Email input
email_label = tk.Label(root, text="Email:", font=("Arial", 12))
email_label.pack(pady=10)
email_input = tk.Entry(root, font=("Arial", 12))
email_input.pack(pady=5)

# Submit and Verify button for Email
submit_button = tk.Button(root, text="Submit Email", command=submit_email, font=("Arial", 12))
submit_button.pack(pady=10)

# OTP input
otp_label = tk.Label(root, text="Enter OTP:", font=("Arial", 12))
otp_label.pack(pady=10)
otp_input = tk.Entry(root, font=("Arial", 12))
otp_input.pack(pady=5)

# Verify and Resend buttons
verify_button = tk.Button(root, text="Verify OTP", command=verify_otp, font=("Arial", 12))
verify_button.pack(pady=10)

resend_button = tk.Button(root, text="Resend OTP", command=resend_otp, font=("Arial", 12))
resend_button.pack(pady=10)

# Run the application
root.mainloop()

# Close the SMTP server
server.quit()
