import { useState } from "react";
import { useListCompanyDividends } from "../../hooks/api.hooks";
import { Table } from "antd";
import { ColumnsType } from "antd/es/table";
import { Dividend } from "../../models/models";

interface DividendsTableRowExpandProps {
  ticker: string;
}

export function DividendsTableRowExpand({
  ticker,
}: DividendsTableRowExpandProps) {
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const { data, isLoading } = useListCompanyDividends(page, pageSize, ticker);

  const columns: ColumnsType<Dividend> = [
    {
      title: "Ticker",
      dataIndex: "ticker",
      key: "ticker",
      width: 75,
    },
    {
      title: "Payment Date",
      dataIndex: "payment_date",
      key: "payment_date",
    },
    {
      title: "No. of Shares",
      dataIndex: "number_of_shares",
      key: "number_of_shares",
    },
    {
      title: "Total Payment",
      dataIndex: "total_payment",
      render: (payment: string) => <span>£ {Number(payment).toFixed(2)}</span>,
      key: "total_payment",
    },
  ];

  return (
    <Table
      dataSource={data?.data}
      loading={isLoading}
      rowKey="id"
      pagination={{
        current: page,
        pageSize,
        onChange: (page, pageSize) => {
          setPage(page);
          setPageSize(pageSize);
        },
      }}
      columns={columns}
    />
  );
}
