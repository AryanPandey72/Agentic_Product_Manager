from pydantic import BaseModel, Field
from typing import List, Optional

# NEW: Define exactly what a column looks like
class ColumnDefinition(BaseModel):
    name: str = Field(description="The name of the database column (e.g., 'id', 'created_at')")
    data_type: str = Field(description="The SQL data type (e.g., 'UUID', 'TIMESTAMP', 'VARCHAR')")

class DatabaseTable(BaseModel):
    table_name: str
    # FIX: Use a List of models instead of a Dict
    columns: List[ColumnDefinition] = Field(description="List of columns for this table.")
    relationships: List[str] = Field(description="Foreign key relationships.")

class APIRoute(BaseModel):
    endpoint: str = Field(description="e.g., /api/v1/users")
    method: str = Field(description="GET, POST, PUT, DELETE")
    purpose: str = Field(description="What this endpoint does.")

class SecuritySpec(BaseModel):
    authentication_method: str = Field(description="e.g., OAuth2, JWT, Session-based.")
    authorization_roles: List[str] = Field(description="e.g., Admin, User, Manager.")
    data_privacy: str = Field(description="How sensitive data like passwords or PII are handled.")

class InfrastructureSpec(BaseModel):
    hosting: str = Field(description="Cloud provider and compute strategy.")
    caching_strategy: Optional[str] = Field(description="Caching layer if needed.")
    background_workers: Optional[str] = Field(description="Queue systems for async tasks.")
class FeatureMapping(BaseModel):
    feature_name: str = Field(
        description="Feature from the MVP scope."
    )

    database_tables: List[str] = Field(
        description="Database tables supporting this feature."
    )

    api_endpoints: List[str] = Field(
        description="API endpoints supporting this feature."
    )
class ArchitectureSchema(BaseModel):
    tech_stack: List[str] = Field(description="Recommended programming languages and frameworks.")
    infrastructure: InfrastructureSpec
    security: SecuritySpec
    third_party_integrations: List[str] = Field(description="External APIs needed.")
    database_schema: List[DatabaseTable]
    api_specifications: List[APIRoute]
    feature_mappings: List[FeatureMapping] = Field(
        description="Maps MVP features to their supporting tables and APIs.")