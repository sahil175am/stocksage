"""
StockSage Email Service
Sends price alert notifications via Gmail SMTP (free).
Uses Flask-Mail with SMTP credentials from environment.
Falls back to console logging if no credentials set.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    """Sends emails via SMTP. Defaults to Gmail free SMTP."""

    def __init__(self):
        self.smtp_host  = os.environ.get("SMTP_HOST",  "smtp.gmail.com")
        self.smtp_port  = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user  = os.environ.get("SMTP_USER",  "")   # your Gmail address
        self.smtp_pass  = os.environ.get("SMTP_PASS",  "")   # Gmail App Password
        self.from_email = os.environ.get("FROM_EMAIL", self.smtp_user) or "noreply@stocksage.app"
        self.enabled    = bool(self.smtp_user and self.smtp_pass)

    def send_alert_email(self, to_email: str, username: str, triggered_alerts: list) -> bool:
        """
        Send a price alert notification email.
        triggered_alerts: list of dicts with ticker, type, target, current.
        """
        if not self.enabled:
            # Log to console when email is not configured
            for a in triggered_alerts:
                print(f"[ALERT] {username} — {a['ticker']} went {a['type']} ${a['target']} (now ${a['current']})")
            return False

        subject = f"StockSage Alert: {len(triggered_alerts)} Price Alert(s) Triggered"
        html_body = self._build_alert_html(username, triggered_alerts)

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = f"StockSage <{self.from_email}>"
            msg["To"]      = to_email
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.from_email, to_email, msg.as_string())
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] Could not send alert email: {e}")
            return False

    def _build_alert_html(self, username: str, alerts: list) -> str:
        rows = ""
        for a in alerts:
            direction = "▲ above" if a["type"] == "above" else "▼ below"
            color = "#00ff88" if a["type"] == "above" else "#ef4444"
            rows += f"""
            <tr>
              <td style="padding:12px;font-family:monospace;font-size:16px;color:{color};font-weight:700">{a['ticker']}</td>
              <td style="padding:12px;font-family:monospace;color:#e2e8f0">{direction} ${a['target']:.2f}</td>
              <td style="padding:12px;font-family:monospace;color:#00ff88;font-weight:700">${a['current']:.2f}</td>
            </tr>"""

        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="background:#080c10;color:#e2e8f0;font-family:'Barlow',sans-serif;margin:0;padding:0">
          <div style="max-width:520px;margin:40px auto;background:#0d1117;border:1px solid #1e2d3d;border-radius:6px;overflow:hidden">
            <div style="background:#111820;padding:24px 28px;border-bottom:1px solid #1e2d3d">
              <div style="font-family:monospace;font-size:22px;color:#fff;letter-spacing:3px">
                STOCK<span style="color:#00ff88">SAGE</span>
              </div>
              <div style="font-size:11px;color:#4b5563;letter-spacing:1px;margin-top:4px">PRICE ALERT NOTIFICATION</div>
            </div>
            <div style="padding:24px 28px">
              <p style="color:#94a3b8;font-size:15px">Hey <strong style="color:#fff">{username}</strong>, your price alert(s) have been triggered:</p>
              <table style="width:100%;border-collapse:collapse;margin:16px 0;background:#111820;border:1px solid #1e2d3d;border-radius:4px">
                <thead>
                  <tr style="border-bottom:1px solid #1e2d3d">
                    <th style="padding:10px 12px;text-align:left;font-size:10px;letter-spacing:1.5px;color:#4b5563;font-family:monospace">TICKER</th>
                    <th style="padding:10px 12px;text-align:left;font-size:10px;letter-spacing:1.5px;color:#4b5563;font-family:monospace">CONDITION</th>
                    <th style="padding:10px 12px;text-align:left;font-size:10px;letter-spacing:1.5px;color:#4b5563;font-family:monospace">CURRENT PRICE</th>
                  </tr>
                </thead>
                <tbody>{rows}</tbody>
              </table>
              <p style="color:#6b7280;font-size:12px;margin-top:20px">
                Log in to <a href="#" style="color:#00ff88">StockSage</a> to update your alerts or add new ones.
              </p>
            </div>
            <div style="padding:16px 28px;border-top:1px solid #1e2d3d;font-size:11px;color:#374151;font-family:monospace">
              NOT FINANCIAL ADVICE. FOR EDUCATIONAL PURPOSES ONLY.
            </div>
          </div>
        </body>
        </html>"""
