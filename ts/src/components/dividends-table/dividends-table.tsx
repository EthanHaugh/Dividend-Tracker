import { GetProp, Input, Row, Table, TableProps } from "antd";
import styles from "./dividends-table.module.css";
import { useListCompanyTotals } from "../../hooks/api.hooks";
import { DividendPayment } from "../../models/models";
import { useState } from "react";
import { DividendsTableRowExpand } from "../dividends-table-row-expand/dividends-table-row-expand";

type ColumnsType<T extends object> = GetProp<TableProps<T>, "columns">;

export function DividendsTable() {
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [search, setSearch] = useState<string>("");

  const { data, isLoading } = useListCompanyTotals(page, pageSize, search);

  const columns: ColumnsType<DividendPayment> = [
    {
      title: "Ticker",
      dataIndex: "ticker",
      key: "ticker",
      width: 75,
    },
    {
      title: "Total Payment",
      dataIndex: "total_payment",
      render: (payment: string) => <span>£ {Number(payment).toFixed(2)}</span>,
      key: "total_payment",
    },
  ];

  const handleSearchChange = (value: string) => {
    setSearch(value);
  };

  return (
    <>
      <Row justify={"end"} className={styles.row}>
        <Input.Search
          placeholder="Search by ticker"
          className={styles.search}
          onChange={(e) => handleSearchChange(e.target.value)}
        />
      </Row>
      <Row>
        <Table
          dataSource={data?.data}
          columns={columns}
          rowKey={(row) => row.ticker}
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
          expandable={{
            expandedRowRender: (record) => (
              <DividendsTableRowExpand ticker={record.ticker} />
            ),
          }}
          className={styles.table}
        />
      </Row>
    </>
  );
}
