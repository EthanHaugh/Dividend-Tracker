export interface AccountCashResponse {
  id: number;
  account_value: number;
  estimated_deposits: number;
}

export interface PieChartResponse {
  data: {
    ticker: string;
    name: string;
    total_payment: number;
    percentage: number;
  }[];
  total_count: number;
}

export interface ListDividendsResponse {
  data: DividendPayment[];
  page: number;
  page_size: number;
  total_count: number;
}

export interface DividendPayment {
  ticker: string;
  name: string;
  total_payments: number;
  updated_at: string;
}

export interface YearlyDividendsResponse {
  year: number;
  created_at: string;
  id: number;
  total_dividends: number;
  yoy_increase: number;
}

export interface ListCompanyDividendsResponse {
  data: Dividend[];
  page: number;
  total_count: number;
  page_size: number;
}

export interface ListAvailableTickersResponse {
  data: AvailableTicker[]
}

interface AvailableTicker {
  ticker: string;
  name: string;
}

export interface Dividend {
  company_id: number,
  created_at: string;
  dividend_id: number;
  number_of_shares: number;
  report_id: number;
  year: number;
  ticker: string;
  payment_date: string;
  total_payment: string;
  currency: string;
}

export interface ListAvaiableTickersResponse {
  data: string[]
}

export interface DividendProjectionsResponse {
  annual_contribution: number,
  cagr: number,
  cagr_pct: string
  capital_growth_rate: number,
  capital_growth_rate_pct: string,
  cumulative_dividends_recieived: number,
  final_year: {
    annual_dividend: number,
    portfolio_value: number,
    real_annual_dividend: number,
    real_portfolio_value: number,
    year: number
  },
  growth_rate: number,
  growth_rate_companies_used: number,
  growth_rate_pct: string,
  inflation_rate: number,
  inflation_rate_pct: string,
  investment_only_growth: number,
  reinvest: boolean,
  starting_portfolio_value: number,
  starting_yield_pct: string,
  total_contributions: number,
  total_dividend_growth_pct: string,
  years: DividendProjectionYears[]
}

interface DividendProjectionYears {
  annual_dividend: number,
  cumulative_contributions: number,
  portfolio_value: number,
  real_annual_dividend: number,
  real_portfolio_value: number,
  year: number,
  yield_on_cost: string
}