from dataclasses import dataclass


@dataclass
class DividendHistory:
    reportId: int
    downloadLink: str
    timeFrom: str
    timeTo: str


@dataclass
class _AccountCash:
    availableToTrade: float
    inPies: float
    reservedForOrders: float


@dataclass
class _AccountInvestments:
    currentValue: float
    realizedProfitLoss: float
    totalCost: float
    unrealizedProfitLoss: float


@dataclass
class AccountSummaryResponse:
    cash: _AccountCash
    currency: str
    id: int
    investments: _AccountInvestments
    totalValue: float

    def __post_init__(self):
        if isinstance(self.cash, dict):
            self.cash = _AccountCash(**self.cash)
        if isinstance(self.investments, dict):
            self.investments = _AccountInvestments(**self.investments)
