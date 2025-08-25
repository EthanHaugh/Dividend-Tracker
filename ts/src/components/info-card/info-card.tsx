import { Card, Skeleton, Typography } from "antd";
import styles from "./info-card.module.css";

interface InfoCardProps {
  title: string;
  loading: boolean;
  value?: string | number;
  footerTitle?: string;
  footerValue?: string | number;
}

export function InfoCard({
  title,
  value,
  loading,
  footerTitle,
  footerValue,
}: InfoCardProps) {
  return (
    <Card className={styles.card}>
      <Skeleton loading={loading} active>
        <Typography.Text type="secondary">{title}</Typography.Text>
        <Typography.Title level={2} style={{ margin: 0 }}>
          {value}
        </Typography.Title>
        {footerTitle && (
          <Typography.Text type="secondary" className={styles.footer}>
            {footerTitle}: {footerValue}
          </Typography.Text>
        )}
      </Skeleton>
    </Card>
  );
}

export default InfoCard;
