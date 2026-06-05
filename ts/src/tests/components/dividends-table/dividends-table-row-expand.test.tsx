import { expect, test, describe, vi, afterEach, beforeEach } from 'vitest'
import { DividendsTableRowExpand } from '../../../components/dividends-table-row-expand/dividends-table-row-expand'
import { cleanup, render, screen } from '@testing-library/react'
import { useListCompanyDividends } from '../../../hooks/api.hooks'
import { mockData } from './mocks'
import userEvent from '@testing-library/user-event'

vi.mock('../../../hooks/api.hooks.ts', () => ({
    useListCompanyDividends: vi.fn(),
}))

const mockedUseListCompanyDividends = vi.mocked(useListCompanyDividends)

describe('Test Dividends Table Row Expansion', () => {
    afterEach(() => {
        cleanup();
    });

    beforeEach(() => {
        mockedUseListCompanyDividends.mockReturnValue({
            data: {
                data: [],
                page: 1,
                page_size: 10,
                total_count: 0,
            },
            isLoading: false,
            error: null,
            statusCode: undefined,
        });
    });

    test('Table Render', () => {
        render(<DividendsTableRowExpand ticker="MSFT_US_EQ" />)

        expect(screen.getByTestId('MSFT_US_EQ-table')).not.toBeNull()
    })

    test('Table Empty Date', () => {
        render(<DividendsTableRowExpand ticker="MSFT_US_EQ" />)

        expect(screen.getAllByText('No data')).toBeDefined()
    })

    test('Table Columns', () => {
        render(<DividendsTableRowExpand ticker="MSFT_US_EQ" />)

        expect(screen.getByText('Ticker')).toBeDefined()
        expect(screen.getByText('Payment Date')).toBeDefined()
        expect(screen.getByText('No. of Shares')).toBeDefined()
        expect(screen.getByText('Total Payment')).toBeDefined()
    })

    test('Table Data', () => {
        mockedUseListCompanyDividends.mockReturnValue(mockData)

        render(<DividendsTableRowExpand ticker="MSFT_US_EQ" />)

        // Can't use `getByText` here, multiple rows, each displays the ticker
        expect(screen.getAllByText('MSFT_US_EQ')).toBeDefined()
    })

    test('Table Pagination', async () => {
        mockedUseListCompanyDividends.mockReturnValue(mockData)

        render(<DividendsTableRowExpand ticker="MSFT_US_EQ" />)

        const page2Button = screen.getByText('2')
        await userEvent.click(page2Button)

        expect(mockedUseListCompanyDividends).toHaveBeenLastCalledWith(
            2,
            5,
            'MSFT_US_EQ'
        )
    })
})