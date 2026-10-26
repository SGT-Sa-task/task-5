"""Pydantic models for CRM Lead data validation and serialization."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LeadBase(BaseModel):
    """Base schema containing common Lead fields."""

    name: str = Field(
        ...,
        description="Opportunity / Lead title or requirement summary",
        min_length=1,
        max_length=255,
    )
    contact_name: str | None = Field(
        default=None,
        description="Customer or contact person full name",
        max_length=128,
    )
    phone: str | None = Field(
        default=None,
        description="Contact phone number",
        max_length=64,
    )
    email: EmailStr | None = Field(
        default=None,
        description="Contact email address",
    )
    event: str | None = Field(
        default=None,
        description="Event name or campaign source",
        max_length=128,
    )
    event_location: str | None = Field(
        default=None,
        description="Event or meeting location",
        max_length=255,
    )


class LeadCreate(LeadBase):
    """Schema for incoming request payload to create a Lead."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Hợp đồng tư vấn ERP Odoo",
                "contact_name": "Nguyễn Văn A",
                "phone": "0901234567",
                "email": "nguyenvana@example.com",
                "event": "TechExpo 2026",
                "event_location": "SECC TP.HCM",
            }
        }
    )


class LeadResponse(BaseModel):
    """Schema for API response after Lead creation."""

    success: bool = Field(default=True, description="Operation status indicator")
    lead_id: int = Field(..., description="Generated Odoo CRM Lead ID")
    message: str = Field(
        default="Lead created successfully",
        description="Status description",
    )
