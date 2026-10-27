import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { useListCompanyTotals } from "../../hooks/api.hooks";

describe("useListCompanyTotals", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({}),
    });
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    fetchMock.mockReset();
  });

  test("sends each filter as a separate query parameter", async () => {
    renderHook(() =>
      useListCompanyTotals(1, 10, "", ["AAPL_US_EQ", "ADM_US_EQ"]),
    );

    await waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());

    const requestUrl = String(fetchMock.mock.calls[0][0]);
    const params = new URL(requestUrl, "http://localhost").searchParams;

    expect(params.getAll("filters")).toEqual(["AAPL_US_EQ", "ADM_US_EQ"]);
    expect(requestUrl).not.toContain("AAPL_US_EQ,");
  });
});
