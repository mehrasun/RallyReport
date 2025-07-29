from requests.auth import HTTPBasicAuth
from app.jenkins_config import USERNAME, PASSWORD
from datetime import datetime, timedelta, timezone
import requests

auth = HTTPBasicAuth(USERNAME, PASSWORD) if USERNAME and PASSWORD else None
utc_timezone = timezone.utc

def time_ago(dt, jenkins_tz):
    now_jenkins = datetime.now(jenkins_tz)
    diff = now_jenkins - dt

    if diff.total_seconds() < 60:
        return "Just now"
    elif diff.total_seconds() < 3600:
        mins = int(diff.total_seconds() / 60)
        return f"{mins} minute{'s' if mins > 1 else ''} ago"
    elif diff.total_seconds() < 86400:
        hrs = int(diff.total_seconds() / 3600)
        return f"{hrs} hour{'s' if hrs > 1 else ''} ago"
    else:
        days = diff.days
        return f"{days} day{'s' if days > 1 else ''} ago"

def get_build_date(timestamp):
    dt = datetime.fromtimestamp(timestamp / 1000, tz=utc_timezone)
    return dt.date()

def fetch_latest_build(job_url, selected_date):
    last_build_url = f"{job_url}lastBuild/api/json"
    response = requests.get(last_build_url, auth=auth)
    if response.status_code != 200:
        return None
    build_info = response.json()
    if build_info.get("building"):
        return None
    timestamp = build_info.get("timestamp")
    if not timestamp:
        return None
    build_date = get_build_date(timestamp)
    if build_date == selected_date:
        return build_info
    else:
        return None

def get_latest_build_on_date(job_url, selected_date):
    """
    Fetch the latest completed build JSON for a given job URL on a specific date.
    Returns build JSON or None.
    """
    try:
        # Normalize selected_date string to date object
        if isinstance(selected_date, str):
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

        # Fetch all builds (basic metadata)
        api_url = f"{job_url}api/json?tree=builds[number,url]"
        response = requests.get(api_url, auth=auth)
        if response.status_code != 200:
            print(f"Failed to fetch builds: {response.status_code}")
            return None

        builds = response.json().get("builds", [])

        for build in builds:
            build_number = build["number"]
            build_api_url = f"{job_url}{build_number}/api/json"
            build_response = requests.get(build_api_url, auth=auth)

            if build_response.status_code != 200:
                continue
            build_info = build_response.json()
            timestamp = build_info["timestamp"]
            build_date = get_build_date(timestamp)

            if build_date < selected_date:
                break

            if build_date == selected_date:
                if build_info.get("building"):
                    continue  # skip in-progress
                return build_info  # ✅ Return completed build JSON

        return None  # No completed builds found on selected_date

    except Exception as e:
        print(f"Error fetching build on {selected_date} from {job_url}: {e}")
        return None
