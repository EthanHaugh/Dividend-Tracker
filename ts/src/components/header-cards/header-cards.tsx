import { Col, Row } from "antd";
import InfoCard from "../info-card/info-card";
import {
  useGetAccountCash,
  useGetPreviousYearDividends,
  useGetTotalDividends,
} from "../../hooks/api.hooks";
import {
  AreaChartOutlined,
  BankOutlined,
  CalendarOutlined,
  PercentageOutlined,
} from "@ant-design/icons";

export function HeaderCards() {
  const { data: totalDividends, isLoading: totalDividendsLoading } =
    useGetTotalDividends();
  const { data: previousYearData, isLoading: isLoadingPreviousYear } =
    useGetPreviousYearDividends();
  const { data: accountCash, isLoading: accountCashLoading } =
    useGetAccountCash();

  return (
    <Row justify={"space-between"} gutter={24}>
      <Col span={6}>
        <InfoCard
          title="Total Dividends"
          value={`£ ${totalDividends?.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`}
          loading={totalDividendsLoading}
          suffix={<BankOutlined />}
        />
      </Col>
      <Col span={6}>
        <InfoCard
          title="Prev. Year Avg. Monthly"
          value={`£ ${(previousYearData
            ? previousYearData / 12
            : 0
          ).toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`}
          loading={isLoadingPreviousYear}
          suffix={<CalendarOutlined />}
        />
      </Col>
      <Col span={6}>
        <InfoCard
          title="Portfolio Value"
          value={`£ ${accountCash?.account_value.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`}
          loading={accountCashLoading}
          footerTitle="Estimated Deposits"
          footerValue={`£${accountCash?.estimated_deposits.toLocaleString(
            undefined,
            {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }
          )}`}
          suffix={<AreaChartOutlined />}
        />
      </Col>
      <Col span={6}>
        <InfoCard
          title="Yield"
          value={`~${
            accountCash && previousYearData
              ? (
                  (previousYearData / accountCash.estimated_deposits) *
                  100
                ).toFixed(2)
              : 0
          }
                    %`}
          loading={accountCashLoading || totalDividendsLoading}
          suffix={<PercentageOutlined />}
        />
      </Col>
    </Row>
  );
}

export default HeaderCards;
