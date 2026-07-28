import { useEffect, useState } from "react";
import {
  AccountCashResponse,
  DividendProjectionsResponse,
  ListAvailableTickersResponse,
  ListCompanyDividendsResponse,
  ListDividendsResponse,
  MonthlyDividendsComparisonResponse,
  PieChartResponse,
  YearlyDividendsResponse,
} from "../models/models";
import { BASE_URL } from "./consts";

let _invalidateId = 0;
const _invalidateListeners = new Set<(id: number) => void>();

export function invalidateApi() {
  _invalidateId++;
  _invalidateListeners.forEach((l) => l(_invalidateId));
}
/*
  Used to invalidate current API responses
*/
export function useInvalidationToken() {
  const [token, setToken] = useState<number>(_invalidateId);
  useEffect(() => {
    const listener = (id: number) => setToken(id);
    _invalidateListeners.add(listener);
    return () => {
      _invalidateListeners.delete(listener);
    };
  }, []);
  return token;
}

// Generic fetch hook for GET requests
function useFetch<T>(url: string, dependencies: unknown[] = []) {
  const invalidateToken = useInvalidationToken();
  const [data, setData] = useState<T | null>(null);
  const [statusCode, setStatusCode] = useState<number>();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setIsLoading(true);
    fetch(url)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        if (response.status) {
          setStatusCode(response.status)
        }
        return response.json();
      })
      .then((result) => {
        setData(result);
        setError(null);
      })
      .catch((err) => {
        setError(err as Error);
        setData(null);
      })
      .finally(() => setIsLoading(false));
  }, [url, invalidateToken, ...dependencies]);

  return { data, isLoading, error, statusCode };
}

// Generic mutation hook for POST/GET mutations
function useMutation<T>(onSuccess?: (data?: T) => void) {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const mutate = async (url: string): Promise<T | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = (await response.json()) as T;
      setData(result);
      setError(null);
      if (onSuccess) {
        onSuccess()
      }
      return result;
    } catch (err) {
      setError(err as Error);
      setData(null);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { mutate, data, isLoading, error };
}

export function useGetTotalDividends() {
  return useFetch<{ total_dividends: number }>(`${BASE_URL}/total-dividends`, []);
}

export function useGetPreviousYearDividends() {
  const year = new Date().getFullYear() - 1;
  const { data: fullData, ...rest } = useFetch<YearlyDividendsResponse[]>(
    `${BASE_URL}/yearly-dividends?year=${year}`
  );

  return {
    data: fullData ? fullData[0] : null,
    ...rest,
  };
}

export function useGetYearlyDividends() {
  return useFetch<YearlyDividendsResponse[]>(`${BASE_URL}/yearly-dividends`);
}

export function useGetAccountCash() {
  return useFetch<AccountCashResponse>(`${BASE_URL}/account-cash`);
}

export function useGetPieChartData() {
  return useFetch<PieChartResponse>(`${BASE_URL}/pie-chart`);
}

export function useListCompanyTotals(
  page: number,
  pageSize: number,
  search: string,
  filters: string[],
  sortBy?: string,
  sortDirection?: string,
) {
  const url = `${BASE_URL}/list-company-totals?page=${page}&page_size=${pageSize}&search=${search}&filters=${filters}${sortBy ? `&sort_by=${sortBy}` : ''}${sortDirection ? `&sort_direction=${sortDirection}` : ''}`;
  return useFetch<ListDividendsResponse>(url, [page, pageSize, search, filters, sortBy, sortDirection]);
}

export function useListCompanyDividends(
  page: number,
  pageSize: number,
  ticker: string,
) {
  const url = `${BASE_URL}/list-company-dividends?page=${page}&page_size=${pageSize}&ticker=${ticker}`;
  return useFetch<ListCompanyDividendsResponse>(url, [page, pageSize, ticker]);
}

export function useUpdateCurrentYearDividends(onSuccess?: () => void) {
  const { mutate: baseMutate, ...rest } = useMutation<ListCompanyDividendsResponse>(onSuccess);

  const mutate = async (year?: number) => {
    const url = `${BASE_URL}/download?year=${year || new Date().getFullYear()}`;
    return baseMutate(url);
  };

  return { mutate, ...rest };
}

export function useListAvailableTickers() {
  const { data: fullData, ...rest } = useFetch<ListAvailableTickersResponse>(
    `${BASE_URL}/list-available-tickers`
  );

  return {
    data: fullData?.data || null,
    ...rest,
  };
}

export function useHealthCheck() {
  const { data: fullData, ...rest } = useFetch<{ data: string[] }>(
    `${BASE_URL}/health`
  );

  return {
    data: fullData?.data || null,
    ...rest,
  };
}

export function useGetDividendProjections(years: number | null, reinvest: boolean | null, contributions: number | null) {
  const { data: fullData, ...rest } = useFetch<{ data: DividendProjectionsResponse }>(
    `${BASE_URL}/dividend-projection?years=${years}&reinvest=${reinvest}&annual_contributions=${contributions}`
  );

  return {
    data: fullData?.data || null,
    ...rest,
  };
}

export function useGetMonthlyDividendsComparison() {
  return useFetch<MonthlyDividendsComparisonResponse>(`${BASE_URL}/monthly-dividends-comparison`);
}