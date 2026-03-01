import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title,
  TooltipItem,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { useGetYearlyDividends } from "../../hooks/api.hooks";
import { Spin } from "antd";

// Register necessary Chart.js components
ChartJS.register(
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title
);

const DividendsLineChart = () => {
  const { data, isLoading } = useGetYearlyDividends();

  const labels = data?.map((item) => item.year);
  const dataPoints = data?.map((item) => item.total_dividends);

  const chartData = {
    labels,
    datasets: [
      {
        label: "Total Dividends",
        data: dataPoints,
        fill: false,
        borderColor: "rgba(255, 99, 132, 1)", // pinkish red
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        tension: 0.3,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: "Dividends Over the Years",
      },
      legend: {
        display: false,
      },
      tooltip: {
        displayColors: false,
        callbacks: {
          label: function (context: TooltipItem<"line">) {
            const value = context.parsed.y;
            return `£ ${value.toFixed(2)}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: "Dividends ($)",
        },
      },
      x: {
        title: {
          display: true,
          text: "Year",
        },
      },
    },
  };

  return isLoading ? <Spin /> : <Line data={chartData} options={options} />;
};

export default DividendsLineChart;
