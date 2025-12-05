import { LineChartOutlined } from "@ant-design/icons";
import {
  theme,
  Layout,
  ConfigProvider,
  Typography,
  Row,
  Divider,
  Col,
  Space,
  Button,
} from "antd";
import { Content, Footer, Header } from "antd/es/layout/layout";
import styles from "./App.module.css";
import "./styles/styles.css";
import "bootstrap/dist/css/bootstrap.min.css";
import HeaderCards from "./components/header-cards/header-cards";
import DonutChart from "./components/pie-chart/pie-chart";
import { DividendsTable } from "./components/dividends-table/dividends-table";
import LineChart from "./components/line-chart/line-chart";
import { useUpdateCurrentYearDividends } from "./hooks/api.hooks";

function App() {
  const { mutate: updateDividends, isLoading: isUpdating } =
    useUpdateCurrentYearDividends();

  const handleRefresh = () => {
    // call the mutate function returned by the hook
    updateDividends();
  };
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        components: {
          Statistic: {
            padding: 0,
          },
          Card: {
            bodyPadding: 16,
          },
        },
      }}
    >
      <Layout>
        <Header className={styles.header}>
          <Row
            className={styles.headerTitle}
            justify="space-between"
            align="middle"
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <LineChartOutlined className={styles.icon} />
              <Typography.Title level={3} style={{ margin: 0 }}>
                Dividend Tracker
              </Typography.Title>
            </div>
            <span>
              <Button type="text" onClick={handleRefresh} loading={isUpdating}>
                Refresh
              </Button>
            </span>
          </Row>
          <Divider className={styles.divider} />
        </Header>
        <Content className={styles.content}>
          <HeaderCards />
          <Row className={styles.chartRow}>
            <Col span={12} className={styles.chartCol}>
              <DonutChart />
            </Col>
            <Col span={12} className={styles.chartCol}>
              <LineChart />
            </Col>
          </Row>
          <Space direction="vertical" />
          <Row>
            <DividendsTable />
          </Row>
        </Content>
        <Footer />
      </Layout>
    </ConfigProvider>
  );
}

export default App;
