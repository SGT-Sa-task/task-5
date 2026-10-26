"""CLI script to create an Odoo CRM Lead from JSON input or JSON file."""

import argparse
import json
import random
import sys
import unicodedata
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.core.exceptions import (
    OdooAuthenticationError,
    OdooConnectionError,
    OdooOperationError,
)
from src.schemas.lead import LeadCreate
from src.services.odoo_client import OdooClient

# Default path to sample JSON data
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SAMPLE_FILE = PROJECT_ROOT / "sample_data" / "sample_lead.json"


def generate_random_lead() -> dict[str, Any]:
    """Generate realistic random sample lead data for testing.

    Returns:
        dict[str, Any]: Random lead payload compliant with LeadCreate schema.
    """
    first_names = [
        "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ",
        "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý",
    ]
    middle_and_last = [
        "Văn An", "Thị Bình", "Quốc Cường", "Minh Dũng", "Thị Hạnh", "Văn Hải",
        "Tuấn Kiệt", "Bảo Long", "Thị Mai", "Hoàng Nam", "Thanh Phong",
        "Quang Phúc", "Hồng Quân", "Minh Tâm", "Đức Thắng", "Anh Tuấn",
    ]
    companies = [
        "SaigonTrade", "An Nam Logistics", "Mekong Corp", "TechVina", "VinaFood",
        "Nam Á Steel", "Việt Nhật Tech", "Đại Phát Retail",
    ]
    topics = [
        "Tư vấn triển khai hệ thống ERP Odoo",
        "Tối ưu hóa quy trình quản lý chuỗi cung ứng",
        "Tích hợp Odoo CRM với bán hàng đa kênh",
        "Xây dựng cổng thông tin khách hàng B2B",
        "Nâng cấp hạ tầng quản lý kho bãi & vận chuyển",
    ]
    events = [
        "Vietnam Tech Expo 2026",
        "Hội nghị Chuyển đổi số Doanh nghiệp 2026",
        "Diễn đàn Doanh nghiệp Quốc tế",
        "Triển lãm Công nghiệp & Tự động hóa",
        "Hội thảo Giải pháp ERP Thế hệ Mới",
    ]
    locations = [
        "Trung tâm Hội chợ và Triển lãm Sài Gòn (SECC)",
        "Trung tâm Hội nghị Quốc gia Hà Nội",
        "Khách sạn Vinpearl Landmark 81",
        "Trung tâm Hội nghị White Palace TP.HCM",
        "Gem Center TP.HCM",
    ]

    selected_first = random.choice(first_names)
    selected_last = random.choice(middle_and_last)
    contact_name = f"{selected_first} {selected_last}"
    company = random.choice(companies)
    lead_name = f"{random.choice(topics)} - {company}"

    # Generate random 10-digit phone number in VN prefix format
    prefix = random.choice(["09", "08", "07", "03"])
    suffix = f"{random.randint(10000000, 99999999)}"[:8]
    phone = f"{prefix}{suffix}"

    # Generate email based on ascii-normalized contact name and random id
    norm_name = unicodedata.normalize("NFKD", contact_name)
    ascii_name = "".join(
        c for c in norm_name if not unicodedata.combining(c) and c.isalnum()
    ).lower()
    rand_suffix = random.randint(100, 999)
    email = f"lead.{ascii_name[:8]}.{rand_suffix}@example.com"

    return {
        "name": lead_name,
        "contact_name": contact_name,
        "phone": phone,
        "email": email,
        "event": random.choice(events),
        "event_location": random.choice(locations),
    }


def load_json_data(
    file_path: str | None = None,
    raw_json: str | None = None,
    generate_random: bool = False,
) -> dict[str, Any]:
    """Load, parse, or generate Lead JSON data.

    Args:
        file_path: Optional path to the JSON file.
        raw_json: Optional raw JSON string.
        generate_random: If True, generate random sample lead data.

    Returns:
        dict[str, Any]: The parsed or generated JSON data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If JSON syntax is invalid.
        ValueError: If parsed JSON is not a dictionary.
    """
    if generate_random:
        return generate_random_lead()

    if raw_json:
        data = json.loads(raw_json)
    elif file_path:
        target_path = Path(file_path)
        if not target_path.is_absolute():
            target_path = (Path.cwd() / target_path).resolve()

        if not target_path.exists():
            raise FileNotFoundError(f"JSON file not found: {target_path}")

        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif DEFAULT_SAMPLE_FILE.exists():
        print(f"[INFO] Using default sample file: {DEFAULT_SAMPLE_FILE}")
        with open(DEFAULT_SAMPLE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raise ValueError(
            "No JSON input provided and default sample file does not exist. "
            "Use --file <path>, --json '<json_str>', or --random."
        )

    if not isinstance(data, dict):
        raise ValueError("JSON content must be a JSON object (dictionary).")

    return data


def create_lead_from_dict(raw_data: dict[str, Any]) -> int:
    """Validate data and create a Lead in Odoo via OdooClient.

    Args:
        raw_data: Dictionary containing lead attributes.

    Returns:
        int: Created Odoo Lead ID.
    """
    # Validate payload using Pydantic schema
    lead = LeadCreate.model_validate(raw_data)
    lead_payload = lead.model_dump(exclude_none=True)

    # Initialize client (loads connection info from secrets/.env)
    client = OdooClient()
    lead_id = client.create_lead(lead_payload)
    return lead_id


def main() -> None:
    """Entry point for CLI execution."""
    parser = argparse.ArgumentParser(
        description="Create an Odoo CRM Lead from a JSON file, raw JSON, or randomly."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f",
        "--file",
        type=str,
        help="Path to JSON file containing lead details.",
    )
    group.add_argument(
        "-j",
        "--json",
        type=str,
        help="Raw JSON string containing lead details.",
    )
    group.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="Generate random sample lead data and create lead directly in Odoo.",
    )

    args = parser.parse_args()

    print("==================================================")
    print("           Odoo Lead Creator (CLI)")
    print("==================================================")

    try:
        raw_data = load_json_data(
            file_path=args.file,
            raw_json=args.json,
            generate_random=args.random,
        )
        if args.random:
            print("[INFO] Generated Random Lead Data successfully.")
        print(f"[INFO] Lead Name : \"{raw_data.get('name', 'N/A')}\"")
        print("[INFO] Connecting to Odoo and creating lead...")

        lead_id = create_lead_from_dict(raw_data)

        print("\n--------------------------------------------------")
        print(" [SUCCESS] Lead created successfully in Odoo!")
        print(f" -> Lead ID       : {lead_id}")
        print(f" -> Name/Title    : {raw_data.get('name')}")
        print(f" -> Contact Name  : {raw_data.get('contact_name', 'N/A')}")
        print(f" -> Phone         : {raw_data.get('phone', 'N/A')}")
        print(f" -> Email         : {raw_data.get('email', 'N/A')}")
        if raw_data.get("event"):
            print(f" -> Event         : {raw_data.get('event')}")
        if raw_data.get("event_location"):
            print(f" -> Location      : {raw_data.get('event_location')}")
        print("--------------------------------------------------")
        sys.exit(0)

    except FileNotFoundError as err:
        print(f"\n[ERROR] File Error: {err}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as err:
        print(f"\n[ERROR] Invalid JSON syntax: {err}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as err:
        print("\n[ERROR] Lead Data Validation Failed:", file=sys.stderr)
        for error in err.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            print(f"  - Field '{loc}': {error['msg']}", file=sys.stderr)
        sys.exit(1)
    except OdooAuthenticationError as err:
        print(f"\n[ERROR] Odoo Authentication Failed: {err}", file=sys.stderr)
        sys.exit(1)
    except OdooConnectionError as err:
        print(f"\n[ERROR] Odoo Connection Failed: {err}", file=sys.stderr)
        sys.exit(1)
    except OdooOperationError as err:
        print(f"\n[ERROR] Odoo Lead Creation Rejected: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"\n[ERROR] Unexpected error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
