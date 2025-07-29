from flask import Blueprint, render_template, request
from app.jenkins_dashboard_service import fetch_jenkins_data
from app.jenkins_region_service import fetch_region_jobs
from app.jenkins_config import REGION_MAP
from datetime import datetime, timezone
from app.jenkins_config import OS_SERVICE
from app.jenkins_job_service import get_filtered_jobs
from app.service_specific_job import get_services_specific_jobs

main = Blueprint("main", __name__)
regions_name = list(REGION_MAP.keys())

@main.route("/", methods=["GET"])
def dashboard():
    selected_date_str = request.args.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    print(regions_name)
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    jenkins_data = fetch_jenkins_data(selected_date)
    print(jenkins_data)
    if jenkins_data:
        return render_template(
            "dashboard.html",
            regions=regions_name,
            selected_date=selected_date,
            regional=jenkins_data["region_summary"],
            summary=jenkins_data["latest_status_summary"],
            trend_regional=jenkins_data["trend_data"],
            recent_activity=jenkins_data["recent_activity"],
            top_failing=jenkins_data["top_failing_scenarios"]
        )
    else:
        return render_template("tryagain.html", date=selected_date)

@main.route("/dashboard/<region>", methods=["GET"])
def regionDashboard(region):
    if region not in REGION_MAP:
        return "Invalid region", 404

    selected_date = datetime.now(timezone.utc).date()
    region_config = REGION_MAP[region]
    view = region_config.get("view")
    folder = region_config.get("folders")
    openstack_service = [f[0].split("-")[-1] for f in folder]
    openstack_service = ['Nova' if service == 'Compute' else service for service in openstack_service]
    region_jobs= fetch_region_jobs(folder, view, selected_date)
    daily_summary = region_jobs.get('summary')
    os_service_data = {}
    os_service_jobs_data = {}

    for service, data in region_jobs.get("services", {}).items():
        if service.lower() == "compute":
            service = "Nova"
        summary = data.get("summary", {})
        jobs = data.get("jobs", [])
        os_service_data[service] = {
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "aborted": summary.get("aborted", 0)
        }
        os_service_jobs_data[service] = jobs
    return render_template(
        "serviceDashboard.html",
        region_jobs=region_jobs,
        daily_summary=daily_summary,
        region_name=region.upper(),
        regions=regions_name,
        # regional=jenkins_data["region_summary"],
        os_service=openstack_service,
        os_service_data=os_service_data,
        selected_date=selected_date
    )

@main.route("/jobSummary/<jobType>", methods=["GET"])
def jobSummary(jobType):
    jobType = jobType.upper()
    selected_date_str = request.args.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    if jobType not in ["SUCCESS", "FAILURE", "ABORTED"]:
        return f"Invalid job type: {jobType}", 400
    jobs = get_filtered_jobs(selected_date, status_filter=jobType)
    return render_template("jobSummary.html", jobType=jobType, jobs=jobs, regions=regions_name)

@main.route("/dashboard/<region>/jobSummary/<jobType>", methods=["GET"])
def regionJobSummary(jobType, region):
    jobType = jobType.upper()
    selected_date_str = request.args.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    if jobType not in ["SUCCESS", "FAILURE", "ABORTED"]:
        return f"Invalid job type: {jobType}", 400
    jobs = get_filtered_jobs(selected_date, status_filter=jobType, region=region)
    return render_template("jobSummary.html", jobType=jobType, jobs=jobs, regions=regions_name)

@main.route("/dashboard/<region>/<service_name>/<selected_date>", methods=["GET"])
def service_jobs(region,service_name,selected_date):
    if region not in REGION_MAP:
        return "Invalid region", 404

    region_data = REGION_MAP.get(region)
    view = region_data.get("view")
    folders = region_data.get("folders", [])
    matched_folder = None

    for folder in folders:
        service_name_in_folder = folder[0]
        if service_name_in_folder.endswith(service_name):
            matched_folder = folder
            break

    if not matched_folder:
        return f"Service '{service_name}' not found in region '{region}'", 404

    selected_date_str = selected_date
    service_selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    region_jobs = get_services_specific_jobs(service_selected_date, view, matched_folder)
    return render_template("jobSummary.html", jobType=service_name, jobs=region_jobs, regions=regions_name)
