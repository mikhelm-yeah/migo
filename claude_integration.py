"""Claude API integration for AI-powered analysis."""

import logging
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from config import Config

logger = logging.getLogger(__name__)


class ClaudeIntegration:
    """Integrates Claude AI for intelligent analysis of BOM data."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize Claude integration.

        Args:
            api_key: Anthropic API key (defaults to config)
            model: Claude model ID (defaults to config)
        """
        self.api_key = api_key or Config.CLAUDE_API_KEY
        self.model = model or Config.CLAUDE_MODEL
        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history = []

    def analyze_variations(
        self, variations: Dict[str, Any], context: str = ""
    ) -> str:
        """Analyze BOM variations using Claude.

        Args:
            variations: Variation analysis data
            context: Additional context about the products

        Returns:
            Claude's analysis and recommendations
        """
        logger.info("Analyzing variations with Claude")
        
        prompt = f"""
Analyze the following bill of materials variations between product SKUs and provide insights:

{self._format_variations(variations)}

Context: {context or 'Standard product family'}

Please provide:
1. Summary of variations found
2. Assessment of which variations appear intentional vs. inadvertent
3. Risk assessment for any structural or material changes
4. Recommendations for verification or changes
"""
        
        return self._call_claude(prompt)

    def analyze_data_quality(
        self, validation_reports: List[Dict[str, Any]]
    ) -> str:
        """Analyze data quality issues using Claude.

        Args:
            validation_reports: List of validation reports

        Returns:
            Claude's analysis and recommendations
        """
        logger.info("Analyzing data quality with Claude")
        
        prompt = f"""
Review the following data quality validation reports and provide insights:

{self._format_validation_reports(validation_reports)}

Please provide:
1. High-level summary of data quality status
2. Most critical issues to address
3. Patterns in errors or missing fields
4. Recommended remediation steps
5. Priority ranking of issues to fix
"""
        
        return self._call_claude(prompt)

    def suggest_error_fixes(
        self, error_messages: List[str], product_context: Dict[str, Any]
    ) -> str:
        """Suggest fixes for detected errors using Claude.

        Args:
            error_messages: List of error descriptions
            product_context: Context about the product

        Returns:
            Claude's suggestions for fixing errors
        """
        logger.info("Getting error fix suggestions from Claude")
        
        prompt = f"""
A product has the following data validation errors:

Product: {product_context.get('sku', 'Unknown')}
Category: {product_context.get('category', 'Unknown')}

Errors:
{chr(10).join(f'- {err}' for err in error_messages)}

Please suggest:
1. Specific corrections for each error
2. Validation rules that should apply
3. Any assumptions or additional information needed
"""
        
        return self._call_claude(prompt)

    def interactive_bom_query(self, bom_data: Dict[str, Any]) -> str:
        """Start interactive conversation about BOM data.

        Args:
            bom_data: BOM structure to discuss

        Returns:
            Initial Claude response
        """
        logger.info("Starting interactive BOM query")
        
        system_message = """
You are an expert in product lifecycle management and bill of materials analysis.
You help users understand product structures, identify variations, and improve data quality.
Provide detailed, actionable insights based on the data provided.
"""
        
        initial_prompt = f"""
I'm providing you with a bill of materials structure to analyze. 
Please familiarize yourself with it and ask clarifying questions if needed.

BOM Data:
{self._format_bom(bom_data)}

How would you like to proceed? You can:
1. Analyze this BOM's structure
2. Compare it with other products
3. Identify potential data quality issues
4. Suggest improvements
"""
        
        self.conversation_history = [
            {"role": "user", "content": initial_prompt}
        ]
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=Config.CLAUDE_MAX_TOKENS,
            system=system_message,
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_message}
        )
        
        return assistant_message

    def continue_conversation(self, user_input: str) -> str:
        """Continue interactive conversation.

        Args:
            user_input: User's message

        Returns:
            Claude's response
        """
        logger.info("Continuing conversation with Claude")
        
        self.conversation_history.append(
            {"role": "user", "content": user_input}
        )
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=Config.CLAUDE_MAX_TOKENS,
            system="You are an expert in product lifecycle management and bill of materials analysis.",
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_message}
        )
        
        return assistant_message

    def _call_claude(self, prompt: str) -> str:
        """Call Claude API with a prompt.

        Args:
            prompt: Prompt to send to Claude

        Returns:
            Claude's response
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=Config.CLAUDE_MAX_TOKENS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def _format_variations(self, variations: Dict[str, Any]) -> str:
        """Format variations for Claude prompt.

        Args:
            variations: Variation analysis data

        Returns:
            Formatted string
        """
        formatted = "\n"
        
        if variations.get("summary"):
            formatted += "SUMMARY:\n"
            for key, value in variations["summary"].items():
                formatted += f"  {key}: {value}\n"
        
        if variations.get("color_variations"):
            formatted += f"\nColor Variations ({len(variations['color_variations'])} found)\n"
            for var in variations["color_variations"][:5]:  # Show first 5
                formatted += f"  {var['sku1']} vs {var['sku2']}: Part {var['part_number']} {var['color1']} → {var['color2']}\n"
        
        if variations.get("material_variations"):
            formatted += f"\nMaterial Variations ({len(variations['material_variations'])} found)\n"
            for var in variations["material_variations"][:5]:
                formatted += f"  {var['sku1']} vs {var['sku2']}: Part {var['part_number']} {var['material1']} → {var['material2']}\n"
        
        return formatted

    def _format_validation_reports(self, reports: List[Dict[str, Any]]) -> str:
        """Format validation reports for Claude prompt.

        Args:
            reports: List of validation reports

        Returns:
            Formatted string
        """
        formatted = "\n"
        error_count = 0
        warning_count = 0
        
        for report in reports:
            formatted += f"SKU: {report['sku']} | Quality Score: {report['data_quality_score']}/100\n"
            error_count += len(report.get("errors", []))
            warning_count += len(report.get("warnings", []))
            
            if report.get("errors"):
                for error in report["errors"][:3]:
                    formatted += f"  ✗ {error}\n"
        
        formatted += f"\nTotal Issues: {error_count} errors, {warning_count} warnings\n"
        return formatted

    def _format_bom(self, bom: Dict[str, Any]) -> str:
        """Format BOM for Claude prompt.

        Args:
            bom: BOM structure

        Returns:
            Formatted string
        """
        formatted = f"\nSKU: {bom.get('sku')}\n"
        formatted += f"Revision: {bom.get('revision')}\n"
        formatted += f"Total Components: {len(bom.get('components', []))}\n\n"
        
        for idx, comp in enumerate(bom.get("components", [])[:10], 1):
            formatted += f"{idx}. {comp.get('part_number')} - {comp.get('description')}\n"
            formatted += f"   Qty: {comp.get('quantity')} | Material: {comp.get('material')}\n"
        
        if len(bom.get("components", [])) > 10:
            formatted += f"\n... and {len(bom['components']) - 10} more components\n"
        
        return formatted
