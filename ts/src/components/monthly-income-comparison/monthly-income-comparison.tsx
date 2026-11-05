import { useEffect, useMemo, useState } from "react";
import { Col, Empty, Row, Select, Switch, Tooltip, Typography } from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";
import { CircularProgress } from "@mui/material";
import { LineChart, LineSeries } from "@mui/x-charts/LineChart";

import { useGetMonthlyDividendsComparison } from "../../hooks/api.hooks";
import styles from "./monthly-income-comparison.module.css";
import { removeMonthlyOutliers } from "./outlier-removal";

const AXIS_COLOUR = "rgba(255,255,255,0.5)";

type MetricMode = "monthly" | "cumulative";

const METRIC_OPTIONS: { label: string; value: MetricMode }[] = [
    { label: "Monthly Income", value: "monthly" },
    { label: "Cumulative YTD", value: "cumulative" },
];

export function MonthlyIncomeComparisonChart() {
    const { data, isLoading } = useGetMonthlyDividendsComparison();
    const [selectedYears, setSelectedYears] = useState<number[]>([]);
    const [metricMode, setMetricMode] = useState<MetricMode>("monthly");
    const [removeOutliers, setRemoveOutliers] = useState<boolean>(true);

    const availableYears = useMemo(() => data?.available_years ?? [], [data?.available_years]);

    useEffect(() => {
        if (availableYears.length === 0) {
            setSelectedYears([]);
            return;
        }

        setSelectedYears((currentYears) => {
            if (currentYears.length === 0) {
                return [...availableYears];
            }

            const filteredYears = currentYears.filter((year) =>
                availableYears.includes(year),
            );
            return filteredYears.length > 0 ? filteredYears : [...availableYears];
        });
    }, [availableYears]);

    const months = useMemo(() => data?.data ?? [], [data?.data]);

    const series = useMemo((): LineSeries[] => {
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth() + 1;
        const monthlyValues = selectedYears.map((year) =>
            months.map((monthPoint) =>
                year > currentYear || (year === currentYear && monthPoint.month > currentMonth)
                    ? null
                    : monthPoint.values[String(year)] ?? 0,
            ),
        );
        const filteredMonthlyValues = removeOutliers ? removeMonthlyOutliers(monthlyValues) : monthlyValues;

        return selectedYears.map((year, seriesIndex): LineSeries => {
            let cumulativeTotal = 0;
            const points = filteredMonthlyValues[seriesIndex].map((monthlyValue, monthIndex) => {
                const month = months[monthIndex].month;
                if (year > currentYear || (year === currentYear && month > currentMonth)) {
                    return null;
                }

                if (monthlyValue === null) {
                    return metricMode === "monthly" ? null : Number(cumulativeTotal.toFixed(2));
                }

                if (metricMode === "cumulative") {
                    cumulativeTotal += monthlyValue;
                    return Number(cumulativeTotal.toFixed(2));
                }
                return monthlyValue;
            });

            return {
                data: points,
                label: `${year}`,
                valueFormatter: (value: number | null) => `£${Number(value ?? 0).toFixed(2)}`,
                highlightScope: { fade: "global", highlight: "series" }
            };
        });
    }, [metricMode, months, selectedYears, removeOutliers]);

    if (isLoading) {
        return <CircularProgress size={48} />;
    }

    if (!data || availableYears.length === 0) {
        return <Empty description="No monthly dividend history available yet" />;
    }

    return (
        <>
            <Row justify="space-between" align="middle" className="mb-3">
                <Col span={8}>
                    <Typography.Text className={styles.controlLabel}>
                        Years to Compare
                    </Typography.Text>
                    <Select
                        mode="multiple"
                        value={selectedYears}
                        onChange={(values: number[]) =>
                            setSelectedYears([...values].sort((a, b) => a - b))
                        }
                        options={availableYears.map((year) => ({ label: `${year}`, value: year }))}
                        className={styles.controlInput}
                        placeholder="Select years"
                        allowClear={false}
                    />
                </Col>
                <Col span={7}>
                    <Row justify="center" align="middle">
                        <Typography.Title level={5} className={styles.title}>
                            Monthly Dividend Growth
                        </Typography.Title>
                        <Tooltip title="Compare how your monthly dividend income changes across years.">
                            <InfoCircleOutlined style={{ marginLeft: 8 }} />
                        </Tooltip>
                    </Row>
                </Col>
                <Col span={7}>
                    <Typography.Text className={styles.controlLabel}>Metric</Typography.Text>
                    <Select
                        value={metricMode}
                        onChange={(value: MetricMode) => setMetricMode(value)}
                        options={METRIC_OPTIONS}
                        className={styles.controlInput}
                    />
                </Col>
                <Col span={1}>
                    <Typography.Text className={styles.controlLabel}>Pull Outliers</Typography.Text>
                    <Switch
                        value={removeOutliers}
                        onChange={(value: boolean) => setRemoveOutliers(value)}
                        className={styles.controlInput}
                    />
                </Col>
            </Row>

            {selectedYears.length === 0 ? (
                <Row
                    justify="center"
                    align="middle"
                    style={{ height: 320, backgroundColor: "#02010a" }}
                >
                    <Empty description="Select at least one year to view monthly income" />
                </Row>
            ) : (
                <Row>
                    <LineChart
                        loading={isLoading}
                        sx={{ backgroundColor: "#02010a" }}
                        xAxis={[
                            {
                                data: months.map((monthPoint) => monthPoint.month_label),
                                label: "Month",
                                scaleType: "point",
                                disableLine: true,
                                disableTicks: true,
                                tickLabelStyle: { fill: AXIS_COLOUR },
                                labelStyle: { fill: AXIS_COLOUR },
                            },
                        ]}
                        yAxis={[
                            {
                                label: metricMode === "monthly" ? "Income (£)" : "Cumulative (£)",
                                tickLabelStyle: { fill: AXIS_COLOUR },
                                labelStyle: { fill: AXIS_COLOUR },
                            },
                        ]}
                        series={series}
                        slotProps={{
                            legend: {
                                sx: {
                                    fontSize: 14,
                                    color: AXIS_COLOUR,
                                },
                            },
                        }}
                        height={340}
                    />
                </Row>
            )}
        </>
    );
}
