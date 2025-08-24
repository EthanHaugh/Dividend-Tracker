import { LineChartOutlined } from "@ant-design/icons";
import {
  theme,
  Layout,
  ConfigProvider,
  Typography,
  Row,
  Col,
  Card,
  Divider,
  Skeleton,
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
              <Card className={styles.card}>
                <Skeleton loading={totalDividendsLoading} active>
                  <Typography.Text type="secondary">
                    Total Dividends
                  </Typography.Text>
                  <Typography.Title level={2} style={{ margin: 0 }}>
                    £ {totalDividends}
                  </Typography.Title>
                </Skeleton>
              </Card>
            </Col>
            <Col span={6}>
              <Card className={styles.card}>
                <Skeleton loading={isLoadingPreviousYear} active>
                  <Typography.Text type="secondary">
                    Previous Year Avg. Monthly
                  </Typography.Text>
                  <Typography.Title level={2} style={{ margin: 0 }}>
                    £{" "}
                    {(previousYearData
                      ? previousYearData / 12
                      : 0
                    ).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </Typography.Title>
                </Skeleton>
              </Card>
            </Col>
            <Col span={6}>
              <Card className={styles.card}>
                <Skeleton loading={accountCashLoading} active>
                  <Typography.Text type="secondary">
                    Portfolio Value
                  </Typography.Text>
                  <Typography.Title level={2} style={{ margin: 0 }}>
                    £{" "}
                    {accountCash?.account_value.toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </Typography.Title>
                </Skeleton>
              </Card>
            </Col>
            <Col span={6}>
              <Card className={styles.card}>
                <Skeleton
                  loading={accountCashLoading || totalDividendsLoading}
                  active
                >
                  <Typography.Text type="secondary">Yield</Typography.Text>
                  <Typography.Title level={2} style={{ margin: 0 }}>
                    {accountCash && totalDividends
                      ? (
                          (totalDividends / accountCash.account_value) *
                          100
                        ).toFixed(2)
                      : 0}
                    %
                  </Typography.Title>
                </Skeleton>
              </Card>
            </Col>
          </Row>
        </Content>
        <Footer style={{ textAlign: "center" }}>
          Ant Design ©{new Date().getFullYear()} Created by Ant UED
        </Footer>
      </Layout>
    </ConfigProvider>
  );
}

export default App;
