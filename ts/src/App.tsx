import { LineChartOutlined } from "@ant-design/icons";
import { theme, Layout, ConfigProvider, Typography, Row, Divider } from "antd";
import { Content, Footer, Header } from "antd/es/layout/layout";
import styles from "./App.module.css";
import "./styles/styles.css";
import "bootstrap/dist/css/bootstrap.min.css";
import HeaderCards from "./components/header-cards/header-cards";

function App() {
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
          <Row className={styles.headerTitle}>
            <LineChartOutlined className={styles.icon} />
            <Typography.Title level={3} style={{ margin: 0 }}>
              Dividend Tracker
            </Typography.Title>
          </Row>
          <Divider />
        </Header>
        <Content style={{ padding: "0 48px" }}>
          <HeaderCards />
        </Content>
        <Footer />
      </Layout>
    </ConfigProvider>
  );
}

export default App;
