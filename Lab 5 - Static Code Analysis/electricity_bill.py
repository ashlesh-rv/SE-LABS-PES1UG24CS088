
"""Calculate electricity bills and save the results to JSON."""

import http.client
import ipaddress
import json

from defusedxml import ElementTree as ET


SLABS = [(100, 3.5), (200, 5.0), (300, 6.5)]
HIGH_RATE = 8.0
FIXED_CHARGE = 75
DEFAULT_TAX_RATE = 0.05
METER_XML = (
    "<meters>"
    "<meter id='M1' prev='1200' curr='1350'/>"
    "<meter id='M2' prev='5000' curr='5420'/>"
    "<meter id='M3' prev='800' curr='760'/>"
    "</meters>"
)


def read_meters(xml_text):
    """Read meter IDs and readings from an XML document."""
    root = ET.fromstring(xml_text)
    return [
        (meter.get("id"), int(meter.get("prev")), int(meter.get("curr")))
        for meter in root.findall("meter")
    ]


def calculate_units(previous, current):
    """Calculate consumed units from two meter readings."""
    if current < previous:
        print("Warning: meter reading went backwards")
        return 0
    return current - previous


def energy_charge(units):
    """Calculate the electricity charge using tariff slabs."""
    charge = 0
    lower = 0
    remaining = units

    for limit, rate in SLABS:
        slab_units = min(remaining, limit - lower)
        if slab_units > 0:
            charge += slab_units * rate
            remaining -= slab_units
        lower = limit

    return charge + remaining * HIGH_RATE


def generate_bill(meter_id, units, tax_rate=DEFAULT_TAX_RATE, extras=None):
    """Generate an electricity bill and return its details."""
    if extras is None:
        extras = {}

    amount = energy_charge(units) + FIXED_CHARGE + sum(extras.values())
    bill = {
        "meter": meter_id,
        "units": units,
        "amount": round(amount * (1 + tax_rate), 2),
    }
    return bill


def average_bill(bills):
    """Calculate the average amount of the supplied bills."""
    if not bills:
        return 0
    return round(sum(bill["amount"] for bill in bills) / len(bills), 2)


def save_bills(bills, file_name="bills.json"):
    """Save electricity bills to a UTF-8 JSON file."""
    with open(file_name, "w", encoding="utf-8") as output_file:
        json.dump(bills, output_file, indent=2)


def sync_meter(meter_ip):
    """Read a meter using an IP address without invoking a shell."""
    address = ipaddress.ip_address(meter_ip)
    connection = http.client.HTTPConnection(str(address), timeout=5)

    try:
        connection.request("GET", "/reading")
        response = connection.getresponse()

        if response.status != 200:
            raise OSError(f"Meter returned HTTP status {response.status}")

        return response.read().decode("utf-8")
    finally:
        connection.close()


def main():
    """Calculate, display, and save the demonstration electricity bills."""
    bills = []

    for meter_id, previous, current in read_meters(METER_XML):
        units = calculate_units(previous, current)
        bills.append(generate_bill(meter_id, units))

    bills.append(generate_bill("M4", 50, extras={"late_fee": 25}))

    for bill in bills:
        print(
            bill["meter"],
            "used",
            bill["units"],
            "units, bill Rs.",
            bill["amount"],
        )

    highest = max(bills, key=lambda bill: bill["amount"])
    print("Highest bill:", highest["meter"])
    print("Average bill:", average_bill(bills))

    total = sum(bill["amount"] for bill in bills)
    print("Total billed:", round(total, 2))

    save_bills(bills)
    print("Saved", len(bills), "bills to bills.json")


if __name__ == "__main__":
    main()
