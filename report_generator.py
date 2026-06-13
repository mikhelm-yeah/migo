"""Report generation and formatting module."""

import logging
import json
from typing import Dict, List, Any
from tabulate import tabulate
from datetime import datetime
import csv
import os
from config import Config

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates formatted reports for BOM analysis and validation."""

    def __init__(self, output_dir: str = None):
        """Initialize report generator.

        Args:
            output_dir: Directory for saving reports
        """
        self.output_dir = output_dir or Config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_variation_report(
        self, variations: Dict[str, Any], filename: str = None
    ) -> str:
        """Generate variation analysis report.

        Args:
            variations: Variation analysis data
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to generated report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"variation_report_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("BOM VARIATION ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            summary = variations.get("summary", {})
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Color Variations
            if variations.get("color_variations"):
                f.write("COLOR VARIATIONS\n")
                f.write("-" * 80 + "\n")
                self._write_table(
                    f, variations["color_variations"],
                    headers=["SKU 1", "SKU 2", "Part Number", "Color 1", "Color 2"]
                )
                f.write("\n")
            
            # Material Variations
            if variations.get("material_variations"):
                f.write("MATERIAL VARIATIONS\n")
                f.write("-" * 80 + "\n")
                self._write_table(
                    f, variations["material_variations"],
                    headers=["SKU 1", "SKU 2", "Part Number", "Material 1", "Material 2"]
                )
                f.write("\n")
            
            # Structural Differences
            if variations.get("structural_differences"):
                f.write("STRUCTURAL DIFFERENCES\n")
                f.write("-" * 80 + "\n")
                self._write_table(
                    f, variations["structural_differences"],
                    headers=["SKU 1", "SKU 2", "Difference"]
                )
                f.write("\n")
            
            # Missing Components
            if variations.get("missing_components"):
                f.write("MISSING COMPONENTS\n")
                f.write("-" * 80 + "\n")
                for sku, missing in variations["missing_components"].items():
                    f.write(f"{sku}: {', '.join(missing)}\n")
                f.write("\n")
        
        logger.info(f"Variation report generated: {filepath}")
        return filepath

    def generate_data_quality_report(
        self, validation_reports: List[Dict[str, Any]], filename: str = None
    ) -> str:
        """Generate data quality report for multiple products.

        Args:
            validation_reports: List of validation report dictionaries
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to generated report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_quality_report_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("DATA QUALITY REPORT\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Products Analyzed: {len(validation_reports)}\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary table
            summary_data = []
            for report in validation_reports:
                summary_data.append([
                    report["sku"],
                    "✓" if report["valid"] else "✗",
                    report["data_quality_score"],
                    len(report.get("errors", [])),
                    len(report.get("warnings", []))
                ])
            
            f.write("SUMMARY TABLE\n")
            f.write("-" * 80 + "\n")
            table_str = tabulate(
                summary_data,
                headers=["SKU", "Valid", "Quality Score", "Errors", "Warnings"],
                tablefmt="grid"
            )
            f.write(table_str + "\n\n")
            
            # Detailed reports
            f.write("DETAILED REPORTS\n")
            f.write("=" * 80 + "\n\n")
            
            for report in validation_reports:
                f.write(f"Product: {report['sku']}\n")
                f.write("-" * 80 + "\n")
                
                if report["errors"]:
                    f.write("Errors:\n")
                    for error in report["errors"]:
                        f.write(f"  ✗ {error}\n")
                
                if report["warnings"]:
                    f.write("Warnings:\n")
                    for warning in report["warnings"]:
                        f.write(f"  ⚠ {warning}\n")
                
                if report.get("field_issues"):
                    f.write("Field Issues:\n")
                    for field, issues in report["field_issues"].items():
                        for issue in issues:
                            f.write(f"  ⚠ {issue}\n")
                
                f.write(f"Quality Score: {report['data_quality_score']}/100\n")
                f.write("\n")
        
        logger.info(f"Data quality report generated: {filepath}")
        return filepath

    def generate_missing_fields_report(
        self, validation_reports: List[Dict[str, Any]], filename: str = None
    ) -> str:
        """Generate report of missing or empty fields.

        Args:
            validation_reports: List of validation report dictionaries
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to generated report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"missing_fields_report_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("MISSING FIELDS ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            for report in validation_reports:
                f.write(f"Product: {report['sku']}\n")
                f.write("-" * 80 + "\n")
                
                missing_count = len([w for w in report.get("warnings", []) if "Empty" in w])
                
                if missing_count > 0:
                    f.write("Empty Fields:\n")
                    for warning in report["warnings"]:
                        if "Empty" in warning:
                            f.write(f"  • {warning}\n")
                else:
                    f.write("No empty required fields.\n")
                
                f.write("\n")
        
        logger.info(f"Missing fields report generated: {filepath}")
        return filepath

    def _write_table(
        self, file, data: List[Dict], headers: List[str]
    ) -> None:
        """Write table to file.

        Args:
            file: File object
            data: List of dictionaries
            headers: Column headers
        """
        rows = []
        for item in data:
            row = [item.get(h.lower().replace(" ", "_"), "") for h in headers]
            rows.append(row)
        
        table_str = tabulate(rows, headers=headers, tablefmt="grid")
        file.write(table_str + "\n")

    def export_json(
        self, data: Dict[str, Any], filename: str = None
    ) -> str:
        """Export data as JSON.

        Args:
            data: Data to export
            filename: Output filename

        Returns:
            Path to generated file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"JSON export generated: {filepath}")
        return filepath

    def export_csv(
        self, data: List[Dict[str, Any]], filename: str = None
    ) -> str:
        """Export data as CSV.

        Args:
            data: List of dictionaries to export
            filename: Output filename

        Returns:
            Path to generated file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if not data:
            logger.warning("No data to export")
            return filepath
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"CSV export generated: {filepath}")
        return filepath
