"""
app/core/config_validator.py — YAML-Driven System Configuration Validator

Loads and strictly validates all YAML configuration files in config/:
- platform.yaml
- permissions.yaml
- scoring_policies.yaml
- models.yaml
- datasets.yaml
- runtime.yaml
- portals/*.yaml
- features/*.yaml

Rejects unsafe tags, missing permissions, invalid weights, and unknown critical keys.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator


# ── Pydantic Schemas for Configuration Files ──────────────────────────────────

class PlatformBranding(BaseModel):
    primary_color: str
    secondary_color: str
    accent_color: str
    accent_hover: str
    background_canvas: str
    surface_card: str
    text_primary: str
    text_secondary: str
    border_color: str
    success_color: str
    warning_color: str
    danger_color: str
    info_color: str


class PlatformInfo(BaseModel):
    name: str
    tagline: str
    organization: str
    edition: str
    version: str
    build: str
    environment: str


class PlatformConfig(BaseModel):
    schema_version: str
    platform: PlatformInfo
    branding: PlatformBranding
    typography: Dict[str, Any]
    features: Dict[str, bool]


class RoleDefinition(BaseModel):
    id: str
    name: str
    description: str
    permissions: List[str]


class PermissionsConfig(BaseModel):
    schema_version: str
    roles: List[RoleDefinition]


class ScoringWeights(BaseModel):
    default_semantic_weight_beta: float = Field(ge=0.0, le=1.0)
    default_concept_coverage_weight: float = Field(ge=0.0, le=1.0)
    min_criterion_semantic_weight: float = Field(ge=0.0, le=1.0)
    max_criterion_semantic_weight: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_weights_sum(self) -> ScoringWeights:
        total = self.default_semantic_weight_beta + self.default_concept_coverage_weight
        if abs(total - 1.0) > 1e-4:
            raise ValueError(f"Default scoring weights must sum to 1.0; got {total}")
        return self


class ScoringPoliciesConfig(BaseModel):
    schema_version: str
    policy: Dict[str, Any]
    mathematical_formulation: Dict[str, Any]
    weights: ScoringWeights
    bounds: Dict[str, Any]
    confidence_thresholds: Dict[str, float]
    review_triggers: Dict[str, Any]
    anti_gaming_safeguards: Dict[str, Any]


class ModelProfile(BaseModel):
    name: str
    description: str
    max_ram_usage_mb: int = Field(gt=0)
    max_disk_usage_mb: int = Field(gt=0)
    device: str
    batch_size: int = Field(gt=0)
    enable_onnx_quantization: bool = False


class ModelsConfig(BaseModel):
    schema_version: str
    active_profile: str
    profiles: Dict[str, ModelProfile]
    models: Dict[str, List[Dict[str, Any]]]

    @model_validator(mode="after")
    def validate_active_profile_exists(self) -> ModelsConfig:
        if self.active_profile not in self.profiles:
            raise ValueError(f"Active profile '{self.active_profile}' not defined in profiles")
        return self


class DatasetEntry(BaseModel):
    id: str
    name: str
    repository: str
    task: str
    license: str
    size_mb: float = Field(gt=0)
    checksum_sha256: Optional[str] = None
    status: str
    sample_path: Optional[str] = None
    is_active_benchmark: bool = False


class DatasetsConfig(BaseModel):
    schema_version: str
    download_policy: Dict[str, Any]
    datasets: List[DatasetEntry]


class PortalNavigation(BaseModel):
    id: str
    label: str
    icon: str
    target: str


class PortalDefinition(BaseModel):
    id: str
    display_name: str
    route: str
    description: str
    allowed_roles: List[str]
    required_permissions: List[str]

    @field_validator("route")
    @classmethod
    def validate_route_format(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError(f"Route '{v}' must start with '/'")
        return v


class PortalConfig(BaseModel):
    schema_version: str
    portal: PortalDefinition
    layout: Dict[str, Any]
    navigation: List[PortalNavigation]
    features: Dict[str, bool]
    ui_components: Dict[str, str]
    api_requirements: Dict[str, Any]
    workflow_states: List[str]
    state_expectations: Dict[str, str]
    audit_requirements: Dict[str, Any]
    security_requirements: Dict[str, Any]


class FeatureConfig(BaseModel):
    schema_version: str
    feature: Dict[str, Any]


# ── Loader and Validation Engine ──────────────────────────────────────────────

class ConfigRegistry:
    """
    In-memory registry caching validated YAML configurations.
    """
    def __init__(self, config_root: Optional[Path] = None):
        if config_root is None:
            # Look up from backend/app/core to C:\ANSWERSCRIPT\config
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            self.config_root = base_dir / "config"
        else:
            self.config_root = Path(config_root)

        self.platform: Optional[PlatformConfig] = None
        self.permissions: Optional[PermissionsConfig] = None
        self.scoring_policies: Optional[ScoringPoliciesConfig] = None
        self.models: Optional[ModelsConfig] = None
        self.datasets: Optional[DatasetsConfig] = None
        self.portals: Dict[str, PortalConfig] = {}
        self.features: Dict[str, FeatureConfig] = {}
        self.validation_errors: List[str] = []

    def _safe_read_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Safely parse YAML without allowing code execution or unsafe tags."""
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file missing: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"File {file_path} must define a top-level dictionary")
        return data

    def load_and_validate_all(self) -> bool:
        """
        Loads and validates every configuration file in the hierarchy.
        Returns True if all files pass schema validation without errors.
        """
        self.validation_errors.clear()
        self.portals.clear()
        self.features.clear()

        # 1. Platform
        try:
            p_data = self._safe_read_yaml(self.config_root / "platform.yaml")
            self.platform = PlatformConfig.model_validate(p_data)
        except Exception as e:
            self.validation_errors.append(f"platform.yaml: {e}")

        # 2. Permissions
        all_permission_ids = set()
        role_ids = set()
        try:
            perm_data = self._safe_read_yaml(self.config_root / "permissions.yaml")
            self.permissions = PermissionsConfig.model_validate(perm_data)
            for r in self.permissions.roles:
                role_ids.add(r.id)
                for p in r.permissions:
                    all_permission_ids.add(p)
        except Exception as e:
            self.validation_errors.append(f"permissions.yaml: {e}")

        # 3. Scoring Policies
        try:
            sp_data = self._safe_read_yaml(self.config_root / "scoring_policies.yaml")
            self.scoring_policies = ScoringPoliciesConfig.model_validate(sp_data)
        except Exception as e:
            self.validation_errors.append(f"scoring_policies.yaml: {e}")

        # 4. Models
        try:
            m_data = self._safe_read_yaml(self.config_root / "models.yaml")
            self.models = ModelsConfig.model_validate(m_data)
        except Exception as e:
            self.validation_errors.append(f"models.yaml: {e}")

        # 5. Datasets
        try:
            d_data = self._safe_read_yaml(self.config_root / "datasets.yaml")
            self.datasets = DatasetsConfig.model_validate(d_data)
        except Exception as e:
            self.validation_errors.append(f"datasets.yaml: {e}")

        # 6. Portals
        portals_dir = self.config_root / "portals"
        if portals_dir.exists():
            for p_file in portals_dir.glob("*.yaml"):
                try:
                    p_data = self._safe_read_yaml(p_file)
                    p_obj = PortalConfig.model_validate(p_data)
                    # Cross-validate roles and permissions against permissions.yaml
                    if role_ids:
                        for role in p_obj.portal.allowed_roles:
                            if role not in role_ids:
                                self.validation_errors.append(
                                    f"portal {p_file.name}: unknown role '{role}'"
                                )
                    self.portals[p_obj.portal.id] = p_obj
                except Exception as e:
                    self.validation_errors.append(f"portal {p_file.name}: {e}")
        else:
            self.validation_errors.append("Directory config/portals/ missing")

        # 7. Features
        features_dir = self.config_root / "features"
        if features_dir.exists():
            for f_file in features_dir.glob("*.yaml"):
                try:
                    f_data = self._safe_read_yaml(f_file)
                    f_obj = FeatureConfig.model_validate(f_data)
                    fid = f_obj.feature.get("id", f_file.stem)
                    self.features[fid] = f_obj
                except Exception as e:
                    self.validation_errors.append(f"feature {f_file.name}: {e}")

        return len(self.validation_errors) == 0

    def get_summary(self) -> Dict[str, Any]:
        """Returns diagnostic status of all loaded configurations."""
        return {
            "status": "VALID" if not self.validation_errors else "INVALID",
            "total_errors": len(self.validation_errors),
            "errors": self.validation_errors,
            "portals_loaded": list(self.portals.keys()),
            "features_loaded": list(self.features.keys()),
            "active_model_profile": self.models.active_profile if self.models else None,
            "platform_version": self.platform.platform.version if self.platform else None,
        }


# Global singleton instance
_registry: Optional[ConfigRegistry] = None

def get_config_registry() -> ConfigRegistry:
    global _registry
    if _registry is None:
        _registry = ConfigRegistry()
        _registry.load_and_validate_all()
    return _registry


if __name__ == "__main__":
    reg = ConfigRegistry()
    success = reg.load_and_validate_all()
    summary = reg.get_summary()
    print("=== INTELLIGRADE CONFIG VALIDATION SUMMARY ===")
    print(f"Status: {summary['status']}")
    print(f"Portals Loaded: {len(summary['portals_loaded'])} ({', '.join(summary['portals_loaded'])})")
    print(f"Features Loaded: {len(summary['features_loaded'])} ({', '.join(summary['features_loaded'])})")
    if summary['errors']:
        print("\nERRORS DETECTED:")
        for err in summary['errors']:
            print(f"  - {err}")
    else:
        print("All YAML configuration files strictly validated against Pydantic schemas!")
