from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class AutoFilledParamsRequest(BaseModel):
    data_meatinfo: Dict[str, Any]
    query_template: Dict[str, Any]
    user: str = "abc-123"
    conversation_id: str = ""
    response_mode: str = "blocking"

class AutoFilledParamsResponse(BaseModel):
    code: int
    message: str
    filled_parameters: Optional[Dict[str, Any]] = None