from datetime import datetime, timedelta, timezone
import requests
from app.utils import auth, get_latest_build_on_date
from app.jenkins_config import JENKINS_URL, REGION_MAP

def get_last_7_days(selected_date):
    last_7_days = [(selected_date - timedelta(days=i)) for i in range(0, 7)]
    return [str(d) for d in sorted(last_7_days)]

def init_trend_data(last_7_days_str):
    return {
        date_str: {"passed": 0, "failed": 0, "aborted": 0}
        for date_str in last_7_days_str
    }

def fetch_weekly_data(selected_date):
    if selected_date > datetime.now(timezone.utc).date():
        return None
    last_7_days_str = get_last_7_days(selected_date)
    trend_data = {}

    for region_key, meta in REGION_MAP.items():
        trend_data[region_key] = init_trend_data(last_7_days_str)
        view_path = f"view/{meta['view']}"

        for folder_list in meta["folders"]:
            folder_path = "/".join([f"job/{f}" for f in folder_list])
            api_url = f"{JENKINS_URL}/{view_path}/{folder_path}/api/json"
            response = requests.get(api_url, auth=auth)
            if response.status_code != 200:
                continue
            jobs = response.json().get("jobs", [])

            for job in jobs:
                if job['color'] in ["notbuilt", "grey", "disabled"]:
                    continue
                job_url = job["url"]

                for date_str in last_7_days_str:
                    latest_build_info = get_latest_build_on_date(job_url, date_str)
                    if latest_build_info:
                        result = latest_build_info.get("result")
                        if not result:
                            continue
                        if result == "SUCCESS":
                            trend_data[region_key][date_str]["passed"] += 1
                        elif result == "FAILURE":
                            trend_data[region_key][date_str]["failed"] += 1
                        elif result == "ABORTED":
                            trend_data[region_key][date_str]["aborted"] += 1

    return {
        "trend_data": {
            region: {
                date: trend_data[region][date]
                for date in sorted(trend_data[region])
            } for region in trend_data
        }
    }