"""
Facebook Graph API Client for Hamara Gujranwala Page.
Supports posting photos, text, verifying Page Access Token, and tracking follower counts.
"""

import os
import requests
from config import FB_PAGE_ACCESS_TOKEN, GRAPH_API_BASE_URL, PAGE_ID, PAGE_NAME


class FacebookPoster:
    def __init__(self, page_id=None, access_token=None):
        self.page_id = str(page_id or PAGE_ID).strip()
        self.raw_token = (access_token or FB_PAGE_ACCESS_TOKEN or "").strip()
        self.base_url = GRAPH_API_BASE_URL
        self._page_token = None

    def is_configured(self):
        """Check if access token is available."""
        return bool(self.raw_token and self.raw_token != "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN")

    def get_effective_page_token(self):
        """
        Ensure we are using a Page Access Token, not a User Access Token.
        If a User Access Token was provided, automatically query Graph API
        to resolve the actual Page Access Token for this Page ID.
        """
        if self._page_token:
            return self._page_token

        if not self.is_configured():
            return ""

        # Step 1: Check if raw_token directly gives access_token for the Page
        try:
            url = f"{self.base_url}/{self.page_id}"
            resp = requests.get(url, params={"fields": "access_token,name", "access_token": self.raw_token}, timeout=15)
            data = resp.json()
            if resp.status_code == 200 and "access_token" in data:
                print(f"🔄 Automatically resolved Page Access Token for '{data.get('name', self.page_id)}'!")
                self._page_token = data["access_token"]
                return self._page_token
        except Exception as e:
            print(f"Notice: Direct page token lookup: {e}")

        # Step 2: Try /me/accounts in case raw_token is a User Token with pages_show_list
        try:
            url = f"{self.base_url}/me/accounts"
            resp = requests.get(url, params={"access_token": self.raw_token}, timeout=15)
            data = resp.json()
            if "data" in data and isinstance(data["data"], list):
                for page in data["data"]:
                    p_id = str(page.get("id"))
                    p_name = page.get("name")
                    if p_id == self.page_id or "gujranwala" in p_name.lower():
                        if "access_token" in page:
                            print(f"🔄 Found Page Access Token in /me/accounts for '{p_name}' ({p_id})!")
                            self.page_id = p_id
                            self._page_token = page["access_token"]
                            return self._page_token
                # Fallback: If only 1 page is managed, use its token
                if len(data["data"]) == 1 and "access_token" in data["data"][0]:
                    page = data["data"][0]
                    print(f"🔄 Using Page Access Token for managed page '{page.get('name')}' ({page.get('id')})!")
                    self.page_id = str(page.get("id"))
                    self._page_token = page["access_token"]
                    return self._page_token
        except Exception as e:
            print(f"Notice: me/accounts lookup: {e}")

        # Step 3: Default to raw_token
        self._page_token = self.raw_token
        return self._page_token

    def get_page_stats(self):
        """Fetch live page statistics (Follower count, likes)."""
        if not self.is_configured():
            return {
                "configured": False,
                "name": PAGE_NAME,
                "page_id": self.page_id,
                "followers": 0,
                "likes": 0,
                "message": "FB_PAGE_ACCESS_TOKEN not set in environment/secrets."
            }

        token = self.get_effective_page_token()
        url = f"{self.base_url}/{self.page_id}"
        params = {
            "fields": "id,name,followers_count,fan_count,verification_status",
            "access_token": token
        }

        try:
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            if resp.status_code == 200:
                return {
                    "configured": True,
                    "name": data.get("name", PAGE_NAME),
                    "page_id": data.get("id", self.page_id),
                    "followers": data.get("followers_count", 0),
                    "likes": data.get("fan_count", 0),
                    "raw": data
                }
            else:
                return {
                    "configured": False,
                    "error": data.get("error", {}).get("message", "API Error"),
                    "code": resp.status_code
                }
        except Exception as e:
            return {"configured": False, "error": str(e)}

    def post_photo(self, image_path, caption):
        """
        Post a photo with caption to the Facebook Page feed.
        """
        if not self.is_configured():
            print(f"[SIMULATION / DRY-RUN] Would post photo '{image_path}' to Page {self.page_id}.")
            print("Caption Preview:")
            print(caption[:200] + "...")
            return {
                "success": True,
                "mode": "simulation",
                "id": "dry_run_post_id",
                "message": "Simulated successfully. Configure FB_PAGE_ACCESS_TOKEN for live posting."
            }

        if not os.path.exists(image_path):
            return {"success": False, "error": f"Image file not found: {image_path}"}

        token = self.get_effective_page_token()
        url = f"{self.base_url}/{self.page_id}/photos"
        data = {
            "caption": caption,
            "access_token": token
        }

        try:
            with open(image_path, "rb") as img_file:
                files = {"source": img_file}
                resp = requests.post(url, data=data, files=files, timeout=30)
            
            result = resp.json()
            if resp.status_code == 200 and "id" in result:
                post_id = result.get("post_id", result.get("id"))
                print(f"✅ Successfully posted to Facebook Page! Post ID: {post_id}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "id": result.get("id"),
                    "mode": "live"
                }
            else:
                err_msg = result.get("error", {}).get("message", "Unknown Facebook API error")
                err_code = result.get("error", {}).get("code")
                print(f"❌ Failed to post photo to Facebook: {err_msg} (Code: {err_code})")
                return {"success": False, "error": err_msg, "code": err_code, "raw": result}
        except Exception as e:
            print(f"❌ Exception posting photo: {e}")
            return {"success": False, "error": str(e)}

    def post_text(self, message, link=None):
        """
        Post a text/link status update to the Facebook Page feed.
        """
        if not self.is_configured():
            print(f"[SIMULATION / DRY-RUN] Would post text update to Page {self.page_id}.")
            return {
                "success": True,
                "mode": "simulation",
                "id": "dry_run_feed_id"
            }

        token = self.get_effective_page_token()
        url = f"{self.base_url}/{self.page_id}/feed"
        data = {
            "message": message,
            "access_token": token
        }
        if link:
            data["link"] = link

        try:
            resp = requests.post(url, data=data, timeout=20)
            result = resp.json()
            if resp.status_code == 200 and "id" in result:
                print(f"✅ Successfully posted feed update! ID: {result['id']}")
                return {"success": True, "post_id": result["id"], "mode": "live"}
            else:
                err_msg = result.get("error", {}).get("message", "Unknown error")
                print(f"❌ Facebook post failed: {err_msg}")
                return {"success": False, "error": err_msg}
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    poster = FacebookPoster()
    stats = poster.get_page_stats()
    print("Page Connection Status:", stats)
