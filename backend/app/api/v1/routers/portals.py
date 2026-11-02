"""
app/api/v1/routers/portals.py — Multi-Portal Dynamic Configuration Endpoints

Exposes validated YAML configuration for all 10 role-specific portals to the frontend.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Any, Dict, List

from app.core.config_validator import get_config_registry

router = APIRouter(prefix="/portals", tags=["Portals Configuration"])


@router.get("", response_model=Dict[str, Any])
async def list_all_portals() -> Dict[str, Any]:
    """
    Returns the complete registry of all 10 role-specific portals
    and global platform branding tokens.
    """
    reg = get_config_registry()
    portals_list = []
    for pid, p in reg.portals.items():
        portals_list.append({
            "id": p.portal.id,
            "display_name": p.portal.display_name,
            "route": p.portal.route,
            "description": p.portal.description,
            "allowed_roles": p.portal.allowed_roles,
            "required_permissions": p.portal.required_permissions,
            "layout": p.layout,
            "navigation": [n.model_dump() for n in p.navigation],
            "features": p.features,
            "workflow_states": p.workflow_states,
        })

    branding = reg.platform.branding.model_dump() if reg.platform else {}
    platform_info = reg.platform.platform.model_dump() if reg.platform else {}

    return {
        "platform": platform_info,
        "branding": branding,
        "total_portals": len(portals_list),
        "portals": portals_list,
    }


@router.get("/{portal_id}", response_model=Dict[str, Any])
async def get_portal_details(portal_id: str) -> Dict[str, Any]:
    """
    Returns granular YAML configuration for a specific portal including UI components,
    api requirements, state expectations, and audit requirements.
    """
    reg = get_config_registry()
    p = reg.portals.get(portal_id)
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portal '{portal_id}' not found in registry"
        )
    return p.model_dump()


@router.get("/validation/status", response_model=Dict[str, Any])
async def get_config_validation_status() -> Dict[str, Any]:
    """Returns real-time Pydantic validation status for all YAML configurations."""
    reg = get_config_registry()
    return reg.get_summary()
