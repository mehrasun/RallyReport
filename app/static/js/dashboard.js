//// Chart.JS
//const createDonutChart = (id, passed, failed, aborted, inprogress) => {
//  const chart = new Chart(document.getElementById(id), {
//    type: "doughnut",
//    data: {
//      labels: ["Passed", "Failed", "Aborted", "InProgress"],
//      datasets: [
//        {
//          data: [passed, failed, aborted, inprogress],
//          backgroundColor: ["#10b981", "#ef4444", "#f59e0b", "#3b82f6"],
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
//          display: false,
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
//// Latest code it works great as well.
//if (regionalData) {
//  regions_name.forEach((region) => {
//    if (regionalData[region]) {
//      // Dynamically create a chart for each region
//      createDonutChart(
//        `chart-${region}`, // Use the region name to dynamically set the ID
//        regionalData[region].passed,
//        regionalData[region].failed,
//        regionalData[region].aborted,
//        regionalData[region].inprogress
//      );
//    }
//  });
//}




// Chart.JS
const createDonutChart = (id, passed, failed, aborted, inprogress) => {
  const chart = new Chart(document.getElementById(id), {
    type: "doughnut",
    data: {
      labels: ["Passed", "Failed", "Aborted", "InProgress"],
      datasets: [
        {
          data: [passed, failed, aborted, inprogress],
          backgroundColor: ["#10b981", "#ef4444", "#f59e0b", "#3b82f6"],
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
          display: false,
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

// Render charts or fallback message
if (regionalData) {
  regions_name.forEach((region) => {
    const chartId = `chart-${region}`;
    const canvas = document.getElementById(chartId);
    const regionStats = regionalData[region];

    if (
      regionStats &&
      (regionStats.passed || regionStats.failed || regionStats.aborted || regionStats.inprogress)
    ) {
      createDonutChart(
        chartId,
        regionStats.passed,
        regionStats.failed,
        regionStats.aborted,
        regionStats.inprogress
      );
    } else if (canvas) {
      // Draw fallback message on canvas
      const ctx = canvas.getContext("2d");

      // Clear any existing chart
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw fallback text
      ctx.font = "bold 20px sans-serif";  // larger and bold
      ctx.fillStyle = isDarkTheme() ? "#f3f4f6" : "#1f2937";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(`No ${region} job run today`, canvas.width / 2, canvas.height / 2);
    }
  });
}
