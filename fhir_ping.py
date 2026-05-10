"""
fhir_ping.py

Simple command-line FHIR application to verify that a FHIR server
is reachable and responding.

Uses:
- fhir_client.py
- GET /metadata
"""

from fhir_client import FHIR_BASE_URL, get_resource

def main() -> None:
    print("\nFHIR Server Ping")
    print("=" * 64)
    print(f"Connecting to: {FHIR_BASE_URL}\n")

    print("Pinging FHIR server using GET /metadata")

    metadata = get_resource("metadata", "")

    fhir_version = metadata.get("fhirVersion", "unknown")
    print(f"FHIR Version: {fhir_version}")

    software = metadata.get("software", {})
    software_name = software.get("name", "unknown")
    software_version = software.get("version", "")

    if software_version:
        print(f"Software Version: {software_version}")
    if software_name:
        print(f"Software: {software_name}")
    
    rest = metadata.get("rest", [])
    if rest:
        resources = rest[0].get("resource", [])
        types = [r.get("type") for r in resources if "type" in r]

        for resource_type in types[:10]:
            print(f" - {resource_type}")

        if len(types) > 10:
            print(" - ...")
    else:
        print(" No REST metadata found")

    print("\nPing successful")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\n Ping failed")
        print(f"Error: {exc}")