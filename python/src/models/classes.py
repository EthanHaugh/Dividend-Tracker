from dataclasses import dataclass


@dataclass
class DividendHistory:
    reportId: int
    downloadLink: str
    timeFrom: str
    timeTo: str


@dataclass
class AccountCashResponse:
    free: float
    total: float
    ppl: float
    result: float
    invested: float
    pieCash: float
    blocked: float
