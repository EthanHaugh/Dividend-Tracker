import { Card, Col, Row, Skeleton, Typography } from "antd";
import styles from "./info-card.module.css";
import Statistic from "antd/es/statistic/Statistic";
import { ReactElement } from "react";

interface InfoCardProps {
  title: string;
  loading: boolean;
  value?: string | number;
  footerTitle?: string;
  footerValue?: string | number;
  footerIcon?: ReactElement;
  suffix?: ReactElement;
}

export function InfoCard({
  title,
  value,
  loading,
  footerTitle,
  footerValue,
  footerIcon,
  suffix,
}: InfoCardProps) {
  return (
    <Card className={styles.card}>
      <Skeleton active loading={loading} paragraph={false}>
        <Row align="middle" justify="space-between">
          <Col span={20}>
            <Statistic
              title={title}
              value={value}
              className={styles.statistic}
            />
            <Typography.Text type="secondary" className={styles.footer}>
              {/* <div>{footerTitle}{footerTitle ? ': ' : ''}{footerValue}{footerIcon && footerIcon}</div> */}
              {footerTitle && <div className={styles.footerItem}>{footerTitle}:</div>}
              {footerValue && <div className={styles.footerItem}>{footerValue}</div>}
              {footerIcon && <div className={styles.footerItem}>{footerIcon}</div>}
            </Typography.Text>
          </Col>
          <Col span={4}>
            <div className={styles.icon}>{suffix}</div>
          </Col>
        </Row>
      </Skeleton>
    </Card>
  );
}

export default InfoCard;
