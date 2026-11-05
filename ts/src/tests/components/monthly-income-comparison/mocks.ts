export const mockUseGetMonthlyDividendsComparison ={
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