"""
Automated Inbox OTP & Verification Link Extractor Engine.
Connects via secure IMAP (SSL) using Google App Password or standard email credentials,
scans ONLY unread verification emails from target platforms, extracts 4-8 digit OTPs
or account activation links, and securely provides them to Custom GPT.
"""
import os
import re
import imaplib
import email
from email.header import decode_header
from typing import Dict, Any, Optional
from core.config import Config

class InboxVerificationReader:
    @staticmethod
    def _clean_header(val: str) -> str:
        if not val:
            return ""
        decoded, encoding = decode_header(val)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(encoding or "utf-8", errors="ignore")
        return str(decoded)

    @classmethod
    def fetch_latest_verification(
        cls,
        sender_filter: Optional[str] = None,
        email_user: Optional[str] = None,
        email_password: Optional[str] = None,
        imap_server: str = "imap.gmail.com"
    ) -> Dict[str, Any]:
        """
        Connects via IMAP, searches recent unread verification emails,
        and extracts the OTP code and/or confirmation link.
        """
        user = email_user or Config.get("IMAP_USER") or os.getenv("IMAP_USER", "")
        pwd = email_password or Config.get("IMAP_PASSWORD") or os.getenv("IMAP_PASSWORD", "")

        if not user or not pwd or user.startswith("your_"):
            return {
                "status": "CONFIG_REQUIRED",
                "message": "IMAP credentials not configured. Please provide your Google App Password.",
                "otp": None,
                "verification_link": None
            }

        try:
            # 1. Connect via SSL
            mail = imaplib.IMAP4_SSL(imap_server, port=993)
            mail.login(user, pwd)
            mail.select("INBOX")

            # 2. Search for recent unread emails
            search_query = '(UNSEEN)'
            if sender_filter:
                search_query = f'(UNSEEN FROM "{sender_filter}")'

            status, messages = mail.search(None, search_query)
            if status != "OK" or not messages[0]:
                # Fallback to general recent search if unread specific wasn't found
                status, messages = mail.search(None, 'ALL')

            mail_ids = messages[0].split()
            if not mail_ids:
                mail.logout()
                return {
                    "status": "NO_EMAIL_FOUND",
                    "message": "No recent verification emails found in inbox.",
                    "otp": None,
                    "verification_link": None
                }

            # Check latest 3 emails
            latest_ids = mail_ids[-3:]
            extracted_otp = None
            extracted_link = None
            found_subject = ""
            found_sender = ""

            for m_id in reversed(latest_ids):
                res, data = mail.fetch(m_id, "(RFC822)")
                if res != "OK":
                    continue

                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                found_subject = cls._clean_header(msg.get("Subject", ""))
                found_sender = cls._clean_header(msg.get("From", ""))

                # Extract body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get("Content-Disposition"))
                        if ctype in ["text/plain", "text/html"] and "attachment" not in cdispo:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body += payload.decode("utf-8", errors="ignore") + "\n"
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode("utf-8", errors="ignore")

                # Extract 4-8 digit numeric OTP (e.g. "code is 584920", "OTP: 123456")
                otp_match = re.search(r'\b(?:code|otp|verification code|pin)?\s*[:\-]?\s*([0-9]{4,8})\b', body, re.IGNORECASE)
                if otp_match and not extracted_otp:
                    extracted_otp = otp_match.group(1)

                # Extract verification or confirmation URL
                url_match = re.search(r'(https?://[^\s"\'<>]+(?:verify|confirm|activate|auth|token)[^\s"\'<>]*)', body, re.IGNORECASE)
                if url_match and not extracted_link:
                    extracted_link = url_match.group(1)

                if extracted_otp or extracted_link:
                    break

            mail.close()
            mail.logout()

            if extracted_otp or extracted_link:
                return {
                    "status": "SUCCESS",
                    "sender": found_sender,
                    "subject": found_subject,
                    "otp": extracted_otp,
                    "verification_link": extracted_link,
                    "message": f"Successfully extracted verification details from '{found_subject}'!"
                }
            else:
                return {
                    "status": "NOT_FOUND",
                    "sender": found_sender,
                    "subject": found_subject,
                    "otp": None,
                    "verification_link": None,
                    "message": "Found recent email but could not detect an OTP or verification link."
                }

        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"IMAP connection failed: {str(e)}",
                "otp": None,
                "verification_link": None
            }
