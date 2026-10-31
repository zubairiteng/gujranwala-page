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
        self._resolved_target_id = None

    def is_configured(self):
        """Check if access token is available."""
        return bool(self.raw_token and self.raw_token != "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN")

    def resolve_target_and_token(self):
        """
        Identify the true Page ID and effective Page Token.
        Uses /me to automatically adapt to New Pages Experience (NPE) IDs.
        """
        if self._page_token and self._resolved_target_id:
            return self._resolved_target_id, self._page_token

        if not self.is_configured():
            return self.page_id, ""

        token = self.raw_token

        # Check /me with current token
        try:
            resp = requests.get(f"{self.base_url}/me", params={"fields": "id,name", "access_token": token}, timeout=15)
            me_data = resp.json()
            if resp.status_code == 200 and "id" in me_data:
                print(f"🎯 Target entity from /me: '{me_data.get('name')}' (ID: {me_data.get('id')})")
                self._resolved_target_id = str(me_data["id"])
                self._page_token = token
                return self._resolved_target_id, self._page_token
        except Exception as e:
            print(f"Notice: /me check: {e}")

        # Check /me/accounts in case token is a User token managing the Page
        try:
            url = f"{self.base_url}/me/accounts"
            resp = requests.get(url, params={"access_token": token}, timeout=15)
            data = resp.json()
            if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                for page in data["data"]:
                    p_id = str(page.get("id"))
                    p_name = page.get("name")
                    if "gujranwala" in p_name.lower() or p_id == self.page_id:
                        print(f"🔄 Using Page Token for '{p_name}' (ID: {p_id}) from /me/accounts")
                        self._resolved_target_id = p_id
                        self._page_token = page.get("access_token", token)
                        return self._resolved_target_id, self._page_token
                # First managed page
                first_page = data["data"][0]
                self._resolved_target_id = str(first_page.get("id"))
                self._page_token = first_page.get("access_token", token)
                return self._resolved_target_id, self._page_token
        except Exception as e:
            print(f"Notice: me/accounts lookup: {e}")

        # Fallback to defaults
        self._resolved_target_id = "me"
        self._page_token = token
        return self._resolved_target_id, self._page_token

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

        target_id, token = self.resolve_target_and_token()
        url = f"{self.base_url}/{target_id}"
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
                    "page_id": data.get("id", target_id),
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

        target_id, token = self.resolve_target_and_token()

        # Primary attempt: Try resolved target ID and 'me'
        targets_to_try = [target_id]
        if target_id != "me":
            targets_to_try.append("me")
        if target_id != "773745422479703" and "773745422479703" not in targets_to_try:
            targets_to_try.append("773745422479703")

        last_error = None
        for t_id in targets_to_try:
            url = f"{self.base_url}/{t_id}/photos"
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
                    print(f"✅ Successfully posted to Facebook Page! Post ID: {post_id} (Target: {t_id})")
                    return {
                        "success": True,
                        "post_id": post_id,
                        "id": result.get("id"),
                        "mode": "live",
                        "target": t_id
                    }
                else:
                    err_msg = result.get("error", {}).get("message", "Unknown Facebook API error")
                    err_code = result.get("error", {}).get("code")
                    print(f"Notice: Failed target '{t_id}': {err_msg} (Code: {err_code})")
                    last_error = err_msg
            except Exception as e:
                print(f"Notice: Exception on target '{t_id}': {e}")
                last_error = str(e)

        # Fallback attempt: Post as text feed update if photo upload is restricted
        print("🔄 Attempting fallback: posting to feed...")
        feed_res = self.post_text(caption)
        if feed_res.get("success"):
            return feed_res

        return {"success": False, "error": last_error}

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

        target_id, token = self.resolve_target_and_token()
        targets = [target_id]
        if target_id != "me":
            targets.append("me")

        for t_id in targets:
            url = f"{self.base_url}/{t_id}/feed"
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
                    print(f"✅ Successfully posted feed update! ID: {result['id']} (Target: {t_id})")
                    return {"success": True, "post_id": result["id"], "mode": "live"}
                else:
                    err_msg = result.get("error", {}).get("message", "Unknown error")
                    print(f"Notice on feed {t_id}: {err_msg}")
            except Exception as e:
                print(f"Notice on feed {t_id}: {e}")

        return {"success": False, "error": "Feed update failed across all targets"}
