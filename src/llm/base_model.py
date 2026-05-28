from pydantic import BaseModel
from  typing import List,Optional
class SnakeResponse(BaseModel):
    input_label: str
    canonical_name: str
    scientific_name: str
    habitat: str

    venomous: str
    venom_type: Optional[str]

    first_aid: List[str]

    emergency_priority: str

    safety_info: List[str]

    confidence_note: str

    verify_sources: List[str]

    timestamp: str