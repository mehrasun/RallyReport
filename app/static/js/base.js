// Sidebar toggle
const sidebarToggle = document.querySelector("#sidebar-toggle");
sidebarToggle.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("collapsed");
});

// Theme toggle
document.querySelector(".theme-toggle").addEventListener("click", () => {
  toggleLocalStorage();
  toggleRootClass();
  updateChartsTheme(); // refresh chart colors
});

function toggleRootClass() {
  const current = document.documentElement.getAttribute("data-bs-theme");
  const inverted = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-bs-theme", inverted);
}

function toggleLocalStorage() {
  if (isLight()) {
    localStorage.removeItem("light");
  } else {
    localStorage.setItem("light", "set");
  }
}

function isLight() {
  return localStorage.getItem("light");
}

if (isLight()) {
  toggleRootClass();
}

function isDarkTheme() {
  return document.documentElement.getAttribute("data-bs-theme") === "dark";
}

// Store chart instances globally to update them later
const donutCharts = {};
const lineCharts = {};

// Chart.JS
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
//const createLineChart = (id, passed, failed, aborted) => {
//  const textColor = isDarkTheme() ? "#f3f4f6" : "#1f2937";
//  const chart = new Chart(document.getElementById(id), {
//    type: "line",
//    data: {
//      labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
//      datasets: [
//        {
//          label: "Passed",
//          data: [5, 7, 6, 4, 3, 5, 7],
//          borderColor: "#10b981",
//          backgroundColor: "rgba(16, 185, 129, 0.2)",
//          fill: true,
//          tension: 0.4,
//        },
//        {
//          label: "Failed",
//          data: [1, 0, 1, 2, 0, 1, 1],
//          borderColor: "#ef4444",
//          backgroundColor: "rgba(239, 68, 68, 0.2)",
//          fill: true,
//          tension: 0.4,
//        },
//        {
//          label: "Aborted",
//          data: [0, 1, 0, 1, 1, 0, 0],
//          borderColor: "#f59e0b",
//          backgroundColor: "rgba(245, 158, 11, 0.2)",
//          fill: true,
//          tension: 0.4,
//        },
//      ],
//    },
//    options: {
//      responsive: true,
//      plugins: {
//        title: {
//          display: true,
//          text: id.replace("trend-", "").toUpperCase(), // e.g., "DFW-DEV"
//          font: { size: 18 },
//          color: isDarkTheme() ? "#f3f4f6" : "#1f2937",
//        },
//        legend: {
//          position: "top",
//          labels: {
//            color: textColor,
//          },
//        },
//      },
//      scales: {
//        x: {
//          ticks: {
//            color: textColor,
//          },
//          grid: {
//            color: isDarkTheme() ? "#374151" : "#e5e7eb",
//          },
//        },
//        y: {
//          ticks: {
//            color: textColor,
//          },
//          grid: {
//            color: isDarkTheme() ? "#374151" : "#e5e7eb",
//          },
//        },
//      },
//    },
//  });
//
//  lineCharts[id] = chart;
//};

// Create charts using regionalData dynamically
// if (regionalData) {
//   if (regionalData.DFW) {
//     createDonutChart(
//       "chart-DFW-Dev",
//       regionalData.DFW.passed,
//       regionalData.DFW.failed,
//       regionalData.DFW.aborted
//     );
//   }
//   if (regionalData.SJC) {
//     createDonutChart(
//       "chart-SJC-Prod",
//       regionalData.SJC.passed,
//       regionalData.SJC.failed,
//       regionalData.SJC.aborted
//     );
//   }
//   if (regionalData.IAD) {
//     createDonutChart(
//       "chart-DFW-Prod",
//       regionalData.IAD.passed,
//       regionalData.IAD.failed,
//       regionalData.IAD.aborted
//     );
//   }
// }

// Latest code it works great as well.
//if (regionalData) {
//  regions_name.forEach((region) => {
//    if (regionalData[region]) {
//      // Dynamically create a chart for each region
//      createDonutChart(
//        `chart-${region}`, // Use the region name to dynamically set the ID
//        regionalData[region].passed,
//        regionalData[region].failed,
//        regionalData[region].aborted
//      );
//    }
//  });
//}
//
//createLineChart("trend-DFW", 10, 2, 1);
//createLineChart("trend-IAD", 8, 3, 1);
//createLineChart("trend-SJC", 9, 1, 0);
//createLineChart("trend-ORD", 7, 1, 0);

//// right now I am just using a constant
//const servicesData = {
//  Nova: { passed: 12, failed: 1, aborted: 0 },
//  Glance: { passed: 12, failed: 1, aborted: 0 },
//  Neutron: { passed: 9, failed: 3, aborted: 2 },
//  Octavia: { passed: 7, failed: 2, aborted: 1 },
//  Heat: { passed: 15, failed: 0, aborted: 1 },
//  Magnum: { passed: 15, failed: 0, aborted: 1 },
//  Barbican: { passed: 15, failed: 0, aborted: 1 },
//};

//// List of services
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

// Function to update all chart styles when theme changes
function updateChartsTheme() {
  const textColor = isDarkTheme() ? "#f3f4f6" : "#1f2937";
  const gridColor = isDarkTheme() ? "#374151" : "#e5e7eb";

  Object.values(donutCharts).forEach((chart) => {
    chart.options.plugins.title.color = textColor;
    chart.options.plugins.legend.labels.color = textColor;
    chart.update();
  });

  Object.values(lineCharts).forEach((chart) => {
    chart.options.plugins.title.color = textColor;
    chart.options.plugins.legend.labels.color = textColor;
     chart.options.scales.x.ticks.color = textColor;
     chart.options.scales.y.ticks.color = textColor;
     chart.options.scales.x.grid.color = gridColor;
     chart.options.scales.y.grid.color = gridColor;
    chart.update();
  });
}
