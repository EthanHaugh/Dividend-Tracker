import { LineChartOutlined } from "@ant-design/icons";
import {
  theme,
  Layout,
  ConfigProvider,
  Typography,
  Row,
  Col,
  Divider,
} from "antd";
import { Content, Footer, Header } from "antd/es/layout/layout";
import styles from "./App.module.css";
import "./styles/styles.css";
import "bootstrap/dist/css/bootstrap.min.css";
import {
  useGetAccountCash,
  useGetPreviousYearDividends,
  useGetTotalDividends,
} from "./hooks/api.hooks";
import InfoCard from "./components/info-card/info-card";

function App() {
  const { data: totalDividends, isLoading: totalDividendsLoading } =
    useGetTotalDividends();
  const { data: previousYearData, isLoading: isLoadingPreviousYear } =
    useGetPreviousYearDividends();
  const { data: accountCash, isLoading: accountCashLoading } =
    useGetAccountCash();

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
      }}
    >
      <Layout>
        <Header className={styles.header}>
          <Row className={styles.headerTitle}>
            <LineChartOutlined className={styles.icon} />
            <Typography.Title level={3} style={{ margin: 0 }}>
              Dividend Tracker
            </Typography.Title>
          </Row>
          <Divider />
        </Header>
        <Content style={{ padding: "0 48px" }}>
          <Row justify={"space-between"} gutter={24}>
            <Col span={6}>
              <InfoCard
                title="Total Dividends"
                value={`£ ${totalDividends?.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}`}
                loading={totalDividendsLoading}
              />
            </Col>
            <Col span={6}>
              <InfoCard
                title="Previous Year Avg. Monthly"
                value={`£ ${(previousYearData
                  ? previousYearData / 12
                  : 0
                ).toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}`}
                loading={isLoadingPreviousYear}
              />
            </Col>
            <Col span={6}>
              <InfoCard
                title="Portfolio Value"
                value={`£ ${accountCash?.account_value.toLocaleString(
                  undefined,
                  {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  }
                )}`}
                loading={accountCashLoading}
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
                footerTitle="Estimated Deposits"
                footerValue={`£${accountCash?.estimated_deposits.toLocaleString(
                  undefined,
                  {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  }
                )}`}
              />
            </Col>
          </Row>
        </Content>
        <Footer />
      </Layout>
    </ConfigProvider>
  );
}

export default App;
