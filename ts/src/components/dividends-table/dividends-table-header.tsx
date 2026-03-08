import { Col, Input, Row, Select, Skeleton, Typography } from "antd"
import { useListAvailableTickers } from "../../hooks/api.hooks";
import styles from "./dividends-table.module.css"

export interface DividendsTableHeaderProps {
    isLoading: boolean;
    total_count: number;
    selectOnOpen: (open: boolean) => void;
    selectOnSelect: (ticker: string) => void;
    selectOnClear: () => void;
    searchOnChange: (value: string) => void;
}


export function DividendsTableHeader({ isLoading, total_count, selectOnOpen, selectOnSelect, selectOnClear, searchOnChange }: DividendsTableHeaderProps) {
    const { data: availableTickersData, isLoading: tickersLoading } = useListAvailableTickers();

    return (
        <Row justify={"space-between"} className={styles.row} gutter={5}>
            {isLoading ? <Skeleton /> :
                <Row align="middle" gutter={5}>
                    <Col>
                        <Typography.Title level={3} type="secondary" style={{ margin: 0 }}>
                            {total_count}
                        </Typography.Title>
                    </Col>
                    <Col>
                        <Typography.Title level={5} type="secondary" style={{ margin: 0 }}>
                            Dividend Payers
                        </Typography.Title>
                    </Col>
                </Row>
            }
            <Row gutter={5}>
                <Col>
                    <Select
                        mode="multiple"
                        className={styles.tickerSelect}
                        placeholder="Filter"
                        allowClear
                        loading={tickersLoading}
                        maxTagCount={0}
                        showSearch
                        options={availableTickersData?.map((item) => { return { value: item.ticker, label: item.name } })}
                        onOpenChange={selectOnOpen}
                        onSelect={selectOnSelect}
                        onClear={selectOnClear}
                    />
                </Col>
                <Col>
                    <Input
                        placeholder="Search..."
                        className={styles.search}
                        onChange={(e) => searchOnChange(e.target.value)}
                    />
                </Col>
            </ Row>
        </Row >
    )
}

export default DividendsTableHeader