import requests
import re
from app.jenkins_config import JENKINS_URL, REGION_MAP
from app.utils import auth, time_ago, fetch_latest_build, get_latest_build_on_date
from app.jenkins_dashboard_service import get_build_date
from datetime import datetime, timezone

def fetch_build_data(build_url):
    build_api_url = f"{build_url}api/json"
    response = requests.get(build_api_url, auth=auth)
    if response.status_code != 200:
        return None
    return response.json()

def fetch_builds(job_url, selected_date):
    """
    Fetch all completed builds for a specific job URL on the given date.
    Returns a list of build JSON objects.
    """
    selected_builds = []
    job_api_url = f"{job_url}api/json?tree=builds[number,url]"

    try:
        response = requests.get(job_api_url, auth=auth)
        if response.status_code != 200:
            print(f"Error fetching job info from {job_api_url}")
            return []

        all_builds = response.json().get("builds", [])

        for build in all_builds:
            build_data = fetch_build_data(build["url"])
            if not build_data or build_data.get("building"):
                continue

            build_date = get_build_date(build_data["timestamp"])

            if build_date == selected_date:
                selected_builds.append(build_data)

            # Stop early if older builds are found
            elif build_date < selected_date:
                break

        if len(selected_builds) >= 5:
            return selected_builds

        for build in all_builds:
            if len(selected_builds) >= 5:
                break

            build_data = fetch_build_data(build["url"])
            if not build_data or build_data.get("building"):
                continue

            build_date = get_build_date(build_data["timestamp"])

            if build_date < selected_date and build_data not in selected_builds:
                selected_builds.append(build_data)

        return selected_builds

    except Exception as e:
        print(f"Error in fetch_builds(): {e}")
        return []


def get_services_specific_jobs(selected_date, view, folders):
    """
    Get jobs across all regions filtered by status for today.
    - status_filter: "SUCCESS", "FAILURE", "ABORTED", or None for all
    """
    job_details = []
    today_utc = datetime.now(timezone.utc).date()
    view_path = f"view/{view}"
    folder_path = "/".join([f"job/{f}" for f in folders])
    api_url = f"{JENKINS_URL}/{view_path}/{folder_path}/api/json"
    response = requests.get(api_url, auth=auth)
    if response.status_code != 200:
        return None

    jobs = response.json().get("jobs", [])
    for job in jobs:
        if selected_date == today_utc:
            latest_build = fetch_latest_build(job["url"], selected_date)
        elif selected_date < today_utc:
            latest_build = get_latest_build_on_date(job["url"], selected_date)
        else:
            return f"The date you have selected is a future data {selected_date}"
        if not latest_build:
            continue

        console_url = f"{latest_build['url']}consoleText"
        response = requests.get(console_url, auth=auth)
        if response.status_code == 200:
            console_output = response.text

            html_pattern = r"Generated HTML Report - (http[^\s]+)"
            report_match = re.search(html_pattern, console_output)
            if report_match:
                html_report = report_match.group(1)
            else:
                html_report = "Not Found"
        else:
            html_report = "Not Found"

        result = latest_build.get("result")
        timestamp = latest_build["timestamp"] // 1000
        build_datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)

        if build_datetime.date() != selected_date:
            continue

        last_run_ago = time_ago(build_datetime, timezone.utc)

        # ✅ Process all builds to calculate success rate
        builds = fetch_builds(job["url"], selected_date)
        last_5 = []
        date_success = 0
        date_total = 0

        for b in builds:
            b_data = fetch_build_data(b["url"])
            if not b_data:
                continue

            # Collect for last_5 status display
            if len(last_5) < 5:
                last_5.append(b_data.get("result", "N/A"))

            # Count today's builds
            b_ts = b_data["timestamp"] // 1000
            b_date = datetime.fromtimestamp(b_ts, tz=timezone.utc).date()
            if b_date == selected_date:
                date_total += 1
                if b_data.get("result") == "SUCCESS":
                    date_success += 1

        # ✅ Skip job if no builds ran today
        if date_total == 0:
            continue

        # ✅ Calculate success rate
        success_rate = round((date_success / date_total) * 100)

        job_details.append({
            "job_name": job["name"],
            "last_run": last_run_ago,
            "latest_build_status": result,
            "last_5": last_5,
            "build_number": latest_build.get("number"),
            "console_url": f"{latest_build['url']}console",
            "report_url": html_report,
            "success_rate": success_rate
        })

    return job_details
