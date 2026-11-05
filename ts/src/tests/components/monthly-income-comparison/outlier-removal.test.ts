import { describe, expect, test } from "vitest";

import { removeMonthlyOutliers } from "../../../components/monthly-income-comparison/outlier-removal";

describe("removeMonthlyOutliers", () => {
    test("replaces a monthly outlier with null without shifting other months", () => {
        expect(removeMonthlyOutliers([
            [10, 5],
            [11, 6],
            [1000, 7],
        ])).toEqual([
            [10, 5],
            [11, 6],
            [null, 7],
        ]);
    });

    test("does not flag a month when fewer than three years are available", () => {
        expect(removeMonthlyOutliers([
            [10],
            [1000],
        ])).toEqual([
            [10],
            [1000],
        ]);
    });

    test("detects an outlier when the median absolute deviation is zero", () => {
        expect(removeMonthlyOutliers([
            [10],
            [10],
            [1000],
        ])).toEqual([
            [10],
            [10],
            [null],
        ]);
    });

    test("keeps low outliers while removing high outliers", () => {
        expect(removeMonthlyOutliers([
            [10],
            [11],
            [12],
            [1000],
        ])).toEqual([
            [10],
            [11],
            [12],
            [null],
        ]);
        expect(removeMonthlyOutliers([
            [10],
            [11],
            [12],
            [-1000],
        ])).toEqual([
            [10],
            [11],
            [12],
            [-1000],
        ]);
    });
    test("drop finite numbers", () => {
        expect(removeMonthlyOutliers([
            [10],
            [11],
            [NaN],
            [1000],
        ])).toEqual([
            [10],
            [11],
            [null],
            [null],
        ]);
    });
});
