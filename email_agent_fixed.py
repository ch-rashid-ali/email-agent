import os
import yagmail
import streamlit as st
from dotenv import load_dotenv

try:
    import openai
except ImportError:
    openai = None

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_email_client():
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return None
    try:
        return yagmail.SMTP(EMAIL_ADDRESS, EMAIL_PASSWORD)
    except Exception as exc:
        st.error(f"Email client initialization failed: {exc}")
        return None


def send_email(recipient: str, subject: str, body: str) -> str:
    if not recipient or not subject or not body:
        return "Please provide recipient, subject, and body before sending."

    email_client = get_email_client()
    if email_client is None:
        return (
            "Email client is not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env "
            "and restart the app."
        )

    try:
        email_client.send(to=recipient, subject=subject, contents=body)
        return f"✅ Email sent successfully to {recipient}."
    except Exception as exc:
        return f"❌ Failed to send email: {exc}"


def generate_email_reply(original_email: str) -> str:
    if not original_email:
        return "Paste the original email you want to reply to."

    if openai is None:
        return (
            "OpenAI integration is not available. Install the openai package with "
            "`pip install openai`."
        )

    if not OPENAI_API_KEY:
        return (
            "OpenAI API key is missing. Set OPENAI_API_KEY in .env or Streamlit secrets."
        )

    openai.api_key = OPENAI_API_KEY
    prompt = (
        "You are a professional assistant. Write a concise, courteous, and helpful email reply "
        "based on the original email text below."
        f"\n\nOriginal Email:\n{original_email}\n\nReply:\n"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You write professional email replies."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=350,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        return f"❌ AI reply generation failed: {exc}"


def main():
    st.set_page_config(page_title="AI Email Agent", page_icon="✉️")
    st.title("✉️ AI Email Agent")
    st.write(
        "Use this app to send an email with SMTP credentials or generate a professional reply "
        "from a received message."
    )

    tab_send, tab_reply = st.tabs(["Compose Email", "Generate Reply"])

    with tab_send:
        recipient = st.text_input("Recipient email")
        subject = st.text_input("Subject")
        body = st.text_area("Email body", height=260)

        if st.button("Send Email"):
            result = send_email(recipient, subject, body)
            if result.startswith("✅"):
                st.success(result)
            else:
                st.error(result)

    if "generated_reply" not in st.session_state:
        st.session_state.generated_reply = ""

    with tab_reply:
        original_email = st.text_area(
            "Original email text", height=220,
            help="Paste the incoming email or message for which you want a reply."
        )
        reply_recipient = st.text_input(
            "Reply recipient email",
            help="Enter the address where the generated reply should be sent."
        )
        reply_subject = st.text_input(
            "Reply subject",
            value="Re: Your message",
            help="Subject line for the reply email."
        )

        generate_clicked = st.button("Generate Reply", key="generate_reply")
        if generate_clicked:
            with st.spinner("Generating reply..."):
                reply_text = generate_email_reply(original_email)
                st.session_state.generated_reply = reply_text
                if reply_text.startswith("❌"):
                    st.error(reply_text)
                else:
                    st.success("Reply generated")

        if st.session_state.generated_reply:
            st.subheader("Generated reply draft")
            reply_text = st.text_area(
                "Reply draft",
                value=st.session_state.generated_reply,
                height=220,
                key="reply_draft",
            )

            send_reply_clicked = st.button("Send Reply Email", key="send_reply")
            if send_reply_clicked:
                result = send_email(reply_recipient, reply_subject, reply_text)
                if result.startswith("✅"):
                    st.success(result)
                else:
                    st.error(result)

    with st.sidebar:
        st.header("Configuration")
        st.write("Set these values in `.env` or Streamlit secrets:")
        st.write(f"- EMAIL_ADDRESS: {'configured' if EMAIL_ADDRESS else 'missing'}")
        st.write(f"- EMAIL_PASSWORD: {'configured' if EMAIL_PASSWORD else 'missing'}")
        st.write(f"- OPENAI_API_KEY: {'configured' if OPENAI_API_KEY else 'missing'}")

        if openai is None:
            st.warning("OpenAI package not installed. Run `pip install -r requirements.txt`.")
        else:
            st.success("OpenAI package is installed.")

    st.markdown("---")
    st.markdown(
        "**How to run**\n"
        "1. Copy `.env.example` to `.env` and fill in your credentials.\n"
        "2. Install dependencies with `pip install -r requirements.txt`.\n"
        "3. Start the app with `streamlit run email_agent_fixed.py`."
    )


if __name__ == "__main__":
    main()
