// Donut-Chart
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

// Chart.JS
if (servicesData) {
  servicesList.forEach((service) => {
    if (servicesData[service]) {
      createDonutChart(
        `chart-${service}`,
        servicesData[service].passed,
        servicesData[service].failed,
        servicesData[service].aborted
      );
    }
  });
}


function goToService(regionName, serviceName, selected_date) {
    // Redirect to the service-specific route
    window.location.href = `/dashboard/${regionName}/${serviceName}/${selected_date}`;
}


