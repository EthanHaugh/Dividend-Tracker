import { LineChart } from "@mui/x-charts/LineChart";
import { useGetYearlyDividends } from "../../hooks/api.hooks";
import { CircularProgress } from "@mui/material";

const AXIS_COLOUR = "rgba(255,255,255,0.5)"


const DividendsLineChart = () => {
  const { data, isLoading } = useGetYearlyDividends();

  const years = data?.map((item) => item.year.toString()) ?? [];
  const dataPoints = data?.map((item) => item.total_dividends) ?? [];

  if (isLoading || !data || data.length === 0) {
    return <CircularProgress size={48} />;
  }

  return (
    <LineChart
      key={years.join(",")}
      xAxis={[{
        data: years,
        label: "Year",
        scaleType: "point",
        disableLine: true,
        disableTicks: true,
        tickLabelStyle: { fill: AXIS_COLOUR },
        labelStyle: { fill: AXIS_COLOUR },
      }]}
      yAxis={[{
        label: "Dividends (£)",
        tickLabelStyle: { fill: AXIS_COLOUR },
        labelStyle: { fill: AXIS_COLOUR },
      }]}
      series={[{
        data: dataPoints,
        label: "Total Dividends",
        valueFormatter: (value) => `£${Number(value).toFixed(2)}`,
      }]}
      width={600}
      height={450}
      hideLegend
    />
  );
};

export default DividendsLineChart;