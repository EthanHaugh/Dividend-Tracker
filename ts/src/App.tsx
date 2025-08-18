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
} from "antd";
import { Content, Footer, Header } from "antd/es/layout/layout";
import { useState } from "react";
import styles from "./App.module.css";
import "./styles/styles.css";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);

  return (
    <ConfigProvider
      theme={{
        algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
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
              <Card>
                <Card.Meta title="Stock A" description="Dividend: $2.00" />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Card.Meta title="Stock B" description="Dividend: $1.50" />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Card.Meta title="Stock C" description="Dividend: $3.00" />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Card.Meta title="Stock D" description="Dividend: $4.00" />
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
