"""
Facebook Graph API Client for Hamara Gujranwala Page.
Supports posting photos, text, verifying Page Access Token, and tracking follower counts.
"""

import os
import requests
from config import FB_PAGE_ACCESS_TOKEN, GRAPH_API_BASE_URL, PAGE_ID, PAGE_NAME


class FacebookPoster:
    def __init__(self, page_id=None, access_token=None):
        self.page_id = page_id or PAGE_ID
        self.access_token = (access_token or FB_PAGE_ACCESS_TOKEN or "").strip()
        self.base_url = GRAPH_API_BASE_URL

    def is_configured(self):
        """Check if access token is available."""
        return bool(self.access_token and self.access_token != "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN")

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

        url = f"{self.base_url}/{self.page_id}"
        params = {
            "fields": "id,name,followers_count,fan_count,verification_status",
            "access_token": self.access_token
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

        url = f"{self.base_url}/{self.page_id}/photos"
        data = {
            "caption": caption,
            "access_token": self.access_token
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
                print(f"❌ Failed to post photo to Facebook: {err_msg}")
                return {"success": False, "error": err_msg, "raw": result}
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

        url = f"{self.base_url}/{self.page_id}/feed"
        data = {
            "message": message,
            "access_token": self.access_token
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
