import { DividendPayment, AvailableTicker } from "../../../models/models";

export const mockTableData = {
    data: {
        data: [
            {
                last_payment_date: "14-05-2026",
                name: "Aviva",
                ticker: "AVl_EQ",
                total_payments: "771.6500"
            },
            {
                last_payment_date: "04-06-2026",
                name: "Legal & General",
                ticker: "LGENl_EQ",
                total_payments: "382.9300"
            },
            {
                last_payment_date: "30-06-2026",
                name: "Ares Capital",
                ticker: "ARCC_US_EQ",
                total_payments: "91.4500"
            },
            {
                last_payment_date: "09-06-2026",
                name: "AGNC Investment",
                ticker: "AGNC_US_EQ",
                total_payments: "89.5600"
            },
            {
                last_payment_date: "18-06-2026",
                name: "Prospect Capital",
                ticker: "PSEC_US_EQ",
                total_payments: "79.1600"
            },
            {
                last_payment_date: "13-01-2026",
                name: "National Grid",
                ticker: "NGl_EQ",
                total_payments: "58.9100"
            },
            {
                last_payment_date: "29-06-2026",
                name: "Main Street Capital",
                ticker: "MAIN_US_EQ",
                total_payments: "57.2100"
            },
            {
                last_payment_date: "02-04-2026",
                name: "Pennon",
                ticker: "PNNl_EQ",
                total_payments: "57.1500"
            },
            {
                last_payment_date: "30-06-2026",
                name: "iShares J.P. Morgan USD EM Bond (Dist)",
                ticker: "SEMBl_EQ",
                total_payments: "46.8200"
            },
            {
                last_payment_date: "12-06-2026",
                name: "3M",
                ticker: "MMM_US_EQ",
                total_payments: "44.5000"
            }
        ] as DividendPayment[],
        page: 1,
        page_size: 10,
        total_count: 20
    },
    isLoading: false,
    error: null,
    statusCode: undefined
}

export const mockHeaderData = {
  data: [
    {
      name: "Apple",
      ticker: "AAPL_US_EQ"
    },
    {
      name: "Archer-Daniels-Midland",
      ticker: "ADM_US_EQ"
    },
    {
      name: "Automatic Data Processing",
      ticker: "ADP_US_EQ"
    },
    {
      name: "Aflac",
      ticker: "AFL_US_EQ"
    },
    {
      name: "AGNC Investment",
      ticker: "AGNC_US_EQ"
    },
    {
      name: "Ares Capital",
      ticker: "ARCC_US_EQ"
    },
    {
      name: "Aviva",
      ticker: "AVl_EQ"
    },
    {
      name: "Franklin Resources",
      ticker: "BEN_US_EQ"
    },
    {
      name: "Bank of Montreal",
      ticker: "BMO_US_EQ"
    },
    {
      name: "Bank of Nova Scotia",
      ticker: "BNS_US_EQ"
    }
  ] as AvailableTicker[],
  isLoading: false,
  error: null,
  statusCode: undefined,
}