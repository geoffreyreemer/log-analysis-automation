import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import markdown
import logging

# Load environment variables from .env file
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuration variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAILS = os.getenv("TO_EMAILS", "").split(",")  # Comma-separated list of recipients
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "./error.log")
MAX_LOG_SIZE = int(os.getenv("MAX_LOG_SIZE", 50000))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
USE_HTML_EMAIL = os.getenv("USE_HTML_EMAIL", "true").lower() == "true"

# Step 1: Read the last `MAX_LOG_SIZE` characters of the log file
def parse_logs(file_path: str, max_chars: int = 50000) -> str:
    """Reads the last `max_chars` characters from the log file."""
    try:
        with open(file_path, 'r') as file:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            start_pos = max(0, file_size - max_chars)
            file.seek(start_pos, os.SEEK_SET)
            logs = file.read()
        return logs
    except FileNotFoundError:
        logging.error(f"Log file not found: {file_path}")
        return ""

# Step 2: Analyze logs using OpenAI API
def analyze_logs_with_openai(logs: str) -> str:
    """Analyzes the logs using OpenAI API and returns a summary."""
    openai.api_key = OPENAI_API_KEY
    try:
        completion = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert log analyst. Provide a concise summary of the issues in the logs, formatted in Markdown with sections like '🚨 Critical Issues', '📊 Error Patterns', and '💡 Recommendations'."},
                {"role": "user", "content": f"Here are the logs:\n{logs}"}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Error in OpenAI API call: {str(e)}")
        return f"Error in OpenAI API call: {str(e)}"

# Step 3: Convert Markdown to HTML
def markdown_to_html(markdown_text: str) -> str:
    """Converts Markdown text to styled HTML."""
    html = markdown.markdown(markdown_text, extensions=["extra", "sane_lists"])
    styled_html = f"""
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.5; }}
        ol, ul {{ margin: 0; padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}
        h2, h3 {{ margin-top: 20px; }}
    </style>
    {html}
    """
    return styled_html

# Step 4: Send email summary with logs attached
def send_email(summary: str, recipients: list, log_file_path: str) -> None:
    """Sends an email with the log analysis summary and attaches the log file."""
    today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"Daily Log Analysis Report - {today_date}"

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = ', '.join(recipients)

    # Add content (HTML or plain text)
    if USE_HTML_EMAIL:
        summary_html = markdown_to_html(summary)
        html_content = f"""
        <html>
            <body>
                <h2>Daily Log Analysis Report - {today_date}</h2>
                <div>
                    {summary_html}
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))
    else:
        msg.attach(MIMEText(summary, "plain"))

    # Attach the log file
    try:
        with open(log_file_path, 'r') as log_file:
            log_attachment = MIMEBase('application', 'octet-stream')
            log_attachment.set_payload(log_file.read())
            encoders.encode_base64(log_attachment)
            log_attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(log_file_path)}"'
            )
            msg.attach(log_attachment)
    except Exception as e:
        logging.error(f"Error attaching log file: {str(e)}")

    # Send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
            logging.info(f"Email sent successfully to: {', '.join(recipients)}")
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")

# Step 5: Rotate log file after processing
def rotate_log_file(log_file_path: str) -> None:
    """Renames the processed log file and creates a new empty log file."""
    timestamp = int(time.time())
    new_log_file_name = f"{log_file_path}.{timestamp}"
    try:
        os.rename(log_file_path, new_log_file_name)
        logging.info(f"Log file renamed to: {new_log_file_name}")
        open(log_file_path, 'w').close()
        logging.info(f"New empty log file created: {log_file_path}")
    except Exception as e:
        logging.error(f"Error rotating log file: {str(e)}")

# Main script
def main():
    logging.info("Reading logs...")
    logs = parse_logs(LOG_FILE_PATH, MAX_LOG_SIZE)

    if not logs.strip():
        logging.warning("No logs to process.")
        return

    logging.info("Analyzing logs with OpenAI API...")
    summary = analyze_logs_with_openai(logs)
    logging.info("Analysis complete. Summary generated.")

    logging.info("Sending email summary...")
    send_email(summary, TO_EMAILS, LOG_FILE_PATH)

    logging.info("Rotating log file...")
    rotate_log_file(LOG_FILE_PATH)

if __name__ == "__main__":
    main()
