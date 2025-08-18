from dataclasses import dataclass

@dataclass
class DividendHistory:
    reportId: int
    downloadLink: str
    timeFrom: str
    timeTo: str