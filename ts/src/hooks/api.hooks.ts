import { useEffect, useState } from "react";
import {
  AccountCashResponse,
  ListDividendsResponse,
  PieChartResponse,
} from "../models/models";
import { BASE_URL } from "./consts";

export function useGetTotalDividends() {
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
  }, []);

  return { data, isLoading, error };
}

export function useGetPreviousYearDividends() {
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
  }, []);

  return { data, isLoading, error };
}

export function useGetAccountCash() {
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
  }, []);

  return { data, isLoading, error };
}

export function useGetPieChartData() {
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
  }, []);

  return { data, isLoading, error };
}

export function useListDividendPayments(page: number, pageSize: number) {
  const [data, setData] = useState<ListDividendsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setIsLoading(true);
    fetch(`${BASE_URL}/list-dividends?page=${page}&page_size=${pageSize}`)
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
  }, [page, pageSize]);

  return { data, isLoading, error };
}
