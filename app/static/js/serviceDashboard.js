//// Donut-Chart
//const createDonutChart = (id, passed, failed, aborted) => {
//  const chart = new Chart(document.getElementById(id), {
//    type: "doughnut",
//    data: {
//      labels: ["Passed", "Failed", "Aborted"],
//      datasets: [
//        {
//          data: [passed, failed, aborted],
//          backgroundColor: ["#10b981", "#ef4444", "#f59e0b"],
//          borderWidth: 1,
//        },
//      ],
//    },
//    options: {
//      plugins: {
//        title: {
//          display: true,
//          text: id.replace("chart-", "").toUpperCase(),
//          font: { size: 18 },
//          color: isDarkTheme() ? "#f3f4f6" : "#1f2937",
//        },
//        legend: {
//          position: "bottom",
//          labels: {
//            color: isDarkTheme() ? "#f3f4f6" : "#1f2937",
//          },
//        },
//      },
//    },
//  });
//
//  donutCharts[id] = chart;
//};
//
//// Chart.JS
//if (servicesData) {
//  servicesList.forEach((service) => {
//    if (servicesData[service]) {
//      createDonutChart(
//        `chart-${service}`,
//        servicesData[service].passed,
//        servicesData[service].failed,
//        servicesData[service].aborted
//      );
//    }
//  });
//}
//
//
//function goToService(regionName, serviceName, selected_date) {
//    // Redirect to the service-specific route
//    window.location.href = `/dashboard/${regionName}/${serviceName}/${selected_date}`;
//}
//
//


// Donut-Chart for Services
const createDonutChart = (id, passed, failed, aborted) => {
  const chart = new Chart(document.getElementById(id), {
    type: "doughnut",
    data: {
      labels: ["Passed", "Failed", "Aborted"],
      datasets: [
        {
          data: [passed, failed, aborted],
          backgroundColor: ["#10b981", "#ef4444", "#f59e0b"],
          borderWidth: 1,
        },
      ],
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: id.replace("chart-", "").toUpperCase(),
          font: { size: 18 },
          color: isDarkTheme() ? "#f3f4f6" : "#1f2937",
        },
        legend: {
          position: "bottom",
          labels: {
            color: isDarkTheme() ? "#f3f4f6" : "#1f2937",
          },
        },
      },
    },
  });

  donutCharts[id] = chart;
};

// Chart.JS for Services
if (servicesData) {
  servicesList.forEach((service) => {
    const chartId = `chart-${service}`;
    const canvas = document.getElementById(chartId);
    const serviceStats = servicesData[service];

    if (
      serviceStats &&
      (serviceStats.passed || serviceStats.failed || serviceStats.aborted)
    ) {
      createDonutChart(
        chartId,
        serviceStats.passed,
        serviceStats.failed,
        serviceStats.aborted
      );
    } else if (canvas) {
      // Draw fallback message on canvas
      const ctx = canvas.getContext("2d");

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw fallback text
      ctx.font = "bold 20px sans-serif";  // larger and bold
      ctx.fillStyle = isDarkTheme() ? "#f3f4f6" : "#1f2937",
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(`No ${service} job run today`, canvas.width / 2, canvas.height / 2);
    }
  });
}

// Redirect to Service Details
function goToService(regionName, serviceName, selected_date) {
  window.location.href = `/dashboard/${regionName}/${serviceName}/${selected_date}`;
}
