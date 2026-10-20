import { Button, DatePicker, Space } from "antd";
import dayjs from "dayjs";
import { useState } from "react";
import { useUpdateCurrentYearDividends } from "../../hooks/api.hooks";

export default function RefreshControls() {
    const [year, setYear] = useState<number | undefined>(
        new Date().getFullYear(),
    );
    const { mutate: updateDividends, isLoading: isUpdating } =
        useUpdateCurrentYearDividends();

    const handleRefresh = () => {
        updateDividends(year);
    };

    const handleDateChange = (date: dayjs.Dayjs | null) => {
        setYear(date ? date.year() : undefined)
    };

    const disabledDate = (current: dayjs.Dayjs) =>
        current && current > dayjs().endOf("year");

    return (
        <Space.Compact>
            <Button onClick={handleRefresh} loading={isUpdating}>
                Refresh
            </Button>
            <DatePicker
                picker="year"
                placeholder="Select year"
                disabledDate={disabledDate}
                value={year ? dayjs().year(year) : null}
                onChange={handleDateChange}
            />
        </Space.Compact>
    );
}