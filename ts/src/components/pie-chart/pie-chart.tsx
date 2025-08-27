import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Title } from "chart.js";
import { useGetPieChartData } from "../../hooks/api.hooks";
import styles from "./pie-chart.module.css";
import { Flex, Spin } from "antd";

// Register chart components
ChartJS.register(ArcElement, Tooltip, Title);

export function DonutChart() {
  const { data, isLoading } = useGetPieChartData();
  const labels = data?.data.map((item) => item.ticker);
  const values = data?.data.map((item) => item.total_payment);

  const chartData = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: [
          "#e60000", // vivid red
          "#ff1a1a", // bright red with a hint of pink
          "#990000", // strong deep red
          "#4d0000", // darkest red, close to black but still visibly red
        ],
        hoverOffset: 20,
      },
    ],
  };

  const options = {
    responsive: true,
    layout: {
      padding: 8,
    },
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: "Total Dividends by Ticker",
      },
    },
  };

  return (
    <Flex
      align="center"
      gap="middle"
      style={{ width: "500px", height: "500px" }}
      justify="center"
    >
      {isLoading ? (
        <Spin size="large" />
      ) : (
        <Doughnut data={chartData} options={options} className={styles.chart} />
      )}
    </Flex>
  );
}

export default DonutChart;
