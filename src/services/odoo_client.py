"""Odoo XML-RPC Client service for authentication and CRM Lead operations."""

import logging
import socket
import xmlrpc.client
from typing import Any, cast
from urllib.parse import urlparse

from src.core.config import settings
from src.core.exceptions import (
    OdooAuthenticationError,
    OdooConnectionError,
    OdooOperationError,
)

logger = logging.getLogger(__name__)


class TimeoutTransport(xmlrpc.client.Transport):
    """Custom HTTP transport with configurable socket timeout."""

    def __init__(self, timeout: int = 10, *args: Any, **kwargs: Any) -> None:
        """Initialize transport with timeout."""
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host: Any) -> Any:
        """Create HTTPConnection with socket timeout configured."""
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn


class TimeoutSafeTransport(xmlrpc.client.SafeTransport):
    """Custom HTTPS transport with configurable socket timeout."""

    def __init__(self, timeout: int = 10, *args: Any, **kwargs: Any) -> None:
        """Initialize safe transport with timeout."""
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host: Any) -> Any:
        """Create HTTPSConnection with socket timeout configured."""
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn


class OdooClient:
    """Client for communicating with Odoo server via XML-RPC."""

    def __init__(
        self,
        url: str | None = None,
        db: str | None = None,
        username: str | None = None,
        password: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Initialize OdooClient with connection parameters.

        Falls back to global settings if values are not explicitly passed.
        """
        self.url = (url or settings.url).rstrip("/")
        self.db = db or settings.db
        self.username = username or settings.username
        self.password = password or settings.password
        self.timeout = timeout or settings.timeout
        self.uid: int | None = None

    def _get_transport(self) -> xmlrpc.client.Transport:
        """Return appropriate Transport (HTTP or HTTPS) based on server URL."""
        parsed = urlparse(self.url)
        if parsed.scheme == "https":
            return TimeoutSafeTransport(timeout=self.timeout)
        return TimeoutTransport(timeout=self.timeout)

    def _get_common_proxy(self) -> xmlrpc.client.ServerProxy:
        """Return XML-RPC ServerProxy for the /xmlrpc/2/common endpoint."""
        endpoint = f"{self.url}/xmlrpc/2/common"
        return xmlrpc.client.ServerProxy(
            endpoint,
            transport=self._get_transport(),
            allow_none=True,
        )

    def _get_object_proxy(self) -> xmlrpc.client.ServerProxy:
        """Return XML-RPC ServerProxy for the /xmlrpc/2/object endpoint."""
        endpoint = f"{self.url}/xmlrpc/2/object"
        return xmlrpc.client.ServerProxy(
            endpoint,
            transport=self._get_transport(),
            allow_none=True,
        )

    def authenticate(self, force_reauth: bool = False) -> int:
        """Authenticate with Odoo and retrieve user id (uid).

        Args:
            force_reauth: If True, re-authenticates even if uid is already cached.

        Returns:
            int: The authenticated user ID (uid).

        Raises:
            OdooAuthenticationError: If credentials or database name are invalid.
            OdooConnectionError: If server is unreachable or request times out.
        """
        if self.uid is not None and not force_reauth:
            return self.uid

        logger.info(
            "Authenticating with Odoo: url=%s, db=%s, user=%s",
            self.url,
            self.db,
            self.username,
        )

        try:
            common = self._get_common_proxy()
            uid = common.authenticate(self.db, self.username, self.password, {})

            if not uid:
                raise OdooAuthenticationError(
                    "Odoo authentication failed: Invalid"
                    + " username, password, or database name."
                )

            self.uid = cast(int, uid)
            logger.info("Successfully authenticated with Odoo. UID: %d", self.uid)
            return self.uid

        except xmlrpc.client.Fault as fault:
            logger.error("XML-RPC Fault during authentication: %s", fault.faultString)
            raise OdooAuthenticationError(
                f"Authentication rejected by Odoo: {fault.faultString}"
            ) from fault
        except (
            socket.timeout,
            ConnectionRefusedError,
            socket.gaierror,
            OSError,
            xmlrpc.client.ProtocolError,
        ) as conn_err:
            logger.error("Connection error during authentication: %s", str(conn_err))
            raise OdooConnectionError(
                "Failed to connect to Odoo server. "
                + "Please check URL and network status.",
                details=str(conn_err),
            ) from conn_err

    def create_lead(self, lead_data: dict[str, Any]) -> int:
        """Create a new Lead in Odoo CRM ('crm.lead').

        Args:
            lead_data: Dictionary containing Lead fields.

        Returns:
            int: The created Lead ID in Odoo.

        Raises:
            OdooAuthenticationError: If authentication fails.
            OdooOperationError: If lead creation is rejected by Odoo.
            OdooConnectionError: If connection drops or times out.
        """
        uid = self.authenticate()
        payload = self._prepare_lead_payload(lead_data)

        logger.info("Creating lead in Odoo with payload: %s", payload)

        try:
            models = self._get_object_proxy()
            lead_id = models.execute_kw(
                self.db,
                uid,
                self.password,
                "crm.lead",
                "create",
                [payload],
            )

            if not lead_id or not isinstance(lead_id, int):
                raise OdooOperationError(
                    f"Unexpected response from Odoo when creating lead: {lead_id}"
                )

            logger.info("Lead created successfully with ID: %d", lead_id)
            return lead_id

        except xmlrpc.client.Fault as fault:
            logger.error("XML-RPC Fault during lead creation: %s", fault.faultString)
            raise OdooOperationError(
                f"Odoo rejected lead creation: {fault.faultString}",
                details=str(fault),
            ) from fault
        except (
            socket.timeout,
            ConnectionRefusedError,
            socket.gaierror,
            OSError,
            xmlrpc.client.ProtocolError,
        ) as conn_err:
            logger.error("Connection error during lead creation: %s", str(conn_err))
            raise OdooConnectionError(
                "Network error or timeout occurred while creating lead in Odoo.",
                details=str(conn_err),
            ) from conn_err

    @staticmethod
    def _prepare_lead_payload(data: dict[str, Any]) -> dict[str, Any]:
        """Normalize and map schema fields to standard Odoo crm.lead model fields."""
        payload: dict[str, Any] = {
            "name": data.get("name", "New Lead"),
        }

        if data.get("contact_name"):
            payload["contact_name"] = data["contact_name"]
        if data.get("phone"):
            payload["phone"] = data["phone"]
        if data.get("email"):
            payload["email_from"] = data["email"]

        # Preserve event details into lead description
        notes: list[str] = []
        if data.get("event"):
            notes.append(f"Event: {data['event']}")
        if data.get("event_location"):
            notes.append(f"Location: {data['event_location']}")

        existing_desc = data.get("description", "")
        if notes:
            additional_notes = "\n".join(notes)
            if existing_desc:
                payload["description"] = f"{existing_desc}\n{additional_notes}"
            else:
                payload["description"] = additional_notes
        elif existing_desc:
            payload["description"] = existing_desc

        return payload
