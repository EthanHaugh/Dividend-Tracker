export interface AccountCashResponse {
  id: number;
  account_value: number;
  estimated_deposits: number;
}

export interface PieChartResponse {
  data: {
    ticker: string;
    total_payment: number;
  }[];
}

export interface ListDividendsResponse {
  data: DividendPayment[];
  page: number;
  page_size: number;
  total_count: number;
}

export interface DividendPayment {
  ticker: string;
  total_payment: number;
}

export interface YearlyDividendsResponse {
  year: number;
  created_at: string;
  id: number;
  total_dividends: string;
}

export interface ListCompanyDividendsResponse {
  data: Dividend[];
  page: number;
  total_count: number;
  page_size: number;
}

export interface Dividend {
  created_at: string;
  dividend_id: number;
  number_of_shares: number;
  report_id: string;
  year: number;
  ticker: string;
  payment_date: string;
  amount: number;
  currency: string;
}
