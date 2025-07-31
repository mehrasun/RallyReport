from datetime import datetime, timedelta, timezone
import requests
from app.utils import auth, get_build_date
from app.jenkins_config import JENKINS_URL, REGION_MAP

def get_last_7_days(selected_date):
    return [(selected_date - timedelta(days=i)) for i in range(0, 7)]

def init_trend_data(dates):
    return {str(d): {"passed": 0, "failed": 0, "aborted": 0} for d in dates}

def fetch_weekly_data(selected_date):
    if selected_date > datetime.now(timezone.utc).date():
        return None

    last_7_days = get_last_7_days(selected_date)
    # last_7_days_str = [str(d) for d in sorted(last_7_days)]
    trend_data = {}

    for region_key, meta in REGION_MAP.items():
        view_path = f"view/{meta['view']}"
        trend_data[region_key] = init_trend_data(last_7_days)

        for folder_list in meta["folders"]:
            folder_path = "/".join([f"job/{f}" for f in folder_list])
            api_url = f"{JENKINS_URL}/{view_path}/{folder_path}/api/json?tree=jobs[url,color]"
            response = requests.get(api_url, auth=auth)
            if response.status_code != 200:
                continue

            jobs = response.json().get("jobs", [])
            for job in jobs:
                if job['color'] in ["notbuilt", "grey", "disabled"]:
                    continue

                job_url = job["url"]
                builds_api_url = f"{job_url}api/json?tree=builds[number,result,timestamp]"
                builds_response = requests.get(builds_api_url, auth=auth)
                if builds_response.status_code != 200:
                    continue

                builds = builds_response.json().get("builds", [])
                seen_dates = set()
                for build in builds:
                    timestamp = build.get("timestamp")
                    result = build.get("result")
                    if not timestamp or not result:
                        continue

                    build_date = get_build_date(timestamp)

                    if build_date in last_7_days and build_date not in seen_dates:
                        seen_dates.add(build_date)
                        date_str = str(build_date)
                        if result == "SUCCESS":
                            trend_data[region_key][date_str]["passed"] += 1
                        elif result == "FAILURE":
                            trend_data[region_key][date_str]["failed"] += 1
                        elif result == "ABORTED":
                            trend_data[region_key][date_str]["aborted"] += 1

    return {
        "trend_data": {
            region: {
                str(date): trend_data[region][str(date)]
                for date in sorted(last_7_days)
            } for region in trend_data
        }
    }
