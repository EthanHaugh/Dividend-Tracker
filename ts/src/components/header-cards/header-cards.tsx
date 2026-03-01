import { Col, Row, Tooltip } from "antd";
import InfoCard from "../info-card/info-card";
import {
  useGetAccountCash,
  useGetPreviousYearDividends,
  useGetTotalDividends,
} from "../../hooks/api.hooks";
import {
  AreaChartOutlined,
  ArrowDownOutlined,
  ArrowUpOutlined,
  BankOutlined,
  CalendarOutlined,
  InfoCircleOutlined,
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
          value={`£ ${totalDividends?.total_dividends.toLocaleString(undefined, {
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
            ? previousYearData.total_dividends / 12
            : 0
          ).toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`}
          footerTitle="YoY Increase"
          footerValue={`${previousYearData?.yoy_increase.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}% `}
          footerIcon={previousYearData?.yoy_increase! > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
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
          footerTitle="Est. Deposits"
          footerValue={`£${accountCash?.estimated_deposits.toLocaleString(
            undefined,
            {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }
          )}`}
          footerIcon={
            <Tooltip title="We don't have access to your deposit value, so we calculate this from total cost of shares minus your total dividends along with profit and loss">
              <InfoCircleOutlined />
            </Tooltip>
          }
          suffix={<AreaChartOutlined />}
        />
      </Col>
      <Col span={6}>
        <InfoCard
          title="Yield"
          value={`~${accountCash && previousYearData
            ? (
              (previousYearData.total_dividends / accountCash.estimated_deposits) *
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
