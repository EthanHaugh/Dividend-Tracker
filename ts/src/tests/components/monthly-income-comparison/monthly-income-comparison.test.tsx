import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import userEvent from "@testing-library/user-event";

import { MonthlyIncomeComparisonChart } from "../../../components/monthly-income-comparison/monthly-income-comparison";
import { useGetMonthlyDividendsComparison } from "../../../hooks/api.hooks";

const lineChartSpy = vi.fn();

vi.mock("@mui/x-charts/LineChart", () => ({
    LineChart: (props: unknown) => {
        lineChartSpy(props);
        return <div data-testid="line-chart" />;
    },
}));

vi.mock("../../../hooks/api.hooks", () => ({
    useGetMonthlyDividendsComparison: vi.fn(),
}));

const mockedUseGetMonthlyDividendsComparison = vi.mocked(
    useGetMonthlyDividendsComparison,
);

const mockComparisonData = {
    available_years: [2023, 2024],
    selected_years: [2023, 2024],
    data: [
        {
            month: 1,
            month_label: "Jan",
            values: { "2023": 10, "2024": 20 },
        },
        {
            month: 2,
            month_label: "Feb",
            values: { "2023": 5, "2024": 7 },
        },
    ],
};

describe("MonthlyIncomeComparisonChart", () => {
    beforeEach(() => {
        lineChartSpy.mockClear();
        mockedUseGetMonthlyDividendsComparison.mockReturnValue({
            data: mockComparisonData,
            isLoading: false,
            error: null,
            statusCode: undefined,
        });
    });

    afterEach(() => {
        cleanup();
        vi.clearAllMocks();
    });

    test("renders chart with all years selected by default", async () => {
        render(<MonthlyIncomeComparisonChart />);

        await waitFor(() => {
            expect(screen.getByTestId("line-chart")).toBeDefined();
        });

        const lastCall = lineChartSpy.mock.calls.at(-1)?.[0] as {
            series: Array<{ label: string }>;
        };
        expect(lastCall.series).toHaveLength(2);
        expect(lastCall.series.map((series) => series.label)).toEqual(["2023", "2024"]);
    });

    test("year toggle hides selected year series", async () => {
        render(<MonthlyIncomeComparisonChart />);

        const selects = screen.getAllByRole("combobox");
        await userEvent.click(selects[0]);

        const yearOptions = await screen.findAllByTitle("2024");
        const yearOption = yearOptions.find((option) =>
            option.className.includes("ant-select-item-option"),
        );
        if (!yearOption) {
            throw new Error("Year option 2024 not found");
        }
        await userEvent.click(yearOption);

        await waitFor(() => {
            const lastCall = lineChartSpy.mock.calls.at(-1)?.[0] as {
                series: Array<{ label: string }>;
            };
            expect(lastCall.series).toHaveLength(1);
            expect(lastCall.series[0].label).toBe("2023");
        });
    });

    test("metric mode switch applies cumulative values", async () => {
        render(<MonthlyIncomeComparisonChart />);

        const selects = screen.getAllByRole("combobox");
        await userEvent.click(selects[1]);

        const cumulativeOptions = await screen.findAllByTitle("Cumulative YTD");
        const cumulativeOption = cumulativeOptions.find((option) =>
            option.className.includes("ant-select-item-option"),
        );
        if (!cumulativeOption) {
            throw new Error("Cumulative YTD option not found");
        }
        await userEvent.click(cumulativeOption);

        await waitFor(() => {
            const lastCall = lineChartSpy.mock.calls.at(-1)?.[0] as {
                series: Array<{ data: number[]; label: string }>;
            };

            const series2023 = lastCall.series.find((series) => series.label === "2023");
            expect(series2023?.data).toEqual([10, 15]);
        });
    });

    test("shows empty state when there is no monthly data", () => {
        mockedUseGetMonthlyDividendsComparison.mockReturnValue({
            data: {
                available_years: [],
                selected_years: [],
                data: [],
            },
            isLoading: false,
            error: null,
            statusCode: undefined,
        });

        render(<MonthlyIncomeComparisonChart />);

        expect(
            screen.getByText("No monthly dividend history available yet"),
        ).toBeDefined();
    });
});
