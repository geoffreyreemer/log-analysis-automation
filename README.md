# Log Analysis Automation
by Geoffrey Reemer

This Python script automates the process of analyzing log files, summarizing errors using OpenAI, and sending an email report with the analyzed logs attached. It can be used to identify and track issues in applications without the need to manually sift through large log files.

---

## Features

- **Log Analysis**: Processes logs to identify critical issues, error patterns, and recommendations using OpenAI.
- **Email Reports**: Sends a daily email summary of the analyzed logs with an attachment of the log file.
- **Log Rotation**: Automatically renames processed log files to preserve a history of logs and creates a new log file.
- **Markdown to HTML Conversion**: Generates clean, readable HTML emails for easy review (optional).

---

## Prerequisites

Before using this script, ensure you have:

1. **Python 3.7+** installed. You can download it from [python.org](https://www.python.org/downloads/).
2. An OpenAI API key. Sign up at [OpenAI](https://platform.openai.com/).
3. SMTP credentials for sending emails (e.g., your email service provider details like Gmail, Outlook, etc.).
4. Basic familiarity with your server or local environment (e.g., terminal, setting environment variables).

---

## Installation

1. **Clone or Download the Repository**:
   - If you have Git installed, run:
     ```bash
     git clone https://github.com/geoffreyreemer/log-analysis-automation.git
     cd log-analysis-automation
     ```
   - Alternatively, download the ZIP file and extract it.

2. **Install Dependencies**:
   - Open a terminal in the project folder and run:
     ```bash
     pip install -r requirements.txt
     ```

3. **Set Up Environment Variables**:
   - Copy the placeholder `.env.example` file and rename it to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open the `.env` file in a text editor and fill in your values:
     ```env
     OPENAI_API_KEY=your_openai_api_key_here
     SMTP_SERVER=smtp.example.com
     SMTP_PORT=587
     SMTP_USERNAME=noreply@example.com
     SMTP_PASSWORD=your_smtp_password
     FROM_EMAIL=noreply@example.com
     TO_EMAILS=recipient1@example.com,recipient2@example.com
     LOG_FILE_PATH=./error.log
     MAX_LOG_SIZE=50000
     OPENAI_MODEL=gpt-4
     USE_HTML_EMAIL=true
     ```

4. **Create the Log File**:
   - Ensure the log file specified in `LOG_FILE_PATH` exists:
     ```bash
     touch error.log
     ```

---

## Usage

To run the script:

1. Open a terminal in the project folder.
2. Run the following command:
   ```bash
   python3 log_processor.py
   ```

The script will:
- Analyze the logs in the file specified by `LOG_FILE_PATH`.
- Send an email summary with the processed logs attached.
- Rotate the processed log file and create a new empty log file.

---

## Automating the Script with Cron Jobs

You can set up this script to run automatically at regular intervals using cron jobs.

### Option 1: Using a Web Hosting Interface

1. **Log in to Your Hosting Control Panel**:
   - Navigate to your hosting provider's cPanel, Plesk, or equivalent interface.

2. **Locate the Cron Jobs Section**:
   - Look for "Cron Jobs" in the dashboard or use the search feature to find it.

3. **Create a New Cron Job**:
   - Set the time and frequency:
     - Example: To run the script daily at 2:00 AM:
       - Minute: `0`
       - Hour: `2`
       - Day: `*` (every day)
       - Month: `*` (every month)
       - Weekday: `*` (any day of the week)
   - Add the command to execute the script:
     ```bash
     /usr/bin/python3 /path/to/your/project/log_processor.py
     ```
     Replace `/usr/bin/python3` with the path to Python 3 on your server and `/path/to/your/project` with the directory where the script is located.

4. **Save the Cron Job**:
   - Click "Add New Cron Job" or "Save" to schedule the task.

---

### Option 2: Using the Terminal

1. **Open the Cron Table**:
   - Run the following command in your terminal:
     ```bash
     crontab -e
     ```

2. **Add a New Cron Job**:
   - At the bottom of the file, add a line to schedule the script. For example:
     ```bash
     0 2 * * * /usr/bin/python3 /path/to/your/project/log_processor.py >> /path/to/your/project/cron_log.txt 2>&1
     ```
   - This example runs the script at **2:00 AM every day**:
     - `0 2`: Run at minute 0, hour 2 (2:00 AM).
     - `* * *`: Run every day of the month, month, and weekday.
   - The `>> /path/to/your/project/cron_log.txt 2>&1` part logs the output and errors to a file for debugging.

3. **Save and Exit**:
   - Press `CTRL + O` to save and `CTRL + X` to exit the editor.

4. **Verify the Cron Job**:
   - List your cron jobs to confirm:
     ```bash
     crontab -l
     ```

---

## Troubleshooting

### 1. **Email Does Not Contain Any Input**
   - **Cause**: The log file is empty or contains no new entries.
   - **Fix**: Ensure the log file has content. You can manually add some text to test:
     ```bash
     echo "Test log entry" >> error.log
     ```

### 2. **You Don’t Receive Any Emails**
   - **Possible Causes**:
     - SMTP credentials are incorrect.
     - Your email provider blocks automated emails.
     - The email is in the spam folder.
   - **Fix**:
     - Double-check the `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_SERVER`, and `SMTP_PORT` values in the `.env` file.
     - Check your spam/junk email folder.
     - If you’re using Gmail, ensure “Allow less secure apps” is enabled in your account settings (or set up an App Password).

### 3. **Common Errors**

| Error Message                        | Cause                                     | Solution                                  |
|--------------------------------------|-------------------------------------------|------------------------------------------|
| `Log file not found`                 | Specified log file does not exist.        | Create the file using `touch error.log`. |
| `Error in OpenAI API call`           | API key is missing or invalid.            | Ensure `OPENAI_API_KEY` is set correctly in `.env`. |
| `Error sending email`                | SMTP credentials are incorrect.           | Verify the SMTP settings in `.env`.      |
| `Error attaching log file`           | Log file is locked or unreadable.         | Ensure the file has the correct permissions. |

---

## Advanced Configuration

### Environment Variables

| Variable        | Description                                                                 | Default Value             |
|------------------|-----------------------------------------------------------------------------|---------------------------|
| `OPENAI_API_KEY` | OpenAI API key for accessing GPT models.                                   | None (required)           |
| `SMTP_SERVER`    | SMTP server address (e.g., `smtp.gmail.com`).                              | None (required)           |
| `SMTP_PORT`      | SMTP port (usually `587` for TLS or `465` for SSL).                        | `587`                     |
| `SMTP_USERNAME`  | Username for the SMTP server (usually your email address).                 | None (required)           |
| `SMTP_PASSWORD`  | Password for the SMTP server.                                              | None (required)           |
| `FROM_EMAIL`     | The email address shown in the "From" field of the sent email.             | None (required)           |
| `TO_EMAILS`      | Comma-separated list of recipient email addresses.                         | None (required)           |
| `LOG_FILE_PATH`  | Path to the log file to be analyzed.                                       | `./error.log`             |
| `MAX_LOG_SIZE`   | Number of characters to read from the end of the log file.                 | `50000`                   |
| `OPENAI_MODEL`   | The OpenAI model to use (e.g., `gpt-4`, `gpt-4o`).                         | `gpt-4`                   |
| `USE_HTML_EMAIL` | Whether to send email as HTML (`true`) or plain text (`false`).            | `true`                    |

---

## Security Tips

1. **Do Not Hardcode Sensitive Values**:
   - Always use environment variables for API keys, passwords, and other sensitive information.
2. **Restrict File Permissions**:
   - Ensure `.env` and log files are not publicly readable:
     ```bash
     chmod 600 .env error.log
     ```

---

## Contributing

If you encounter any issues or have suggestions for improvements, feel free to open an issue or a pull request on GitHub.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
