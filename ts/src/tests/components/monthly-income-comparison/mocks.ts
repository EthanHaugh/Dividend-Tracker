export const mockNormalUseGetMonthlyDividendsComparison = {
    data: {
        available_years: [2022, 2023, 2024],
        selected_years: [2022, 2023, 2024],
        data: [
            { month: 1, month_label: "Jan", values: { "2022": 10, "2023": 11, "2024": 1000 } },
            { month: 2, month_label: "Feb", values: { "2022": 5, "2023": 6, "2024": 7 } },
        ],
    },
    isLoading: false,
    error: null,
    statusCode: undefined
}

export const mockFutureUseGetMonthlyDividendsCompariosn = {
    data: {
        available_years: [2025, 2026],
        selected_years: [2025, 2026],
        data: [
            { month: 5, month_label: "May", values: { "2025": 10, "2026": 20 } },
            { month: 6, month_label: "Jun", values: { "2025": 30, "2026": 40 } },
            { month: 7, month_label: "Jul", values: { "2025": 50, "2026": 60 } },
        ],
    },
    isLoading: false,
    error: null,
    statusCode: undefined,
}