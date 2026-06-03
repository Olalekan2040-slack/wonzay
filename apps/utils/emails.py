"""
Central email utility for Wonzays Kollections.
All transactional emails are sent from here using HTML + plain-text fallback.
"""

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

FROM = f"Wonzays Kollections <{settings.DEFAULT_FROM_EMAIL}>"


# ─── helpers ────────────────────────────────────────────────────────────────

def _wrap(title: str, body_html: str) -> str:
    """Wrap a content block in the branded email shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#F5F3FF;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" role="presentation"
       style="background:#F5F3FF;padding:32px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" role="presentation"
           style="background:#ffffff;border-radius:16px;overflow:hidden;max-width:600px;width:100%;">

      <!-- Header -->
      <tr>
        <td style="background:#1A0A38;padding:28px 40px;text-align:center;">
          <p style="margin:0;font-family:Georgia,serif;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:-0.01em;">
            Wonzays Kollections
          </p>
          <p style="margin:4px 0 0;font-size:10px;letter-spacing:0.18em;text-transform:uppercase;color:rgba(255,255,255,0.4);">
            Contemporary African Fashion
          </p>
        </td>
      </tr>

      <!-- Body -->
      <tr>
        <td style="padding:40px 40px 32px;">
          {body_html}
        </td>
      </tr>

      <!-- Footer -->
      <tr>
        <td style="background:#F7F5FF;padding:24px 40px;text-align:center;border-top:1px solid #E8E4F5;">
          <p style="margin:0 0 6px;font-size:12px;color:#A7A3C0;">
            Wonzays Kollections · Karalee, Ipswich QLD, Australia
          </p>
          <p style="margin:0;font-size:11px;color:#C4B8E8;">
            © 2026 Wonzays Kollections. All rights reserved.
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


def _send(subject: str, to: str, html: str, text: str) -> bool:
    """Send one email. Returns True on success, False on failure."""
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=FROM,
            to=[to],
        )
        msg.attach_alternative(html, "text/html")
        msg.send()
        return True
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("Email send failed to %s: %s", to, exc)
        return False


# ─── 1. Welcome email on registration ───────────────────────────────────────

def send_welcome_email(user) -> bool:
    name = user.first_name or user.email
    html = _wrap("Welcome to Wonzays Kollections", f"""
      <h1 style="font-family:Georgia,serif;font-size:28px;font-weight:700;color:#1A0A38;margin:0 0 12px;">
        Welcome, {name}! &#127881;
      </h1>
      <p style="font-size:15px;color:#3D2F5C;line-height:1.7;margin:0 0 20px;">
        Your Wonzays Kollections account is ready. You can now shop our latest
        African fashion collections, track orders, save items to your wishlist, and more.
      </p>

      <div style="background:#F7F5FF;border-radius:12px;padding:20px 24px;margin:0 0 24px;border-left:4px solid #5B4B8A;">
        <p style="margin:0 0 4px;font-size:13px;font-weight:600;color:#1A0A38;">Your welcome discount:</p>
        <p style="margin:0;font-size:22px;font-weight:700;color:#5B4B8A;letter-spacing:0.05em;">WONZAYS10</p>
        <p style="margin:4px 0 0;font-size:12px;color:#A7A3C0;">10% off your first order</p>
      </div>

      <table cellpadding="0" cellspacing="0" role="presentation">
        <tr>
          <td style="background:#2D1563;border-radius:10px;">
            <a href="https://wonzayskollections.com.au/collections/"
               style="display:inline-block;padding:14px 32px;font-size:14px;font-weight:700;color:#ffffff;text-decoration:none;letter-spacing:0.02em;">
              Shop Now →
            </a>
          </td>
        </tr>
      </table>

      <p style="margin:28px 0 0;font-size:13px;color:#A7A3C0;line-height:1.6;">
        If you didn't create this account, please ignore this email or
        <a href="mailto:wonzayskollections@gmail.com" style="color:#5B4B8A;">contact us</a>.
      </p>
    """)
    text = (
        f"Welcome to Wonzays Kollections, {name}!\n\n"
        "Your account is ready. Use code WONZAYS10 for 10% off your first order.\n\n"
        "Shop: https://wonzayskollections.com.au/collections/\n\n"
        "Wonzays Kollections · Karalee, Ipswich QLD"
    )
    return _send("Welcome to Wonzays Kollections! 🎉", user.email, html, text)


# ─── 2. Order confirmation ───────────────────────────────────────────────────

def send_order_confirmation(order) -> bool:
    recipient = (
        order.customer.email
        if order.customer
        else order.guest_email
    )
    if not recipient:
        return False

    name = (
        order.customer.first_name
        if order.customer and order.customer.first_name
        else order.shipping_address.full_name.split()[0]
        if order.shipping_address
        else "Customer"
    )

    # Build items table rows
    items_html = ""
    items_text = ""
    for item in order.items.all():
        items_html += f"""
          <tr>
            <td style="padding:10px 0;border-bottom:1px solid #F0EDFF;font-size:14px;color:#1A0A38;">{item.product_name}</td>
            <td style="padding:10px 0;border-bottom:1px solid #F0EDFF;font-size:14px;color:#6B6B7C;text-align:center;">&times;{item.quantity}</td>
            <td style="padding:10px 0;border-bottom:1px solid #F0EDFF;font-size:14px;font-weight:600;color:#1A0A38;text-align:right;">${item.line_total}</td>
          </tr>"""
        items_text += f"  - {item.product_name} x{item.quantity}  ${item.line_total}\n"

    addr = order.shipping_address
    addr_html = (
        f"{addr.full_name}<br/>{addr.address_line1}"
        f"{'<br/>' + addr.address_line2 if addr.address_line2 else ''}"
        f"<br/>{addr.city} {addr.state} {addr.postcode}<br/>{addr.country}"
        if addr else "—"
    )

    html = _wrap(f"Order Confirmation #{order.pk}", f"""
      <h1 style="font-family:Georgia,serif;font-size:26px;font-weight:700;color:#1A0A38;margin:0 0 6px;">
        Thank you, {name}!
      </h1>
      <p style="font-size:15px;color:#5B4B8A;margin:0 0 24px;">
        We've received your order and it's being prepared.
      </p>

      <div style="background:#F7F5FF;border-radius:10px;padding:16px 20px;margin:0 0 24px;display:inline-block;">
        <p style="margin:0;font-size:12px;color:#A7A3C0;text-transform:uppercase;letter-spacing:0.08em;">Order Number</p>
        <p style="margin:4px 0 0;font-size:20px;font-weight:700;color:#2D1563;">#{order.pk}</p>
      </div>

      <!-- Items -->
      <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="margin-bottom:24px;">
        <tr>
          <th style="text-align:left;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#A7A3C0;padding-bottom:8px;border-bottom:2px solid #E8E4F5;">Item</th>
          <th style="text-align:center;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#A7A3C0;padding-bottom:8px;border-bottom:2px solid #E8E4F5;">Qty</th>
          <th style="text-align:right;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#A7A3C0;padding-bottom:8px;border-bottom:2px solid #E8E4F5;">Price</th>
        </tr>
        {items_html}
        <tr>
          <td colspan="2" style="padding:12px 0 0;font-size:14px;font-weight:600;color:#1A0A38;">Shipping</td>
          <td style="padding:12px 0 0;font-size:14px;font-weight:600;color:#1A0A38;text-align:right;">${order.shipping_cost}</td>
        </tr>
        <tr>
          <td colspan="2" style="padding:8px 0 0;font-size:16px;font-weight:700;color:#1A0A38;border-top:2px solid #E8E4F5;">Total</td>
          <td style="padding:8px 0 0;font-size:18px;font-weight:700;color:#2D1563;text-align:right;border-top:2px solid #E8E4F5;">${order.total}</td>
        </tr>
      </table>

      <!-- Shipping address -->
      <div style="background:#F7F5FF;border-radius:10px;padding:16px 20px;margin-bottom:28px;">
        <p style="margin:0 0 6px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#A7A3C0;">Shipping To</p>
        <p style="margin:0;font-size:14px;color:#1A0A38;line-height:1.6;">{addr_html}</p>
      </div>

      <p style="font-size:13px;color:#6B6B7C;line-height:1.6;margin:0;">
        We'll send you another email when your order ships. If you have questions,
        reply to this email or contact us at
        <a href="mailto:wonzayskollections@gmail.com" style="color:#5B4B8A;">wonzayskollections@gmail.com</a>.
      </p>
    """)

    text = (
        f"Thank you, {name}! Your order #{order.pk} has been received.\n\n"
        f"ITEMS:\n{items_text}\n"
        f"Shipping: ${order.shipping_cost}\n"
        f"Total: ${order.total}\n\n"
        f"We'll email you when it ships.\n\n"
        f"Wonzays Kollections · wonzayskollections@gmail.com"
    )
    return _send(f"Order Confirmed #{order.pk} — Wonzays Kollections", recipient, html, text)


# ─── 3. Password changed notification ───────────────────────────────────────

def send_password_changed_email(user) -> bool:
    from django.utils import timezone
    name = user.first_name or user.email
    time_str = timezone.now().strftime("%d %b %Y at %H:%M %Z")
    html = _wrap("Password Changed", f"""
      <h1 style="font-family:Georgia,serif;font-size:24px;font-weight:700;color:#1A0A38;margin:0 0 12px;">
        Password Updated
      </h1>
      <p style="font-size:15px;color:#3D2F5C;line-height:1.7;margin:0 0 20px;">
        Hi {name}, your Wonzays Kollections account password was changed on <strong>{time_str}</strong>.
      </p>

      <div style="background:#FFF3F3;border-radius:10px;padding:16px 20px;margin:0 0 24px;border-left:4px solid #EF4444;">
        <p style="margin:0;font-size:14px;color:#7F1D1D;line-height:1.6;">
          <strong>Not you?</strong> Please
          <a href="https://wonzayskollections.com.au/accounts/password-reset/" style="color:#DC2626;">reset your password immediately</a>
          and contact us at
          <a href="mailto:wonzayskollections@gmail.com" style="color:#DC2626;">wonzayskollections@gmail.com</a>.
        </p>
      </div>

      <p style="font-size:13px;color:#A7A3C0;line-height:1.6;margin:0;">
        If this was you, no further action is needed. Your account is secure.
      </p>
    """)
    text = (
        f"Hi {name}, your Wonzays Kollections password was changed on {time_str}.\n\n"
        "If this wasn't you, reset your password immediately and contact us.\n\n"
        "Wonzays Kollections · wonzayskollections@gmail.com"
    )
    return _send("Your password has been changed — Wonzays Kollections", user.email, html, text)


# ─── 4. Newsletter subscription confirmation ─────────────────────────────────

def send_newsletter_welcome(email: str, first_name: str = "") -> bool:
    name = first_name or "there"
    html = _wrap("Welcome — Wonzays Newsletter", f"""
      <h1 style="font-family:Georgia,serif;font-size:26px;font-weight:700;color:#1A0A38;margin:0 0 12px;">
        You're in, {name}! &#127881;
      </h1>
      <p style="font-size:15px;color:#3D2F5C;line-height:1.7;margin:0 0 20px;">
        Welcome to the Wonzays Kollections community. You'll be the first to know about
        new arrivals, exclusive deals, and style inspiration.
      </p>

      <div style="background:#F7F5FF;border-radius:12px;padding:20px 24px;margin:0 0 28px;text-align:center;border:2px dashed #C4B5FD;">
        <p style="margin:0 0 4px;font-size:13px;color:#6B6B7C;">Here's your welcome gift</p>
        <p style="margin:0;font-size:28px;font-weight:700;color:#5B4B8A;letter-spacing:0.06em;">WONZAYS10</p>
        <p style="margin:6px 0 0;font-size:12px;color:#A7A3C0;">10% off your first order · Single use</p>
      </div>

      <table cellpadding="0" cellspacing="0" role="presentation" style="margin-bottom:28px;">
        <tr>
          <td style="background:#2D1563;border-radius:10px;">
            <a href="https://wonzayskollections.com.au/collections/"
               style="display:inline-block;padding:14px 32px;font-size:14px;font-weight:700;color:#ffffff;text-decoration:none;">
              Browse New Arrivals →
            </a>
          </td>
        </tr>
      </table>

      <p style="font-size:12px;color:#C4B8E8;line-height:1.6;margin:0;">
        You're receiving this because you subscribed at wonzayskollections.com.au.
        Don't want these emails?
        <a href="https://wonzayskollections.com.au/newsletter/unsubscribe/" style="color:#A7A3C0;">Unsubscribe</a>.
      </p>
    """)
    text = (
        f"Hey {name}, you're subscribed to Wonzays Kollections!\n\n"
        "Use code WONZAYS10 for 10% off your first order.\n\n"
        "Shop: https://wonzayskollections.com.au/collections/\n\n"
        "Wonzays Kollections · Karalee, Ipswich QLD"
    )
    return _send("Welcome to Wonzays Kollections 🎉 Here's 10% off", email, html, text)
