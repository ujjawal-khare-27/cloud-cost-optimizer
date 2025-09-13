from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


def get_default_statistics():
    return ["Maximum"]


@dataclass
class CloudWatchMetric:
    namespace: str
    metric_name: str
    dimensions: List[Dict]
    start_time: datetime
    end_time: datetime
    period: int = 600
    statistics: List[str] = field(default_factory=get_default_statistics)
    unit: str = "Count"
