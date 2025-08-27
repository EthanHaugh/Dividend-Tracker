import { GetProp, Table, TableProps } from "antd";
import styles from "./dividends-table.module.css";
import { useListDividendPayments } from "../../hooks/api.hooks";
import { DividendPayment } from "../../models/models";
import { useState } from "react";

type ColumnsType<T extends object> = GetProp<TableProps<T>, "columns">;

export function DividendsTable() {
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);

  const { data, isLoading } = useListDividendPayments(page, pageSize);

  const columns: ColumnsType<DividendPayment> = [
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
      width: 250,
      ellipsis: true,
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
      className={styles.table}
      dataSource={data?.data}
      columns={columns}
      loading={isLoading}
      scroll={{ y: 400 }}
      pagination={{
        current: page,
        pageSize: pageSize,
        total: data?.total_count,
        onChange: (page, pageSize) => {
          setPage(page);
          setPageSize(pageSize);
        },
      }}
    />
  );
}
