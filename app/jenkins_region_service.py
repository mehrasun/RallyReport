import requests
from datetime import datetime, timezone
import pytz  # Import the pytz library
from app.jenkins_config import JENKINS_URL
from app.utils import auth, time_ago, get_latest_build_on_date, fetch_latest_build

def get_daily_job_summary(jobs, selected_date):
    region_passed = 0
    region_failed = 0
    region_aborted = 0
    region_total = 0
    today_utc = datetime.now(timezone.utc).date()
    for job in jobs:
        if selected_date == today_utc:
            latest_build = fetch_latest_build(job["url"], selected_date)
        elif selected_date < today_utc:
            latest_build = get_latest_build_on_date(job["url"], selected_date)
        else:
            return f"The date you have selected is a future data {selected_date}"
        if not latest_build:
            continue
        result = latest_build.get("result")
        if result:
            region_total += 1
            if result == "SUCCESS":
                region_passed += 1
            elif result == "FAILURE":
                region_failed += 1
            elif result == "ABORTED":
                region_aborted += 1
    return {
        "passed": region_passed,
        "failed": region_failed,
        "aborted": region_aborted,
        "total": region_total
    }

def fetch_region_jobs(region_folders, region_view, selected_date):
    jenkins_tz = pytz.utc
    if jenkins_tz:
        print("Using UTC as default for time calculations.")
    region_daily_summary = {
        "passed": 0,
        "failed": 0,
        "aborted": 0,
        "total": 0
    }
    services = {}
    view_path = f"view/{region_view}"
    for folders in region_folders:
        folder_path = "/".join(f"job/{folder}" for folder in folders)
        api_url = f"{JENKINS_URL}/{view_path}/{folder_path}/api/json"
        response = requests.get(api_url, auth=auth)
        if response.status_code != 200:
            return [], {}

        jobs = response.json().get("jobs", [])
        data_about_region_and_service = folders[0]
        service_name = data_about_region_and_service.split('-')[-1]
        scenarios_daily_summary = get_daily_job_summary(jobs, selected_date)

        # Update total region summary
        for key in region_daily_summary:
            region_daily_summary[key] += scenarios_daily_summary.get(key, 0)
        services[service_name] = {
            "summary": scenarios_daily_summary
        }
    return {
        "summary": region_daily_summary,
        "services": services
    }