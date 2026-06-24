# AI Email Agent

A lightweight Streamlit app for sending emails via SMTP and generating email replies using OpenAI.

## Setup

1. Create a virtual environment and activate it:
   - `python -m venv venv`
   - `venv\Scripts\activate`

2. Install dependencies:
   - `pip install -r requirements.txt`

3. Copy `.env.example` to `.env` and add your credentials.

4. Run the app:
   - `streamlit run email_agent_fixed.py`

## Notes

- `EMAIL_ADDRESS` and `EMAIL_PASSWORD` are used by `yagmail` to send SMTP email.
- `OPENAI_API_KEY` is required to generate professional email replies.
- Keep `.env` private and do not commit it to source control.
