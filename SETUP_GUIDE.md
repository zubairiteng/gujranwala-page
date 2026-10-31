# 🔑 Step-by-Step Facebook Page Token & Secrets Setup Guide

To enable automated posting to **Hamara Gujranwala** (`Page ID: 61578710350501`), Meta requires a **Page Access Token**.

Follow these simple steps (takes under 3 minutes):

---

## Step 1: Open Meta Graph API Explorer
1. Go to [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer/).
2. Log in with your Facebook account that manages **Hamara Gujranwala**.
3. Under **Meta App**, select your existing App (or click *Create App* -> Select *Other* -> *Business*).

---

## Step 2: Grant Page Permissions
In the right-hand panel under **User or Page**, select **User Token**.
Add the following permissions from the dropdown:
- `pages_show_list`
- `pages_read_engagement`
- `pages_manage_posts`

Click **Generate Access Token** and approve the popup dialog.

---

## Step 3: Switch to "Hamara Gujranwala" Page Token
1. In the **User or Page** dropdown, switch from *User Token* to **Hamara Gujranwala**.
2. The token displayed in the box is now your **Page Access Token**!
3. Copy this token string (starts with `EAA...`).

> **Tip for a Never-Expiring Token:**
> In Graph API Explorer, query:
> `GET /me/accounts`
> Click "Submit". In the response JSON, look for `"access_token"` next to `"name": "Hamara Gujranwala"`. That token will never expire as long as you remain page admin.

---

## Step 4: Add the Token to GitHub Secrets
1. Open your repository settings:  
   👉 [https://github.com/zubairiteng/gujranwala-page/settings/secrets/actions](https://github.com/zubairiteng/gujranwala-page/settings/secrets/actions)
2. Click **New repository secret**.
3. Add Secret 1:
   - **Name:** `FB_PAGE_ACCESS_TOKEN`
   - **Secret:** Paste your copied token (e.g., `EAAB...`)
4. Add Secret 2 (optional, already defaulted in code):
   - **Name:** `FB_PAGE_ID`
   - **Secret:** `61578710350501`
5. Click **Add secret**.

---

## Step 5: Test 1-Click Publishing
1. Go to **Actions** in your GitHub repo:  
   👉 [https://github.com/zubairiteng/gujranwala-page/actions](https://github.com/zubairiteng/gujranwala-page/actions)
2. Click **Hamara Gujranwala Facebook Autonomous Manager** on the left.
3. Click **Run workflow** -> Select `auto` or `hero` -> Click the green **Run workflow** button.
4. Your post with a branded card will appear live on **Hamara Gujranwala** within 60 seconds!
