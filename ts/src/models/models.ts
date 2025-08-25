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
