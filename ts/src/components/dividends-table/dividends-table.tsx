import { Col, GetProp, Input, Row, Select, Table, TableProps } from "antd";
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
  const [filters, setFilters] = useState<string[]>([])
  const [tickers, setTickers] = useState<string[]>([])

  const { data: companyTotalsData, isLoading: companyTotalsLoading } = useListCompanyTotals(page, pageSize, search, filters)
  const { data: availableTickersData, isLoading: tickersLoading } = useListAvailableTickers();

  const columns: ColumnsType<DividendPayment> = [
    {
      title: "Company",
      dataIndex: "name",
      key: "name",
      width: "80%",
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
      <Row justify={"end"} className={styles.row} gutter={5}>
        <Col>
          <Select
            mode="multiple"
            className={styles.search}
            placeholder="Please select"
            allowClear
            loading={tickersLoading}
            maxTagCount={1}
            showSearch
            options={availableTickersData?.map((item) => { return { value: item.ticker, label: item.name } })}
            onOpenChange={handleDropdownSelect}
            onSelect={handleSelect}
            onClear={handleSelectClear}
          />
        </Col>
        <Col>
          <Input.Search
            placeholder="Search by ticker"
            className={styles.search}
            onChange={(e) => handleSearchChange(e.target.value)}
          />
        </Col>
      </Row>
      <Row>
        <Table
          dataSource={companyTotalsData?.data}
          columns={columns}
          className={styles.table}
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
        />
      </Row>
    </>
  );
}
