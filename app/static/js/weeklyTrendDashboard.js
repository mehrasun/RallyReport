// Trends chart
const createLineChart = (id, labels, passed, failed, aborted) => {
  const textColor = isDarkTheme() ? "#f3f4f6" : "#1f2937";

  const chart = new Chart(document.getElementById(id), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Passed",
          data: passed,
          borderColor: "#10b981",
          backgroundColor: "rgba(16, 185, 129, 0.2)",
          fill: true,
          tension: 0.4,
        },
        {
          label: "Failed",
          data: failed,
          borderColor: "#ef4444",
          backgroundColor: "rgba(239, 68, 68, 0.2)",
          fill: true,
          tension: 0.4,
        },
        {
          label: "Aborted",
          data: aborted,
          borderColor: "#f59e0b",
          backgroundColor: "rgba(245, 158, 11, 0.2)",
          fill: true,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: id.replace("trend-", "").toUpperCase(), // Region name
          font: { size: 18 },
          color: textColor,
        },
        legend: {
          position: "top",
          labels: {
            color: textColor,
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: textColor,
          },
          grid: {
            color: isDarkTheme() ? "#374151" : "#e5e7eb",
          },
        },
        y: {
          ticks: {
            color: textColor,
          },
          grid: {
            color: isDarkTheme() ? "#374151" : "#e5e7eb",
          },
        },
      },
    },
  });

  lineCharts[id] = chart;
};


// Weekly trend line charts
if (weeklyTrendData) {
  Object.entries(weeklyTrendData).forEach(([region, dailyData]) => {
  const dateKeys = Object.keys(dailyData);  // actual date keys like '2025-07-21'

  const labels = dateKeys.map(dateStr => {
    const [year, month, day] = dateStr.split("-").map(Number);
    const date = new Date(year, month - 1, day);
    return date.toLocaleDateString("en-US", { weekday: "short" });  // "Mon", "Tue", etc.
  });

  const passed = [];
  const failed = [];
  const aborted = [];

  dateKeys.forEach(date => {
    const value = dailyData[date];
    if (value) {
      passed.push(value.passed);
      failed.push(value.failed);
      aborted.push(value.aborted);
    } else {
      passed.push(0);
      failed.push(0);
      aborted.push(0);
    }
  });

  createLineChart(`trend-${region}`, labels, passed, failed, aborted);
});
}