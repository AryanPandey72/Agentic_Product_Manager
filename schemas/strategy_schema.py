from pydantic import BaseModel, Field
from typing import List

class RiskMitigationPair(BaseModel):
    risk: str = Field(description="Potential business, technical, or user adoption risk.")
    mitigation: str = Field(description="Strategic action plan to neutralize the risk.")

class ProductStrategySchema(BaseModel):
    market_positioning: str = Field(description="A concise statement defining how the product stands out against competitors.")
    unique_value_proposition: str = Field(description="The core, irreplaceable benefit that makes customers choose this product over alternatives.")
    monetization_strategy: List[str] = Field(description="Max 3 items outlining revenue streams or business value generation models.")
    acquisition_channels: List[str] = Field(description="Max 3 target growth channels to reach and onboard the target users effectively.")
    mvp_scope: List[str] = Field(description="Max 5 core features that must be built for the initial launch phase.")
    gtm_phases: List[str] = Field(description="Max 3 chronological phases for launching and acquiring early users.")
    risks_and_mitigations: List[RiskMitigationPair] = Field(description="Max 3 critical risk-mitigation pairs.")