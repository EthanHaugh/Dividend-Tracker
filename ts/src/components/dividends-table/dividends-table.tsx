import { GetProp, Input, Row, Select, Table, TableProps } from "antd";
import styles from "./dividends-table.module.css";
import { useListAvailableTickers, useListCompanyTotals } from "../../hooks/api.hooks";
import { DividendPayment } from "../../models/models";
import { useState } from "react";
import { DividendsTableRowExpand } from "../dividends-table-row-expand/dividends-table-row-expand";

type ColumnsType<T extends object> = GetProp<TableProps<T>, "columns">;

export function DividendsTable() {
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [search, setSearch] = useState<string>("");

  const { data: companyTotalsData, isLoading: companyTotalsLoading } = useListCompanyTotals(page, pageSize, search)
  const { data: availableTickersData, isLoading: tickersLoading } = useListAvailableTickers();

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

  console.log(availableTickersData)

  return (
    <>
      <Row justify={"end"} className={styles.row}>
        <Select
          mode="multiple"
          className={styles.search}
          placeholder="Please select"
          allowClear
          showSearch
          options={availableTickersData?.map((ticker) => { return { value: ticker, label: ticker } })}
        />
        <Input.Search
          placeholder="Search by ticker"
          className={styles.search}
          onChange={(e) => handleSearchChange(e.target.value)}
        />
      </Row>
      <Row>
        <Table
          dataSource={companyTotalsData?.data}
          columns={columns}
          rowKey={(row) => row.ticker}
          loading={companyTotalsLoading}
          scroll={{ y: 400 }}
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
          className={styles.table}
        />
      </Row>
    </>
  );
}
