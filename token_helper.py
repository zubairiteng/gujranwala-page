"""
Token Helper for Hamara Gujranwala Facebook Automation.
Exchanges short-lived tokens for Never-Expiring (Permanent) Page Access Tokens.
"""

import requests
import subprocess
import sys


def debug_token(token):
    """Inspect token validity and expiration without needing App Secret."""
    url = "https://graph.facebook.com/v21.0/me"
    r = requests.get(url, params={"fields": "id,name", "access_token": token})
    print(f"Token /me check: {r.status_code} - {r.json()}")
    return r.status_code == 200


def get_permanent_page_token(app_id, app_secret, short_lived_user_token):
    """
    1. Exchange short-lived user token for 60-day long-lived user token.
    2. Query /me/accounts using long-lived user token to retrieve
       the Never-Expiring Page Access Token for Hamara Gujranwala.
    """
    print("🔄 Step 1: Exchanging short-lived user token for 60-day user token...")
    exchange_url = "https://graph.facebook.com/v21.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_user_token
    }
    r = requests.get(exchange_url, params=params)
    data = r.json()
    if "access_token" not in data:
        print("❌ Failed to exchange token:", data)
        return None

    long_lived_user_token = data["access_token"]
    print("✅ Successfully acquired 60-day Long-Lived User Token!")

    print("🔄 Step 2: Fetching Never-Expiring Page Token from /me/accounts...")
    accounts_url = "https://graph.facebook.com/v21.0/me/accounts"
    r2 = requests.get(accounts_url, params={"access_token": long_lived_user_token})
    acc_data = r2.json()

    if "data" not in acc_data or not acc_data["data"]:
        print("❌ No pages found in /me/accounts:", acc_data)
        return None

    page_token = None
    page_name = None
    for page in acc_data["data"]:
        p_name = page.get("name", "")
        p_id = str(page.get("id"))
        print(f" - Found Page: {p_name} (ID: {p_id})")
        if "gujranwala" in p_name.lower() or p_id in ["773745422479703", "61578710350501"]:
            page_token = page.get("access_token")
            page_name = p_name
            break

    if not page_token:
        # Default to first page
        first = acc_data["data"][0]
        page_token = first.get("access_token")
        page_name = first.get("name")

    print(f"🎉 SUCCESS! Acquired Permanent Page Token for '{page_name}'!")
    return page_token


def save_token_to_github_secret(token, repo="zubairiteng/gujranwala-page"):
    """Save token to GitHub Secrets via gh CLI."""
    cmd = ["gh", "secret", "set", "FB_PAGE_ACCESS_TOKEN", "--repo", repo, "--body", token]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print("✅ Saved FB_PAGE_ACCESS_TOKEN to GitHub Secrets successfully!")
        return True
    else:
        print("❌ Failed to save secret:", res.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) == 2:
        token = sys.argv[1]
        debug_token(token)
    elif len(sys.argv) == 4:
        app_id = sys.argv[1]
        app_secret = sys.argv[2]
        user_tok = sys.argv[3]
        perm_tok = get_permanent_page_token(app_id, app_secret, user_tok)
        if perm_tok:
            save_token_to_github_secret(perm_tok)
    else:
        print("Usage:")
        print("  python token_helper.py <token>                     (debug token)")
        print("  python token_helper.py <app_id> <app_sec> <token>  (convert to permanent & save)")
