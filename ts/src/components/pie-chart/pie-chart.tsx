import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Title } from "chart.js";
import { useGetPieChartData } from "../../hooks/api.hooks";
import styles from "./pie-chart.module.css";
import { Flex, Spin } from "antd";

ChartJS.register(ArcElement, Tooltip, Title);

function generateColorPalette(count: number): string[] {
  const colors: string[] = [];
  const baseHue = 270; // TODO: Get someone who isn't colour blind to check lol

  for (let i = 0; i < count; i++) {
    // Vary saturation and lightness to get different shades 
    const saturation = 70 + (i % 2) * 100; // 70%, 80%, 90%
    const lightness = 40 + Math.floor(i / 2) * 3; // 40%, 48%, 56%, etc.
    colors.push(`hsl(${baseHue}, ${saturation}%, ${lightness}%)`);
  }

  return colors;
}

export function DonutChart() {
  const { data, isLoading } = useGetPieChartData();
  const labels = data?.data.map((item) => item.name);
  const values = data?.data.map((item) => item.total_payment);
  const percentages = data?.data.map((item) => item.percentage);

  const chartData = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: generateColorPalette(labels?.length || 0),
        borderColor: "#1f2937",
        borderWidth: 2,
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
      tooltip: {
        callbacks: {
          label: function (context: any) {
            const value = context.parsed || 0;
            const percentage = percentages?.[context.dataIndex] || 0;

            return [
              `Amount: £${Number(value).toFixed(2)}`,
              `Percentage: ${percentage.toFixed(2)}%`
            ];
          }
        }
      }
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