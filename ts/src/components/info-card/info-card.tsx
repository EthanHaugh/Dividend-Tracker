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
  footerValueType?: "success" | "danger" | "secondary";
  footerIcon?: ReactElement;
  suffix?: ReactElement;
}

export function InfoCard({
  title,
  value,
  loading,
  footerTitle,
  footerValue,
  footerValueType = "secondary",
  footerIcon,
  suffix,
}: InfoCardProps) {
  return (
    <Card className={styles.card}>
      <Skeleton active loading={loading} paragraph={false}>
        <Row justify="space-between" style={{ height: '100%' }}>
          <Col span={20}>
            <Statistic
              title={title}
              value={value}
              className={styles.statistic}
            />
            <Typography.Text type="secondary" className={styles.footer}>
              {footerTitle && <div className={styles.footerItem}>{footerTitle}:</div>}
              {footerValue && (
                <div className={styles.footerItem}>
                  <Typography.Text type={footerValueType}>{footerValue}</Typography.Text>
                </div>
              )}
              {footerIcon && (
                <div className={styles.footerItem}>
                  <Typography.Text type={footerValueType}>{footerIcon}</Typography.Text>
                </div>
              )}
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
