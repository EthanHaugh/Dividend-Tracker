import { useEffect, useState } from "react";
import {
  AccountCashResponse,
  ListAvaiableTickersResponse,
  ListCompanyDividendsResponse,
  ListDividendsResponse,
  PieChartResponse,
  YearlyDividendsResponse,
} from "../models/models";
import { BASE_URL } from "./consts";

// Simple invalidation utilities: incrementing token + subscriber set.
let _invalidateId = 0;
const _invalidateListeners = new Set<(id: number) => void>();

export function invalidateApi() {
  _invalidateId++;
  _invalidateListeners.forEach((l) => l(_invalidateId));
}

export function useInvalidationToken() {
  const [token, setToken] = useState<number>(_invalidateId);
  useEffect(() => {
    const listener = (id: number) => setToken(id);
    _invalidateListeners.add(listener);
    return () => {
      _invalidateListeners.delete(listener);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return token;
}

export function useGetTotalDividends() {
  const invalidateToken = useInvalidationToken();
  const [data, setData] = useState<number | undefined>(undefined);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | undefined>(undefined);

  useEffect(() => {
    setIsLoading(true);
    fetch(`${BASE_URL}/total-dividends`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((result) => {
        setData(result.total_dividends);
        setError(undefined);
      })
      .catch((err) => {
        setError(err);
        setData(undefined);
      })
      .finally(() => setIsLoading(false));
  }, [invalidateToken]);

  return { data, isLoading, error };
}

export function useGetPreviousYearDividends() {
  const invalidateToken = useInvalidationToken();
  const [data, setData] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const year = new Date().getFullYear() - 1;
    setIsLoading(true);
    fetch(`${BASE_URL}/yearly-dividends?year=${year}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((result) => {
        setData(result[0].total_dividends);
        setError(null);
      })
      .catch((err) => {
        setError(err);
        setData(null);
      })
      .finally(() => setIsLoading(false));
  }, [invalidateToken]);

  return { data, isLoading, error };
}

export function useGetYearlyDividends() {
  const invalidateToken = useInvalidationToken();
  const [data, setData] = useState<YearlyDividendsResponse[] | null>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setIsLoading(true);
    fetch(`${BASE_URL}/yearly-dividends`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((result) => {
        setData(result);
        setError(null);
      })
      .catch((err) => {
        setError(err);
        setData([]);
      })
      .finally(() => setIsLoading(false));
  }, [invalidateToken]);

  return { data, isLoading, error };
}

export function useGetAccountCash() {
  const invalidateToken = useInvalidationToken();
  const [data, setData] = useState<AccountCashResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setIsLoading(true);
    fetch(`${BASE_URL}/account-cash`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((result) => {
        setData(result);
        setError(null);
      })
      .catch((err) => {
        setError(err);
        setData(null);
      })
      .finally(() => setIsLoading(false));
  }, [invalidateToken]);

  return { data, isLoading, error };
}

export function useGetPieChartData() {
  const invalidateToken = useInvalidationToken();
  const [data, setData] = useState<PieChartResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setIsLoading(true);
    fetch(`${BASE_URL}/pie-chart`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((result) => {
        setData(result);
        setError(null);
      })
      .catch((err) => {
        setError(err);
        setData(null);
      })
      .finally(() => setIsLoading(false));
  }, [invalidateToken]);

  return { data, isLoading, error };
}

export function useListCompanyTotals(
  page: number,
  pageSize: number,
  search: string,
) {
  const invalidateToken = useInvalidationToken();
  const [data, setData] = useState<ListDividendsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setIsLoading(true);
    fetch(
      `${BASE_URL}/list-company-totals?page=${page}&page_size=${pageSize}&search=${search}`,
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((result) => {
        setData(result);
        setError(null);
      })
      .catch((err) => {
        setError(err);
        setData(null);
      })
      .finally(() => setIsLoading(false));
  }, [page, pageSize, search, invalidateToken]);

  return { data, isLoading, error };
}

export function useListCompanyDividends(
  page: number,
  pageSize: number,
  ticker: string,
) {
  const invalidateToken = useInvalidationToken();
  const [data, setData] = useState<ListCompanyDividendsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setIsLoading(true);
    fetch(
      `${BASE_URL}/list-company-dividends?page=${page}&page_size=${pageSize}&ticker=${ticker}`,
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((result) => {
        setData(result);
        setError(null);
      })
      .catch((err) => {
        setError(err);
        setData(null);
      })
      .finally(() => setIsLoading(false));
  }, [page, pageSize, ticker, invalidateToken]);

  return { data, isLoading, error };
}

export function useUpdateCurrentYearDividends() {
  const [data, setData] = useState<ListCompanyDividendsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  // Expose a mutate function so callers can trigger the download on demand.
  const mutate = async (
    year?: number,
  ): Promise<ListCompanyDividendsResponse | null> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${BASE_URL}/download?year=${year || new Date().getFullYear()}`,
      );
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = (await response.json()) as ListCompanyDividendsResponse;
      setData(result);
      setError(null);
      // Invalidate other hooks so they refetch their data
      invalidateApi();
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


export function useListAvailableTickers() {
  const [data, setData] = useState<string[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setIsLoading(true);
    fetch(
      `${BASE_URL}/list-available-tickers`,
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((result) => {
        setData(result.data);
        setError(null);
      })
      .catch((err) => {
        setError(err);
        setData(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  return { data, isLoading, error };
}
