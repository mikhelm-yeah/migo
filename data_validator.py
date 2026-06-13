"""Data validation and quality checking module."""

import re
import logging
from typing import Dict, List, Any, Tuple
from config import Config
from arena_client import ArenaClient

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates product data quality and completeness."""

    def __init__(self):
        """Initialize data validator."""
        self.required_fields = Config.REQUIRED_FIELDS
        self.material_regex = Config.MATERIAL_FIELD_REGEX

    def validate_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single product record.

        Args:
            product: Product data dictionary

        Returns:
            Validation report
        """
        report = {
            "sku": product.get("sku"),
            "valid": True,
            "errors": [],
            "warnings": [],
            "field_issues": {},
            "data_quality_score": 100
        }
        
        # Check required fields
        missing_fields = self._check_required_fields(product)
        if missing_fields:
            report["valid"] = False
            report["errors"].extend(missing_fields)
        
        # Check empty fields
        empty_fields = self._check_empty_fields(product)
        if empty_fields:
            report["warnings"].extend(empty_fields)
        
        # Validate material fields
        material_issues = self._validate_material_fields(product)
        if material_issues:
            report["valid"] = False
            report["field_issues"].update(material_issues)
        
        # Validate syntax
        syntax_issues = self._validate_syntax(product)
        if syntax_issues:
            report["errors"].extend(syntax_issues)
        
        # Calculate data quality score
        report["data_quality_score"] = self._calculate_quality_score(report)
        
        return report

    def validate_bom(self, sku: str, bom: Dict[str, Any]) -> Dict[str, Any]:
        """Validate bill of materials completeness and consistency.

        Args:
            sku: Product SKU
            bom: BOM data

        Returns:
            BOM validation report
        """
        report = {
            "sku": sku,
            "total_components": len(bom.get("components", [])),
            "valid": True,
            "component_issues": [],
            "missing_fields_by_component": {}
        }
        
        required_component_fields = ["part_number", "quantity", "material"]
        
        for idx, component in enumerate(bom.get("components", [])):
            component_errors = []
            missing_fields = [
                field for field in required_component_fields
                if field not in component or not component[field]
            ]
            
            if missing_fields:
                report["missing_fields_by_component"][idx] = missing_fields
                report["valid"] = False
            
            # Validate quantity
            if not self._is_valid_quantity(component.get("quantity")):
                component_errors.append(f"Invalid quantity: {component.get('quantity')}")
                report["valid"] = False
            
            # Validate material syntax
            if not self._is_valid_material(component.get("material")):
                component_errors.append(f"Invalid material format: {component.get('material')}")
                report["valid"] = False
            
            if component_errors:
                report["component_issues"].append({
                    "component_index": idx,
                    "part_number": component.get("part_number"),
                    "issues": component_errors
                })
        
        return report

    def _check_required_fields(self, product: Dict[str, Any]) -> List[str]:
        """Check for missing required fields.

        Args:
            product: Product data

        Returns:
            List of missing field errors
        """
        errors = []
        for field in self.required_fields:
            if field not in product:
                errors.append(f"Missing required field: {field}")
        return errors

    def _check_empty_fields(self, product: Dict[str, Any]) -> List[str]:
        """Check for empty required fields.

        Args:
            product: Product data

        Returns:
            List of empty field warnings
        """
        warnings = []
        for field in self.required_fields:
            if field in product and not product[field]:
                warnings.append(f"Empty required field: {field}")
        return warnings

    def _validate_material_fields(self, product: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate material-related fields against regex patterns.

        Args:
            product: Product data

        Returns:
            Dictionary of field validation errors
        """
        issues = {}
        
        for field, pattern in self.material_regex.items():
            if field not in product:
                continue
            
            value = product[field]
            if not value:
                continue
            
            if not re.match(pattern, str(value)):
                if field not in issues:
                    issues[field] = []
                issues[field].append(
                    f"Field '{field}' does not match expected format: {pattern}"
                )
        
        return issues

    def _validate_syntax(self, product: Dict[str, Any]) -> List[str]:
        """Validate data syntax for common fields.

        Args:
            product: Product data

        Returns:
            List of syntax errors
        """
        errors = []
        
        # Validate SKU format (example: alphanumeric, no spaces)
        if "sku" in product:
            if not re.match(r"^[A-Z0-9-]+$", str(product["sku"])):
                errors.append(f"Invalid SKU format: {product['sku']}")
        
        # Validate status field
        if "status" in product:
            valid_statuses = ["active", "inactive", "deprecated", "draft"]
            if product["status"] not in valid_statuses:
                errors.append(f"Invalid status: {product['status']}")
        
        return errors

    def _is_valid_quantity(self, quantity: Any) -> bool:
        """Check if quantity is valid.

        Args:
            quantity: Quantity value

        Returns:
            True if valid, False otherwise
        """
        try:
            q = float(quantity)
            return q > 0
        except (TypeError, ValueError):
            return False

    def _is_valid_material(self, material: Any) -> bool:
        """Check if material field is valid.

        Args:
            material: Material value

        Returns:
            True if valid, False otherwise
        """
        if not material:
            return False
        material_str = str(material).strip()
        return len(material_str) > 0 and not material_str.isspace()

    def _calculate_quality_score(self, report: Dict[str, Any]) -> int:
        """Calculate overall data quality score.

        Args:
            report: Validation report

        Returns:
            Quality score (0-100)
        """
        penalties = 0
        penalties += len(report["errors"]) * 25
        penalties += len(report["warnings"]) * 5
        
        score = max(0, 100 - penalties)
        return score

    def print_report(self, report: Dict[str, Any]):
        """Print validation report.

        Args:
            report: Validation report dictionary
        """
        from tabulate import tabulate
        
        print(f"\n=== Validation Report: {report['sku']} ===")
        print(f"Valid: {report['valid']}")
        print(f"Data Quality Score: {report['data_quality_score']}/100")
        
        if report["errors"]:
            print("\nErrors:")
            for error in report["errors"]:
                print(f"  ✗ {error}")
        
        if report["warnings"]:
            print("\nWarnings:")
            for warning in report["warnings"]:
                print(f"  ⚠ {warning}")
        
        if report["field_issues"]:
            print("\nField Issues:")
            for field, issues in report["field_issues"].items():
                for issue in issues:
                    print(f"  ⚠ {issue}")
