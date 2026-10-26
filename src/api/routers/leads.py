"""REST API routes for CRM Lead operations."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.exceptions import (
    OdooAuthenticationError,
    OdooConnectionError,
    OdooOperationError,
)
from src.schemas.lead import LeadCreate, LeadResponse
from src.services.odoo_client import OdooClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["Leads"])


def get_odoo_client() -> OdooClient:
    """Dependency provider for OdooClient instance."""
    return OdooClient()


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a CRM Lead in Odoo",
    description=(
        "Validate incoming lead information and create a new record in Odoo CRM."
    ),
)
def create_lead(
    lead_in: LeadCreate,
    client: Annotated[OdooClient, Depends(get_odoo_client)],
) -> LeadResponse:
    """Create a new CRM lead in Odoo.

    Args:
        lead_in: Validated lead payload.
        client: Injected OdooClient instance.

    Returns:
        LeadResponse: Created lead details including Odoo lead ID.

    Raises:
        HTTPException: If Odoo connection, authentication, or creation fails.
    """
    payload = lead_in.model_dump(exclude_none=True)

    try:
        lead_id = client.create_lead(payload)
        logger.info("Successfully created Odoo Lead with ID: %d", lead_id)
        return LeadResponse(
            success=True,
            lead_id=lead_id,
            message="Lead created successfully in Odoo CRM",
        )

    except OdooAuthenticationError as err:
        logger.error("Odoo authentication failure: %s", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Odoo authentication failed: {err}",
        ) from err

    except OdooConnectionError as err:
        logger.error("Odoo connection failure: %s", err)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Cannot connect to Odoo server: {err}",
        ) from err

    except OdooOperationError as err:
        logger.error("Odoo operation rejected: %s", err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Odoo operation rejected: {err}",
        ) from err

    except Exception as err:
        logger.exception("Unexpected error while creating lead: %s", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing lead creation.",
        ) from err
