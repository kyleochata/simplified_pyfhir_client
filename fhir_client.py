from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional

import requests

from dotenv import load_dotenv
import os

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

load_dotenv("./.env")

base_url = os.getenv("FHIR_BASE_URL", "")
username = os.getenv("USERNAME", "")
password = os.getenv("PASSWORD", "")

FHIR_BASE_URL = base_url

if FHIR_BASE_URL == "":
    print(f"FHIR BASE URL is {FHIR_BASE_URL}")

USERNAME = username
if USERNAME == "":
    print(f"Username is blank: {USERNAME}")

PASSWORD = password
if PASSWORD == "":
    print(f"Password is empty: {PASSWORD}")

print (f"{ FHIR_BASE_URL}, {USERNAME}, {PASSWORD}")


def _basic_auth_header(username: str, password: str) -> str:
    token = f"{username}:{password}".encode("utf-8")
    return "Basic" + base64.b64encode(token).decode("ascii")

HEADERS = {
    "Authorization": _basic_auth_header(USERNAME, PASSWORD),
    "Accept": "*/*",
    "Content-Type": "application/fhir+json",
    "Prefer": "return=representation",
}


def _full_url(path: str) -> str:
    """
        Safely joins a FHIR base URL and a relative path
    """
    return f"{FHIR_BASE_URL.rstrip('/')}/{path.lstrip('/')}"

def _get(path: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    url = _full_url(path)
    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=15,
    )

    if not response.ok:
        raise RuntimeError(_format_error(response))
    
    try:
        return response.json()
    except ValueError:
        raise RuntimeError("FHIR returned with non-JSON response")

def _format_error(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return f"HTTP {response.status_code}: {response.text}"
    
    if isinstance(body, dict) and body.get("resourceType") == "OperationOutcome":
        issues = body.get("issue", [])
        if issues:
            issue = issues[0]
            details = issue.get("details", {}).get("text")
            diagnostics = issue.get("diagnostics")
            return f"FHIR error: {details or diagnostics or 'OperationOutcome'}"
    return f"HTTP {response.status_code}: {body}"


# ---------------------------------------------------------------------
# Public FHIR functions 
# ---------------------------------------------------------------------

def get_resource(resource_type: str, resource_id: str) -> Dict[str, Any]:
    """
    GET /<resource_type>/<id>
    """
    return _get(f"{resource_type}/{resource_id}")

def search(resource_type: str, **params: str) -> Dict[str, Any]:
    """
    GET /<resource_type>?param=value&...
    """
    return _get(resource_type, params=params)

def extract_resources(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract resource objects from a Bundle
    """
    entries = bundle.get("entry", [])
    resources: List[Dict[str,Any]] = []
    for entry in entries:
        resource = entry.get("resource")
        if isinstance(resource, dict):
            resources.append(resource)
    return resources


# ---------------------------------------------------------------------
# Convenience helpers (human-friendly)
# ---------------------------------------------------------------------

def human_name(patient: Dict[str, Any]) -> str:
    names = patient.get("name", [])
    if not names:
        return "No name"
    
    name = names[0]
    if "text" in name:
        return name["text"]
    
    given = " ".join(name.get("given", []))
    family = name.get("family", "")

    return f"{given} {family}".strip()

def summarize_patient(patient: Dict[str, Any]) -> Dict[str, str]:
    return {
        "id": patient.get("id", ""),
        "name": human_name(patient),
        "gender": patient.get("gender", ""),
        "birthDate": patient.get("birthDate", ""),
    }