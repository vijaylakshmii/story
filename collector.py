"""
Content Research Collector — Reddit + YouTube
------------------------------------------------
Pulls top posts/comments from Reddit (public JSON endpoint, no app needed)
and YouTube (Data API v3) for a fixed list of subreddits and channels.
Saves raw results to timestamped JSON files for the analyzer step to use.

Usage:
    python collector.py

Requirements:
    pip install requests

Config:
    Set these as environment variables before running (do not hardcode
    secrets in this file):
        YOUTUBE_API_KEY   - your YouTube Data API v3 key
        REDDIT_USERNAME   - your Reddit username (used only in the
                             User-Agent string Reddit asks API callers to send)
"""

import os
import requests
import time
import json
from datetime import datetime, timezone

# ============================================================
# CONFIG
# ============================================================

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# Reddit doesn't need a key for the public JSON endpoint — just a
# descriptive User-Agent so Reddit doesn't block the request.
REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME", "anonymous")
REDDIT_USER_AGENT = f"content-research-tool by u/{REDDIT_USERNAME}"

SUBREDDITS = [
    "MBA", "MBAIndia", "business_school", "MBAadmissions",
    "GMAT", "CATpreparation",
    "IndianWorkplace", "developersIndia", "CollegeAdmissionsIndia", "careerguidance",
    "consulting",
    "startups", "IndianStartups", "Entrepreneur", "venturecapital",
    "ycombinator", "SaaS", "indiehackers", "StartUpIndia",
]

# YouTube channel IDs (resolved from the handles we looked up earlier)
YOUTUBE_CHANNELS = {
    "Shweta Arora": "UChUvKQ5WX6YQlP3dYh-bgCQ",
    "Ankur Warikoo": "UCRzYN32xtBf3Yxsx5BvJWJw",
    # Add more as you confirm channel IDs:
    # "InsideIIM": "UC...",
    # "Kushal Lodha": "UC...",
    # "ChetChat": "UC...",
    # "Career Launcher": "UC...",
}

REDDIT_POSTS_PER_SUB = 25
REDDIT_COMMENTS_PER_POST = 30
YOUTUBE_VIDEOS_PER_CHANNEL = 5
YOUTUBE_COMMENTS_PER_VIDEO = 40

OUTPUT_DIR = "."  # change if you want a specific folder

# ============================================================
# REDDIT COLLECTION (public JSON, no auth)
# ============================================================

def fetch_subreddit_top(subreddit, limit=25, timeframe="week"):
    """Fetch top posts from a subreddit using Reddit's public JSON endpoint."""
    url = f"https://www.reddit.com/r/{subreddit}/top.json"
    params = {"limit": limit, "t": timeframe}
    headers = {"User-Agent": REDDIT_USER_AGENT}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data["data"]["children"]
    except Exception as e:
        print(f"  [!] Failed to fetch r/{subreddit}: {e}")
        return []


def fetch_post_comments(subreddit, post_id, limit=30):
    """Fetch top-level comments for a specific post."""
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    headers = {"User-Agent": REDDIT_USER_AGENT}

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        comments_raw = data[1]["data"]["children"]
        comments = []
        for c in comments_raw[:limit]:
            body = c.get("data", {}).get("body")
            if body and body not in ("[deleted]", "[removed]"):
                comments.append(body)
        return comments
    except Exception as e:
        print(f"    [!] Failed to fetch comments for post {post_id}: {e}")
        return []


def collect_reddit():
    print("Collecting Reddit data...")
    all_posts = []

    for sub in SUBREDDITS:
        print(f"  r/{sub}")
        posts = fetch_subreddit_top(sub, limit=REDDIT_POSTS_PER_SUB)
        time.sleep(2)  # be polite to Reddit's unauthenticated rate limit

        for p in posts:
            pdata = p.get("data", {})
            post_id = pdata.get("id")
            comments = fetch_post_comments(sub, post_id, limit=REDDIT_COMMENTS_PER_POST)
            time.sleep(2)

            all_posts.append({
                "source": f"r/{sub}",
                "title": pdata.get("title"),
                "selftext": pdata.get("selftext", ""),
                "score": pdata.get("score"),
                "num_comments": pdata.get("num_comments"),
                "url": f"https://www.reddit.com{pdata.get('permalink', '')}",
                "created_utc": pdata.get("created_utc"),
                "comments": comments,
            })

    print(f"  Collected {len(all_posts)} Reddit posts total.")
    return all_posts


# ============================================================
# YOUTUBE COLLECTION (Data API v3)
# ============================================================

YT_BASE = "https://www.googleapis.com/youtube/v3"


def get_recent_video_ids(channel_id, max_results=5):
    """Get the most recent video IDs for a channel using the search endpoint."""
    url = f"{YT_BASE}/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "id",
        "order": "date",
        "maxResults": max_results,
        "type": "video",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return [item["id"]["videoId"] for item in data.get("items", [])]
    except Exception as e:
        print(f"  [!] Failed to fetch videos for channel {channel_id}: {e}")
        return []


def get_video_details(video_id):
    url = f"{YT_BASE}/videos"
    params = {"key": YOUTUBE_API_KEY, "id": video_id, "part": "snippet,statistics"}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        return items[0] if items else None
    except Exception as e:
        print(f"    [!] Failed to fetch details for video {video_id}: {e}")
        return None


def get_video_comments(video_id, max_results=40):
    url = f"{YT_BASE}/commentThreads"
    params = {
        "key": YOUTUBE_API_KEY,
        "videoId": video_id,
        "part": "snippet",
        "maxResults": min(max_results, 100),
        "order": "relevance",
        "textFormat": "plainText",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        comments = []
        for item in items:
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append(snippet.get("textDisplay", ""))
        return comments
    except Exception as e:
        # Comments can be disabled on some videos — this is expected sometimes
        print(f"    [!] Could not fetch comments for video {video_id}: {e}")
        return []


def collect_youtube():
    print("Collecting YouTube data...")
    all_videos = []

    for channel_name, channel_id in YOUTUBE_CHANNELS.items():
        print(f"  {channel_name}")
        video_ids = get_recent_video_ids(channel_id, max_results=YOUTUBE_VIDEOS_PER_CHANNEL)

        for vid in video_ids:
            details = get_video_details(vid)
            comments = get_video_comments(vid, max_results=YOUTUBE_COMMENTS_PER_VIDEO)

            title = details["snippet"]["title"] if details else None
            views = details["statistics"].get("viewCount") if details else None

            all_videos.append({
                "source": channel_name,
                "video_id": vid,
                "title": title,
                "views": views,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "comments": comments,
            })

    print(f"  Collected {len(all_videos)} YouTube videos total.")
    return all_videos


# ============================================================
# MAIN
# ============================================================

def main():
    if not YOUTUBE_API_KEY:
        print("[!] YOUTUBE_API_KEY environment variable is not set — YouTube "
              "requests will fail. Set it before running, e.g.:\n"
              "      export YOUTUBE_API_KEY=your_key_here")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    reddit_data = collect_reddit()
    reddit_path = f"{OUTPUT_DIR}/reddit_{timestamp}.json"
    with open(reddit_path, "w", encoding="utf-8") as f:
        json.dump(reddit_data, f, ensure_ascii=False, indent=2)
    print(f"Saved Reddit data to {reddit_path}")

    youtube_data = collect_youtube()
    youtube_path = f"{OUTPUT_DIR}/youtube_{timestamp}.json"
    with open(youtube_path, "w", encoding="utf-8") as f:
        json.dump(youtube_data, f, ensure_ascii=False, indent=2)
    print(f"Saved YouTube data to {youtube_path}")

    print("\nDone. Next step: run the analyzer script on these two files.")


if __name__ == "__main__":
    main()
