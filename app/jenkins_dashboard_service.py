from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict
import requests
from app.utils import auth, time_ago, utc_timezone, get_build_date, get_latest_build_on_date, fetch_latest_build
from app.jenkins_config import JENKINS_URL, REGION_MAP
import re

def fetch_jenkins_data():
    selected_date = datetime.now(timezone.utc).date()
    total_summary = {"passed": 0, "failed": 0, "aborted": 0, "inprogress": 0, "total": 0}
    region_summary = {}
    recent_activity = []
    failure_counter = Counter()
    scenario_region_map = defaultdict(set)
    for region_key, meta in REGION_MAP.items():
        summary = {"passed": 0, "failed": 0, "aborted": 0, "inprogress": 0, "total": 0}
        view_path = f"view/{meta['view']}"

        for folder_list in meta["folders"]:
            folder_path = "/".join([f"job/{f}" for f in folder_list])
            api_url = f"{JENKINS_URL}/{view_path}/{folder_path}/api/json?tree=jobs[name,url,color]"
            response = requests.get(api_url, auth=auth)
            if response.status_code != 200:
                continue
            jobs = response.json().get("jobs", [])

            for job in jobs:
                if job['color'] in ["notbuilt", "grey", "disabled"]:
                    continue
                job_name = job["name"]
                job_url = job["url"]
                latest_build = fetch_latest_build(job_url, selected_date)
                if latest_build:
                    timestamp = latest_build["timestamp"]
                    build_date = get_build_date(timestamp)
                    result = latest_build.get("result")
                    is_building = latest_build.get("building", False)
                    if build_date == selected_date:
                        summary["total"] += 1
                        total_summary["total"] += 1
                    if is_building:
                        summary["inprogress"] += 1
                        total_summary["inprogress"] += 1
                    elif result == "SUCCESS":
                        summary["passed"] += 1
                        total_summary["passed"] += 1
                    elif result == "FAILURE":
                        summary["failed"] += 1
                        total_summary["failed"] += 1
                        failure_counter[job_name] += 1
                        scenario_region_map[job_name].add(region_key)
                    elif result == "ABORTED":
                        summary["aborted"] += 1
                        total_summary["aborted"] += 1
                if latest_build:
                    result = latest_build.get("result")
                    timestamp = latest_build.get("timestamp")

                    if not result or not timestamp:
                        continue
                    build_date = get_build_date(timestamp)
                    dt_obj = datetime.fromtimestamp(timestamp / 1000, tz=utc_timezone)
                # Recent activity (top 5 latest by timestamp)
                    if build_date == selected_date:
                        recent_activity.append({
                            "job_name": job_name,
                            "result": result,
                            "build_url": latest_build["url"],
                            "build_number": latest_build["url"].rstrip("/").split("/")[-1],
                            "time": time_ago(dt_obj, utc_timezone),
                            "region": region_key,
                            "report_view": f"{latest_build['url']}consoleText",
                            "timestamp": timestamp
                        })
        region_summary[region_key] = summary
    recent_activity = sorted(recent_activity, key=lambda x: x["timestamp"], reverse=True)[:5]
    for recent_activity_job in recent_activity:
        console_url = recent_activity_job.get("report_view")
        response = requests.get(console_url, auth=auth)
        if response.status_code == 200:
            console_output = response.text

            html_pattern = r"Generated HTML Report - (http[^\s]+)"
            report_match = re.search(html_pattern, console_output)
            if report_match:
                recent_activity_job['report_view'] = report_match.group(1)
            else:
                recent_activity_job['report_view'] = "Not Found"
        else:
            recent_activity_job['report_view'] = "Not Found"
    top_failing_scenarios = [
        {
            "job_name": name,
            "failures": count,
            "regions": sorted(list(scenario_region_map[name]))
        }
        for name, count in failure_counter.most_common(10)
    ]

    return {
        "latest_status_summary": total_summary,
        "region_summary": region_summary,
        "recent_activity": recent_activity,
        "top_failing_scenarios": top_failing_scenarios
    }