"""Unit tests for OdooClient and related components."""

import unittest
from unittest.mock import MagicMock, patch
import xmlrpc.client

from src.core.config import settings
from src.core.exceptions import (
    OdooAuthenticationError,
    OdooConnectionError,
    OdooOperationError,
)
from src.schemas.lead import LeadCreate
from src.services.odoo_client import OdooClient


class TestOdooClient(unittest.TestCase):
    """Test suite for OdooClient service."""

    def setUp(self) -> None:
        """Set up test environment and initialize client."""
        self.client = OdooClient(
            url="http://test-odoo:8069",
            db="test_db",
            username="test_user",
            password="test_password",
            timeout=5,
        )

    def test_settings_loaded(self) -> None:
        """Verify global settings are loaded with valid defaults or env values."""
        self.assertTrue(settings.url.startswith("http"))
        self.assertIsNotNone(settings.db)
        self.assertIsNotNone(settings.username)
        self.assertGreater(settings.timeout, 0)

    def test_prepare_lead_payload(self) -> None:
        """Test normalization and mapping of lead dictionary to Odoo fields."""
        data = {
            "name": "Khách hàng VIP TechExpo",
            "contact_name": "Nguyễn Văn A",
            "phone": "0987654321",
            "email": "nguyenvana@example.com",
            "event": "TechExpo 2026",
            "event_location": "SECC TP.HCM",
        }
        payload = OdooClient._prepare_lead_payload(data)

        self.assertEqual(payload["name"], "Khách hàng VIP TechExpo")
        self.assertEqual(payload["contact_name"], "Nguyễn Văn A")
        self.assertEqual(payload["phone"], "0987654321")
        self.assertEqual(payload["email_from"], "nguyenvana@example.com")
        self.assertIn("Event: TechExpo 2026", payload["description"])
        self.assertIn("Location: SECC TP.HCM", payload["description"])

    @patch("src.services.odoo_client.OdooClient._get_common_proxy")
    def test_authenticate_success(self, mock_common: MagicMock) -> None:
        """Test successful authentication returning user id."""
        mock_proxy = MagicMock()
        mock_proxy.authenticate.return_value = 2
        mock_common.return_value = mock_proxy

        uid = self.client.authenticate()
        self.assertEqual(uid, 2)
        self.assertEqual(self.client.uid, 2)
        mock_proxy.authenticate.assert_called_once_with(
            "test_db", "test_user", "test_password", {}
        )

    @patch("src.services.odoo_client.OdooClient._get_common_proxy")
    def test_authenticate_invalid_credentials(
        self, mock_common: MagicMock
    ) -> None:
        """Test authentication failure when credentials are invalid."""
        mock_proxy = MagicMock()
        mock_proxy.authenticate.return_value = False
        mock_common.return_value = mock_proxy

        with self.assertRaises(OdooAuthenticationError):
            self.client.authenticate()

    @patch("src.services.odoo_client.OdooClient._get_common_proxy")
    def test_authenticate_connection_error(
        self, mock_common: MagicMock
    ) -> None:
        """Test handling of connection error during authentication."""
        mock_proxy = MagicMock()
        mock_proxy.authenticate.side_effect = TimeoutError("Connection timed out")
        mock_common.return_value = mock_proxy

        with self.assertRaises(OdooConnectionError):
            self.client.authenticate()

    @patch("src.services.odoo_client.OdooClient._get_object_proxy")
    @patch.object(OdooClient, "authenticate", return_value=2)
    def test_create_lead_success(
        self, mock_auth: MagicMock, mock_object: MagicMock
    ) -> None:
        """Test successful creation of a Lead in Odoo."""
        mock_proxy = MagicMock()
        mock_proxy.execute_kw.return_value = 101
        mock_object.return_value = mock_proxy

        lead_data = {
            "name": "Cơ hội kinh doanh ERP",
            "contact_name": "Trần Thị B",
            "phone": "0912345678",
            "email": "tranthib@example.com",
        }
        lead_id = self.client.create_lead(lead_data)

        self.assertEqual(lead_id, 101)
        mock_proxy.execute_kw.assert_called_once()
        args = mock_proxy.execute_kw.call_args[0]
        self.assertEqual(args[0], "test_db")
        self.assertEqual(args[1], 2)
        self.assertEqual(args[2], "test_password")
        self.assertEqual(args[3], "crm.lead")
        self.assertEqual(args[4], "create")

    @patch("src.services.odoo_client.OdooClient._get_object_proxy")
    @patch.object(OdooClient, "authenticate", return_value=2)
    def test_create_lead_fault(
        self, mock_auth: MagicMock, mock_object: MagicMock
    ) -> None:
        """Test handling of XML-RPC Fault when Odoo rejects lead creation."""
        mock_proxy = MagicMock()
        mock_proxy.execute_kw.side_effect = xmlrpc.client.Fault(
            1, "Field does not exist: invalid_field"
        )
        mock_object.return_value = mock_proxy

        with self.assertRaises(OdooOperationError):
            self.client.create_lead({"name": "Invalid Lead"})

    def test_lead_schema_validation(self) -> None:
        """Test Pydantic LeadCreate schema validation."""
        lead = LeadCreate(
            name="Khách hàng tiềm năng A",
            email="test@domain.com",
            phone="0909090909",
        )
        self.assertEqual(lead.name, "Khách hàng tiềm năng A")
        self.assertEqual(str(lead.email), "test@domain.com")


if __name__ == "__main__":
    unittest.main()
