import { useState } from "react";
import { Col, Empty, InputNumber, Row, Select, Tooltip, Typography } from "antd";
import { useGetDividendProjections } from "../../hooks/api.hooks";
import { LineChart } from "@mui/x-charts/LineChart";
import { CalendarOutlined, FullscreenExitOutlined, FullscreenOutlined, InfoCircleOutlined } from "@ant-design/icons";
import styles from './projection-chart.module.css'

const AXIS_COLOUR = "rgba(255,255,255,0.5)";
const PORTFOLIO_AXIS_ID = "portfolio-value-axis";

type SeriesKey = "dividends" | "contributions" | "portfolioValue";

const SERIES_OPTIONS: { label: string; value: SeriesKey }[] = [
    { label: "Dividends", value: "dividends" },
    { label: "Contributions", value: "contributions" },
    { label: "Portfolio Value", value: "portfolioValue" },
];

export function DividendProjectionsChart() {
    const [reinvest, setReinvest] = useState<boolean>(false)
    const [projectionYears, setProjectionYears] = useState<number | null>(10)
    const [yearlyContributions, setYearlyContributions] = useState<number | null>(1000)
    const [visibleSeries, setVisibleSeries] = useState<SeriesKey[]>([
        "dividends",
        "contributions",
    ]);

    const { data, isLoading } = useGetDividendProjections(projectionYears, reinvest, yearlyContributions);

    const onReinvestChange = (value: boolean) => {
        setReinvest(value)
    }
    const onProjectionYearsChange = (value: number | null) => {
        setProjectionYears(value)
    }
    const onYearlyContributionsChange = (value: number | null) => {
        setYearlyContributions(value)
    }

    const years = data?.years.map((item) => item.year.toString()) ?? [];
    const dividendDataPoints = data?.years.map((item) => item.annual_dividend) ?? [];
    const contributionDataPoints =
        data?.years.map(() => data.annual_contribution) ?? [];
    const portfolioValueDataPoints =
        data?.years.map((item) => item.portfolio_value) ?? [];

    const showPortfolioValue = visibleSeries.includes("portfolioValue");

    const allSeries = [
        {
            key: "dividends" as const,
            data: dividendDataPoints,
            label: "Total Dividends",
            valueFormatter: (value: number | null) => `£${Number(value).toFixed(2)}`,
        },
        {
            key: "contributions" as const,
            data: contributionDataPoints,
            label: "Annual Contribution",
            valueFormatter: (value: number | null) => `£${Number(value).toFixed(2)}`,
            color: "rgba(255,255,255,0.25)",
            showMark: false,
        },
        {
            key: "portfolioValue" as const,
            data: portfolioValueDataPoints,
            label: "Portfolio Value",
            valueFormatter: (value: number | null) => `£${Number(value).toFixed(2)}`,
            yAxisId: PORTFOLIO_AXIS_ID,
            color: "#5ac8fa",
        },
    ];

    const series = allSeries.filter((s) => visibleSeries.includes(s.key));

    return (
        <>
            <Row justify={'space-between'} className="mt-4">
                <Col span={8}>
                    <Row justify={'space-between'}>
                        <Col span={6} >
                            <Typography.Text className={styles.label}>Years to Predict</Typography.Text>
                            <InputNumber
                                variant="filled"
                                placeholder="Years"
                                onChange={onProjectionYearsChange}
                                value={projectionYears} min={1}
                                max={20}
                                prefix={<CalendarOutlined />}
                                className={styles.dataEntry}
                            />
                        </Col>
                        <Col span={6} >
                            <Typography.Text className={styles.label}>DRIP</Typography.Text>
                            <Select
                                variant="filled"
                                placeholder="Reinvest"
                                options={[{ value: true, label: 'True' },
                                { value: false, label: 'False' }]}
                                className={styles.dataEntry}
                                onChange={onReinvestChange}
                                value={reinvest}
                                prefix={reinvest ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
                            />
                        </Col>
                        <Col span={10} >
                            <Typography.Text className={styles.label}>Yearly Contributions</Typography.Text>
                            <InputNumber
                                prefix="£"
                                variant="filled"
                                placeholder="Contributions / Year"
                                onChange={onYearlyContributionsChange}
                                value={yearlyContributions}
                                min={0}
                                max={100000}
                                className={styles.dataEntry}
                            />
                        </Col>
                    </Row>
                </Col>
                <Col span={5}>
                    <Row justify="center" align="middle">
                        <Typography.Title level={5} className="mr-2 mb-0">
                            Dividend Yearly Projections
                        </Typography.Title>
                        <Tooltip title="Based on your previous dividend growth, contributions, and company dividend growth, heres what you might expect to see in the future">
                            <InfoCircleOutlined />
                        </Tooltip>
                    </Row>
                    <Row justify={"center"}>
                        <Typography.Text type="secondary">
                            Based from data over the last 12 Months
                        </Typography.Text>
                    </Row>
                </Col>
                <Col span={8}>
                    <Row justify="end">
                        <Select
                            mode="multiple"
                            value={visibleSeries}
                            onChange={(value: SeriesKey[]) => setVisibleSeries(value)}
                            options={SERIES_OPTIONS}
                            style={{ minWidth: 240 }}
                            placeholder="Select data to show"
                            allowClear={false}
                        />
                    </Row>
                </Col>
            </Row>
            {visibleSeries.length === 0 ? (
                <Row
                    justify="center"
                    align="middle"
                    style={{ height: 300, backgroundColor: "#02010a" }}
                >
                    <Empty description="Select dividends or contributions to see your projection" />
                </Row>
            ) : (
                <Row>
                    <LineChart
                        loading={isLoading}
                        sx={{
                            backgroundColor: "#02010a",
                        }}
                        xAxis={[
                            {
                                data: years,
                                label: "Year",
                                scaleType: "point",
                                disableLine: true,
                                disableTicks: true,
                                tickLabelStyle: { fill: AXIS_COLOUR },
                                labelStyle: { fill: AXIS_COLOUR },
                            },
                        ]}
                        yAxis={[
                            {
                                width: 50,
                                tickLabelStyle: { fill: AXIS_COLOUR },
                                labelStyle: { fill: AXIS_COLOUR },
                            },
                            ...(showPortfolioValue
                                ? [
                                    {
                                        id: PORTFOLIO_AXIS_ID,
                                        position: "right" as const,
                                        width: 70,
                                        tickLabelStyle: { fill: AXIS_COLOUR },
                                        labelStyle: { fill: AXIS_COLOUR },
                                    },
                                ]
                                : []),
                        ]}
                        series={series}
                        hideLegend
                        height={300}
                    />
                </Row>
            )}
        </>
    );
}