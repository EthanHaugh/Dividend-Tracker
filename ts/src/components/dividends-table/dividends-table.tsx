import { GetProp, Table, TableProps } from "antd";
import styles from "./dividends-table.module.css";
import { useListCompanyTotals } from "../../hooks/api.hooks";
import { DividendPayment } from "../../models/models";
import { useState, useEffect, useRef } from "react";
import { DividendsTableRowExpand } from "../dividends-table-row-expand/dividends-table-row-expand";
import { DividendsTableHeader } from "./dividends-table-header";

type ColumnsType<T extends object> = GetProp<TableProps<T>, "columns">;

export function DividendsTable() {
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [search, setSearch] = useState<string>("");
  const [searchInput, setSearchInput] = useState<string>("");
  const [filters, setFilters] = useState<string[]>([])
  const [sortBy, setSortBy] = useState<string | undefined>()
  const [sortDirection, setSortDirection] = useState<string | undefined>()

  const [tickers, setTickers] = useState<string[]>([])
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  const { data: companyTotalsData, isLoading: companyTotalsLoading } = useListCompanyTotals(page, pageSize, search, filters, sortBy, sortDirection)


  useEffect(() => {
    // Debounce to ensure calls are not made on every key stroke
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      setSearch(searchInput);
    }, 300);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [searchInput]);

  const handleTableChange: TableProps<DividendPayment>['onChange'] = (pagination, filters, sorter) => {
    if (sorter) {
      setSortBy(Array.isArray(sorter) ? undefined : sorter.columnKey as string)
      setSortDirection(Array.isArray(sorter) ? undefined : sorter.order as string)
    }
  }

  const columns: ColumnsType<DividendPayment> = [
    {
      title: "Company",
      dataIndex: "name",
      key: "name",
      width: "65%",
      sorter: true,
    },
    {
      title: "Total Payment",
      dataIndex: "total_payments",
      render: (payment: string) => <span>£ {Number(payment).toFixed(2)}</span>,
      key: "total_payments",
      width: "15%",
      sorter: true,
    },
    {
      title: "Last Payment Date",
      dataIndex: "last_payment_date",
      render: (date: string) => date,
      width: "20%",
      key: 'last_payment_date',
      sorter: true,
    }
  ];

  const handleSearchChange = (value: string) => {
    setSearchInput(value);
  };

  const handleDropdownSelect = (open: boolean) => {
    if (!open) {
      setFilters(tickers)
    }
  }

  const handleSelect = (ticker: string) => {
    setTickers([...tickers, ticker])
  }

  const handleSelectClear = () => {
    setFilters([])
    setTickers([])
  }

  return (
    <>
      <DividendsTableHeader isLoading={companyTotalsLoading} total_count={companyTotalsData?.total_count || 0} selectOnOpen={handleDropdownSelect} selectOnSelect={handleSelect} searchOnChange={handleSearchChange} selectOnClear={handleSelectClear} />
      <Table
        dataSource={companyTotalsData?.data}
        columns={columns}
        className={styles.table}
        rowKey={(row) => row.ticker}
        loading={companyTotalsLoading}
        scroll={{ y: 400 }}
        onChange={handleTableChange}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: companyTotalsData?.total_count,
          onChange: (page, pageSize) => {
            setPage(page);
            setPageSize(pageSize);
          },
        }}
        expandable={{
          expandedRowRender: (record) => (
            <DividendsTableRowExpand ticker={record.ticker} />
          ),
        }}
      />
    </>
  );
}