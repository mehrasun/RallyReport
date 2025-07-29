from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict
import requests
from app.utils import auth, time_ago, utc_timezone, get_build_date, get_latest_build_on_date, fetch_latest_build
from app.jenkins_config import JENKINS_URL, REGION_MAP

def get_last_7_days(selected_date):
    last_7_days = [(selected_date - timedelta(days=i)) for i in range(0, 7)]
    return [str(d) for d in sorted(last_7_days)]

def init_trend_data(last_7_days_str):
    return {
        date_str: {"passed": 0, "failed": 0, "aborted": 0}
        for date_str in last_7_days_str
    }

def fetch_jenkins_data(selected_date):
    if selected_date > datetime.now(timezone.utc).date():
        return None
    last_7_days_str = get_last_7_days(selected_date)
    total_summary = {"passed": 0, "failed": 0, "aborted": 0, "total": 0}
    region_summary = {}
    recent_activity = []
    failure_counter = Counter()
    scenario_region_map = defaultdict(set)
    trend_data = {}

    for region_key, meta in REGION_MAP.items():
        trend_data[region_key] = init_trend_data(last_7_days_str)
        summary = {"passed": 0, "failed": 0, "aborted": 0, "total": 0}
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
                job_name = job["name"]
                job_url = job["url"]
                if selected_date == datetime.now(timezone.utc).date():
                    latest_build_status = fetch_latest_build(job_url, selected_date)
                    if latest_build_status:
                        latest_build = latest_build_status
                    else:
                        latest_build = get_latest_build_on_date(job_url, selected_date)
                else:
                    latest_build = get_latest_build_on_date(job_url, selected_date)
                if latest_build:
                    timestamp = latest_build["timestamp"]
                    build_date = get_build_date(timestamp)
                    if latest_build:
                        result = latest_build.get("result")
                        if build_date == selected_date:
                            summary["total"] += 1
                            total_summary["total"] += 1
                        if result == "SUCCESS":
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

                # builds = fetch_builds(job_url, selected_date)

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
                            "report_view": f"{latest_build['url']}console",
                            "timestamp": timestamp
                        })

        region_summary[region_key] = summary

    recent_activity = sorted(recent_activity, key=lambda x: x["timestamp"], reverse=True)[:5]
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
        "trend_data": {
            region: {
                date: trend_data[region][date]
                for date in sorted(trend_data[region])
            } for region in trend_data
        },
        "top_failing_scenarios": top_failing_scenarios
    }