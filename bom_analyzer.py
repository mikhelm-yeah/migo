"""BOM analysis and comparison engine."""

import logging
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
from arena_client import ArenaClient

logger = logging.getLogger(__name__)


class BOMAnalyzer:
    """Analyzes and compares bill of materials structures."""

    def __init__(self, arena_client: ArenaClient = None):
        """Initialize BOM analyzer.

        Args:
            arena_client: Arena client instance (creates new if not provided)
        """
        self.client = arena_client or ArenaClient()

    def get_bom_structure(self, sku: str) -> Dict[str, Any]:
        """Extract and normalize BOM structure for a SKU.

        Args:
            sku: Product SKU

        Returns:
            Normalized BOM structure
        """
        logger.info(f"Extracting BOM structure for: {sku}")
        bom_data = self.client.get_bom(sku)
        return self._normalize_bom(bom_data)

    def _normalize_bom(self, bom_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize BOM data structure.

        Args:
            bom_data: Raw BOM data from Arena

        Returns:
            Normalized BOM structure
        """
        components = bom_data.get("components", [])
        normalized = {
            "sku": bom_data.get("sku"),
            "revision": bom_data.get("revision"),
            "components": []
        }
        
        for comp in components:
            normalized["components"].append({
                "part_number": comp.get("part_number"),
                "description": comp.get("description"),
                "quantity": comp.get("quantity"),
                "material": comp.get("material"),
                "color": comp.get("color"),
                "supplier": comp.get("supplier"),
                "unit_cost": comp.get("unit_cost"),
                "notes": comp.get("notes"),
            })
        
        return normalized

    def compare_skus(self, skus: List[str]) -> Dict[str, Any]:
        """Compare BOM structures across multiple SKUs.

        Args:
            skus: List of SKUs to compare

        Returns:
            Comparison report with variations
        """
        logger.info(f"Comparing {len(skus)} SKUs")
        boms = {}
        for sku in skus:
            try:
                boms[sku] = self.get_bom_structure(sku)
            except Exception as e:
                logger.error(f"Failed to fetch BOM for {sku}: {e}")
                boms[sku] = None

        return self._analyze_variations(boms)

    def _analyze_variations(self, boms: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze differences between BOMs.

        Args:
            boms: Dictionary of normalized BOMs

        Returns:
            Variation analysis report
        """
        variations = {
            "identical_skus": [],
            "structural_differences": [],
            "color_variations": [],
            "material_variations": [],
            "supplier_variations": [],
            "cost_variations": [],
            "missing_components": defaultdict(list),
            "summary": {}
        }

        skus = list(boms.keys())
        base_sku = skus[0]
        base_bom = boms[base_sku]
        
        if base_bom is None:
            logger.error("Base BOM not available for comparison")
            return variations

        base_components = {c["part_number"]: c for c in base_bom["components"]}

        for sku in skus[1:]:
            compare_bom = boms[sku]
            if compare_bom is None:
                continue

            compare_components = {c["part_number"]: c for c in compare_bom["components"]}
            
            # Check structural differences
            if len(base_components) != len(compare_components):
                variations["structural_differences"].append({
                    "sku1": base_sku,
                    "sku2": sku,
                    "difference": f"Component count: {len(base_components)} vs {len(compare_components)}"
                })
            
            # Check for component differences
            missing_in_compare = set(base_components.keys()) - set(compare_components.keys())
            missing_in_base = set(compare_components.keys()) - set(base_components.keys())
            
            if missing_in_compare:
                variations["missing_components"][sku] = list(missing_in_compare)
            
            # Check for attribute variations
            for part_num in base_components.keys() & compare_components.keys():
                base_comp = base_components[part_num]
                compare_comp = compare_components[part_num]
                
                # Color variations
                if base_comp.get("color") != compare_comp.get("color"):
                    variations["color_variations"].append({
                        "sku1": base_sku,
                        "sku2": sku,
                        "part_number": part_num,
                        "color1": base_comp.get("color"),
                        "color2": compare_comp.get("color")
                    })
                
                # Material variations
                if base_comp.get("material") != compare_comp.get("material"):
                    variations["material_variations"].append({
                        "sku1": base_sku,
                        "sku2": sku,
                        "part_number": part_num,
                        "material1": base_comp.get("material"),
                        "material2": compare_comp.get("material")
                    })
                
                # Cost variations
                if base_comp.get("unit_cost") != compare_comp.get("unit_cost"):
                    variations["cost_variations"].append({
                        "sku1": base_sku,
                        "sku2": sku,
                        "part_number": part_num,
                        "cost1": base_comp.get("unit_cost"),
                        "cost2": compare_comp.get("unit_cost")
                    })
        
        # Generate summary
        variations["summary"] = {
            "skus_compared": len(skus),
            "color_variations_found": len(variations["color_variations"]),
            "material_variations_found": len(variations["material_variations"]),
            "structural_differences_found": len(variations["structural_differences"]),
            "cost_variations_found": len(variations["cost_variations"])
        }
        
        return variations

    def categorize_changes(self, variations: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize changes as intentional or inadvertent.

        Args:
            variations: Variation analysis report

        Returns:
            Categorized changes
        """
        categorized = {
            "likely_intentional": [],  # e.g., color variations, cost reductions
            "likely_inadvertent": [],  # e.g., missing components, structural changes
            "requires_review": []      # e.g., material changes
        }
        
        # Color variations are often intentional
        categorized["likely_intentional"].extend(variations.get("color_variations", []))
        
        # Structural differences and missing components are likely inadvertent
        categorized["likely_inadvertent"].extend(variations.get("structural_differences", []))
        for missing_list in variations.get("missing_components", {}).values():
            categorized["likely_inadvertent"].extend(missing_list)
        
        # Material and cost changes need review
        categorized["requires_review"].extend(variations.get("material_variations", []))
        categorized["requires_review"].extend(variations.get("cost_variations", []))
        
        return categorized
