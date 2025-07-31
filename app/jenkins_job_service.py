import requests
import re
from app.jenkins_config import JENKINS_URL, REGION_MAP
from app.utils import auth, time_ago, fetch_latest_build, get_latest_build_on_date
from app.jenkins_dashboard_service import get_build_date
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_build_data(build_url):
    build_api_url = f"{build_url}api/json?tree=timestamp,result,building,url,number"
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



def get_filtered_jobs(selected_date, status_filter=None, region=None, max_workers=10):
    job_details = []
    today_utc = datetime.now(timezone.utc).date()
    region_values = {region: REGION_MAP.get(region)} if region else REGION_MAP

    def get_html_report(build_url):
        console_url = f"{build_url}consoleText"
        try:
            response = requests.get(console_url, auth=auth, timeout=5)
            if response.status_code == 200:
                match = re.search(r"Generated HTML Report - (http[^\s]+)", response.text)
                return match.group(1) if match else "Not Found"
        except:
            pass
        return "Not Found"

    for region_key, meta in region_values.items():
        view_path = f"view/{meta['view']}"
        for folder_list in meta["folders"]:
            folder_path = "/".join([f"job/{f}" for f in folder_list])
            api_url = f"{JENKINS_URL}/{view_path}/{folder_path}/api/json?tree=jobs[name,url]"
            res = requests.get(api_url, auth=auth)
            if res.status_code != 200:
                continue

            for job in res.json().get("jobs", []):
                if selected_date > today_utc:
                    return f"The date you selected is in the future: {selected_date}"

                latest_build = (
                    fetch_latest_build(job["url"], selected_date)
                    if selected_date == today_utc
                    else get_latest_build_on_date(job["url"], selected_date)
                )
                if not latest_build:
                    continue

                result = latest_build.get("result")
                timestamp = latest_build["timestamp"] // 1000
                build_datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)

                if status_filter and result != status_filter:
                    continue

                last_run_ago = time_ago(build_datetime, timezone.utc)

                # Parallelize fetching all builds on the selected date
                builds = fetch_builds(job["url"], selected_date)
                last_5 = []
                date_success = 0
                date_total = 0

                build_data_list = []

                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(fetch_build_data, b["url"]): b for b in builds}
                    for future in as_completed(futures):
                        b_data = future.result()
                        if not b_data:
                            continue
                        build_data_list.append(b_data)

                for b_data in build_data_list:
                    if len(last_5) < 5:
                        last_5.append(b_data.get("result", "N/A"))

                    b_ts = b_data["timestamp"] // 1000
                    b_date = datetime.fromtimestamp(b_ts, tz=timezone.utc).date()
                    if b_date == selected_date:
                        date_total += 1
                        if b_data.get("result") == "SUCCESS":
                            date_success += 1

                if date_total == 0:
                    continue

                # Fetch console output in parallel (if needed)
                html_report = "Not Found"
                if result:  # You can add more logic here
                    html_report = get_html_report(latest_build["url"])

                success_rate = round((date_success / date_total) * 100)

                job_details.append({
                    "job_name": job["name"],
                    "region": region_key,
                    "last_run": last_run_ago,
                    "latest_build_status": result,
                    "last_5": last_5,
                    "build_number": latest_build.get("number"),
                    "console_url": f"{latest_build['url']}console",
                    "report_url": html_report,
                    "success_rate": success_rate,
                })

    return job_details
