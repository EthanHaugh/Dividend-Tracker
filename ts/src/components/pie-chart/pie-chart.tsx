import { PieChart } from "@mui/x-charts/PieChart";
import { useGetPieChartData } from "../../hooks/api.hooks";
import { CircularProgress, Typography } from "@mui/material";
import { PieValueType } from "@mui/x-charts";
import { Empty } from "antd";

function generateColorPalette(count: number): string[] {
  const colors: string[] = [];
  const baseHue = 270; // TODO: Get someone who isn't colour blind to check lol

  for (let i = 0; i < count; i++) {
    // Vary saturation and lightness to get different shades 
    const saturation = 70 + (i % 2) * 100; // 70%, 80%, 90%
    const lightness = 40 + Math.floor(i / 2) * 2; // 40%, 48%, 56%, etc.
    colors.push(`hsl(${baseHue}, ${saturation}%, ${lightness}%)`);
  }

  return colors;
}

export function DonutChart() {
  const { data, isLoading } = useGetPieChartData();

  const colors = generateColorPalette(data?.data.length || 0);

  // Needed since MUI Charts requires a PieValueType
  const percentageMap = Object.fromEntries(
    data?.data.map((item) => [item.ticker, item.percentage]) ?? []
  );

  const seriesData: PieValueType[] = data?.data.map((item, index) => ({
    id: item.ticker,
    value: item.total_payment,
    label: item.name,
    color: colors[index],
  })) ?? [];

  return (
    isLoading ? (
      <CircularProgress size={48} />
    ) : !isLoading && data?.data.length === 0 ? <Empty /> : (
      <>
        <Typography
          variant="subtitle1"
          align="center"
          gutterBottom
          sx={{ fontWeight: 600, letterSpacing: "0.05em" }}
        >
          Total Dividends by Ticker
        </Typography>
        <PieChart
          series={[
            {
              data: seriesData,
              innerRadius: "50%",
              outerRadius: "90%",
              highlightScope: { fade: "global", highlight: "item" },
              faded: { additionalRadius: -4, color: "gray" },
              valueFormatter: (item) => {
                const percentage = percentageMap[item.id as string] ?? 0;
                return `£${Number(item.value).toFixed(2)} (${percentage.toFixed(2)}%)`;
              },
            },
          ]}
          width={500}
          height={500}
          hideLegend
        />
      </>
    )
  );
}

export default DonutChart;