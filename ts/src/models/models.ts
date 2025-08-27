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
  created_at: string;
  currency: string;
  dividend_id: number;
  payment_date: string;
  number_of_shares: number;
  report_id: number;
  ticker: string;
  total_payment: number;
  year: number;
}
