"""
Professional Email Dispatcher & Copywriter Engine.
Allows ChatGPT Custom GPT to write, format, and send high-converting professional
emails (Product Launch, Cold Pitch, Order Delivery, Client Proposals) via SMTP or 1-Click Mailto.
"""
import os
import smtplib
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from core.config import Config

class EmailDispatcher:
    @staticmethod
    def compose_and_send(
        to_email: str,
        subject: str,
        body: Optional[str] = None,
        product_link: Optional[str] = None,
        email_type: str = "promotional",
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None,
        sender_name: str = "Digital Products Team"
    ) -> Dict[str, Any]:
        """
        Formats an executive professional HTML email and dispatches it via SMTP.
        Falls back to 1-Click Mailto if SMTP credentials are not yet configured.
        """
        clean_to = to_email.strip()
        link_html = ""
        if product_link:
            link_html = f"""
            <div style="text-align: center; margin: 30px 0;">
                <a href="{product_link}" style="background-color: #0066cc; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                    View & Download Asset &rarr;
                </a>
            </div>
            """

        clean_body = body or (
            "I hope this message finds you well.\n\n"
            "We recently developed a premium, formula-driven digital system designed to automate manual calculations and streamline workflows.\n\n"
            "Please feel free to review the details and let us know if you have any questions."
        )

        # Convert line breaks to HTML paragraphs
        paragraphs = clean_body.split("\n\n")
        body_html = "".join(f"<p style='margin-bottom: 16px; line-height: 1.6;'>{p.replace(chr(10), '<br>')}</p>" for p in paragraphs if p.strip())

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #2d3748; background-color: #f7fafc; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="background-color: #1a202c; color: #ffffff; padding: 24px; text-align: center;">
                    <h1 style="margin: 0; font-size: 20px; font-weight: 600;">{subject}</h1>
                </div>
                <div style="padding: 30px;">
                    {body_html}
                    {link_html}
                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                    <p style="color: #718096; font-size: 13px; margin: 0;">
                        Warm regards,<br>
                        <strong>{sender_name}</strong><br>
                        <em>Autonomous Digital Product Suite</em>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        # Generate 1-Click Mailto Link
        mailto_subject = urllib.parse.quote(subject)
        mailto_body = urllib.parse.quote(clean_body + (f"\n\nLink: {product_link}" if product_link else ""))
        one_click_mailto_url = f"mailto:{clean_to}?subject={mailto_subject}&body={mailto_body}"

        # Check SMTP configuration
        smtp_user = sender_email or Config.get("SMTP_USER") or os.getenv("SMTP_USER", "")
        smtp_pass = sender_password or Config.get("SMTP_PASSWORD") or os.getenv("SMTP_PASSWORD", "")
        smtp_host = Config.get("SMTP_HOST") or os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(Config.get("SMTP_PORT") or os.getenv("SMTP_PORT", "587"))

        sent_via_smtp = False
        smtp_message = ""

        if smtp_user and smtp_pass and not smtp_user.startswith("your_"):
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{sender_name} <{smtp_user}>"
                msg["To"] = clean_to

                part_text = MIMEText(clean_body, "plain")
                part_html = MIMEText(html_content, "html")
                msg.attach(part_text)
                msg.attach(part_html)

                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, [clean_to], msg.as_string())

                sent_via_smtp = True
                smtp_message = f"Email successfully dispatched to {clean_to} via SMTP ({smtp_host})!"
            except Exception as e:
                smtp_message = f"SMTP dispatch failed ({e}). 1-Click Mailto link generated."
        else:
            smtp_message = "SMTP not configured yet. 1-Click pre-filled Mailto link generated."

        return {
            "status": "SENT" if sent_via_smtp else "READY_TO_SEND",
            "sent_via_smtp": sent_via_smtp,
            "to_email": clean_to,
            "subject": subject,
            "message": smtp_message,
            "one_click_mailto_url": one_click_mailto_url,
            "preview_text": clean_body[:250] + "..." if len(clean_body) > 250 else clean_body
        }
