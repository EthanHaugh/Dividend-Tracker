// Modified z-scores above this threshold indicate unusually high values.
const MODIFIED_Z_SCORE_THRESHOLD = 3.5;
const MAD_NORMALIZATION_FACTOR = 0.6745;

function median(values: number[]): number {
    const sortedValues = [...values].sort((a, b) => a - b);
    const middleIndex = Math.floor(sortedValues.length / 2);

    return sortedValues.length % 2 === 0
        ? (sortedValues[middleIndex - 1] + sortedValues[middleIndex]) / 2
        : sortedValues[middleIndex];
}

// Compare the same month across years and replace high outliers with null.
export function removeMonthlyOutliers(
    monthlySeries: readonly (readonly (number | null)[])[],
): (number | null)[][] {
    // Work on copies so the monthly data remains unchanged
    const filteredSeries: (number | null)[][] = monthlySeries.map((series) => [...series]);
    const monthCount = Math.max(0, ...monthlySeries.map((series) => series.length));

    for (let monthIndex = 0; monthIndex < monthCount; monthIndex += 1) {
        // Compare values for this month across years, ignore missing or invalid values.
        const values = monthlySeries
            .map((series) => series[monthIndex])
            .filter((value): value is number => Number.isFinite(value));

        // Median and median absolute deviation are robust to unusually large values.
        const monthMedian = median(values);
        const deviations = values.map((value) => Math.abs(value - monthMedian));
        const medianAbsoluteDeviation = median(deviations);

        for (let seriesIndex = 0; seriesIndex < monthlySeries.length; seriesIndex += 1) {
            const value = monthlySeries[seriesIndex][monthIndex];
            if (typeof value !== "number" || !Number.isFinite(value)) {
                filteredSeries[seriesIndex][monthIndex] = null;
                continue;
            }

            // With zero spread, only values above the median are outliers.
            const isOutlier = medianAbsoluteDeviation === 0
                ? value > monthMedian
                // Otherwise, use a one-sided modified z-score to retain low values.
                : (MAD_NORMALIZATION_FACTOR * (value - monthMedian))
                    / medianAbsoluteDeviation > MODIFIED_Z_SCORE_THRESHOLD;

            if (isOutlier) {
                // Preserve the month slot so chart points remain aligned.
                filteredSeries[seriesIndex][monthIndex] = null;
            }
        }
    }

    return filteredSeries;
}
