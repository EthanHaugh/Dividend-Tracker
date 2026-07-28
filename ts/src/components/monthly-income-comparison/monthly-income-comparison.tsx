import { useEffect, useMemo, useState } from "react";
import { Col, Empty, Row, Select, Tooltip, Typography } from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";
import { CircularProgress } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";

import { useGetMonthlyDividendsComparison } from "../../hooks/api.hooks";
import styles from "./monthly-income-comparison.module.css";

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

    const availableYears = data?.available_years ?? [];

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

    const months = data?.data ?? [];

    const series = useMemo(() => {
        return selectedYears.map((year) => {
            let cumulativeTotal = 0;
            const points = months.map((monthPoint) => {
                const monthlyValue = monthPoint.values[String(year)] ?? 0;
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
            };
        });
    }, [metricMode, months, selectedYears]);

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
                <Col span={8}>
                    <Typography.Text className={styles.controlLabel}>Metric</Typography.Text>
                    <Select
                        value={metricMode}
                        onChange={(value: MetricMode) => setMetricMode(value)}
                        options={METRIC_OPTIONS}
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
                        height={340}
                    />
                </Row>
            )}
        </>
    );
}
