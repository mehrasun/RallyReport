import requests
from datetime import datetime
import pytz  # Import the pytz library
from app.jenkins_config import JENKINS_URL
from app.utils import auth, time_ago, get_latest_build_on_date, fetch_latest_build

def get_daily_job_summary(jobs, selected_date):
    region_passed = 0
    region_failed = 0
    region_aborted = 0
    region_total = 0

    for job in jobs:
        job_url = job["url"]
        latest_build = fetch_latest_build(job_url, selected_date)
        today_statuses = list()
        if latest_build:
            result = latest_build.get("result")
            today_statuses.append(result)
        else:
            build_info = get_latest_build_on_date(job_url, selected_date)
            result = build_info.get("result")
            today_statuses.append(result)
        if today_statuses:
            region_total += len(today_statuses)
            region_passed += today_statuses.count("SUCCESS")
            region_failed += today_statuses.count("FAILURE")
            region_aborted += today_statuses.count("ABORTED")

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

    jobs_data_total = []
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
        jobs_data = []

        response = requests.get(api_url, auth=auth)
        if response.status_code != 200:
            return [], {}  # Return empty list and dict on error

        jobs = response.json().get("jobs", [])
        data_about_region_and_service = folders[0]
        service_name = data_about_region_and_service.split('-')[-1]

        # Fetch the daily job summary for this region using Jenkins timezone
        scenarios_daily_summary = get_daily_job_summary(jobs, selected_date)
        # services[service_name]["summary"] = scenarios_daily_summary

        # Update total region summary
        for key in region_daily_summary:
            region_daily_summary[key] += scenarios_daily_summary.get(key, 0)
        for job in jobs:
            job_name = job["name"]
            job_url = job["url"]
            job_api_url = f"{job_url}api/json"

            job_response = requests.get(job_api_url, auth=auth)
            if job_response.status_code != 200:
                continue

            builds = job_response.json().get("builds", [])[:5]
            last_5_status = []
            last_run_time = "N/A"
            console_url = ""
            build_number = None
            latest_build_status = None  # Add variable for latest build status

            if builds:
                latest_build_url = f"{builds[0]['url']}api/json"
                latest_build_response = requests.get(latest_build_url, auth=auth)
                if latest_build_response.status_code == 200:
                    latest_build_data = latest_build_response.json()
                    latest_build_status = latest_build_data.get("result")
                    timestamp = latest_build_data.get("timestamp")
                    if timestamp:
                        # Make the last run time timezone-aware in UTC, then convert to Jenkins timezone
                        dt_obj_utc = datetime.fromtimestamp(timestamp / 1000, tz=pytz.utc)
                        last_run_time = time_ago(dt_obj_utc.astimezone(jenkins_tz), jenkins_tz)
                    console_url = f"{builds[0]['url']}console"
                    build_number = latest_build_data.get("number")

                for build in builds:
                    build_api_url = f"{build['url']}api/json"
                    build_response = requests.get(build_api_url, auth=auth)
                    if build_response.status_code == 200:
                        build_data = build_response.json()
                        last_5_status.append(build_data.get("result"))

            jobs_data.append({
                "name": job_name,
                "last_run": last_run_time,
                "last_5": last_5_status,
                "console_url": console_url,
                "build_number": build_number,
                "latest_build_status": latest_build_status,  # Include latest build status
                "report_url": f"{job_url}lastBuild/HTML_Report/index.html"  # adjust path if needed
            })

        services[service_name] = {
            "summary": scenarios_daily_summary,
            "jobs": jobs_data
        }
    return {
        "summary": region_daily_summary,
        "services": services
    }