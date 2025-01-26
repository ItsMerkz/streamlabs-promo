from typing import Optional
from dataclasses import dataclass


@dataclass
class TurnstileAPIResult:
    task_id: Optional[str] = None  
    elapsed_time: Optional[float] = None
    capcha_key: Optional[str] = None
    status: str = "success"
