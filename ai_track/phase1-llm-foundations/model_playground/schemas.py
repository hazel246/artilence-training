from pydantic import BaseModel, Field
from typing import List

class BenchMarkResult(BaseModel):
    answer: str = Field(description="The final direct answer to the prompt")
    confidence:float = Field(description="Confidence score between 0 and 1")
    reasoning_steps: list[str] = Field(description="Key steps taken to reach the answer")

    

class MultimodalResult(BaseModel):
    image_description: str = Field(description="A detailed description of the image content.")
    extracted_fields: List[str] = Field(description="Key text elements, labels, or facts extracted from the image.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")