"""Main CLI entry point for MIGO."""

import argparse
import logging
from arena_client import ArenaClient
from bom_analyzer import BOMAnalyzer
from data_validator import DataValidator
from report_generator import ReportGenerator
from claude_integration import ClaudeIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def compare_skus(args):
    """Compare BOMs across multiple SKUs."""
    logger.info(f"Comparing SKUs: {args.skus}")
    
    analyzer = BOMAnalyzer()
    variations = analyzer.compare_skus(args.skus)
    
    # Generate report
    report_gen = ReportGenerator()
    report_path = report_gen.generate_variation_report(variations)
    print(f"Report generated: {report_path}")
    
    # Optionally use Claude for analysis
    if args.claude:
        claude = ClaudeIntegration()
        analysis = claude.analyze_variations(variations)
        print("\n=== Claude Analysis ===")
        print(analysis)


def validate_product(args):
    """Validate a single product's data quality."""
    logger.info(f"Validating product: {args.sku}")
    
    arena = ArenaClient()
    product = arena.get_product(args.sku)
    
    validator = DataValidator()
    report = validator.validate_product(product)
    validator.print_report(report)


def validate_products(args):
    """Validate multiple products."""
    logger.info(f"Validating {len(args.skus)} products")
    
    arena = ArenaClient()
    validator = DataValidator()
    reports = []
    
    for sku in args.skus:
        try:
            product = arena.get_product(sku)
            report = validator.validate_product(product)
            reports.append(report)
        except Exception as e:
            logger.error(f"Failed to validate {sku}: {e}")
    
    # Generate report
    report_gen = ReportGenerator()
    report_path = report_gen.generate_data_quality_report(reports)
    print(f"Report generated: {report_path}")
    
    # Optionally use Claude for analysis
    if args.claude:
        claude = ClaudeIntegration()
        analysis = claude.analyze_data_quality(reports)
        print("\n=== Claude Analysis ===")
        print(analysis)


def interactive_mode(args):
    """Enter interactive mode with Claude."""
    arena = ArenaClient()
    bom_data = arena.get_bom(args.sku)
    
    claude = ClaudeIntegration()
    print("Starting interactive BOM analysis...\n")
    print(claude.interactive_bom_query(bom_data))
    
    # Continue conversation
    while True:
        user_input = input("\nYour query: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Exiting...")
            break
        response = claude.continue_conversation(user_input)
        print(f"\nClaude: {response}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MIGO - Arena PLM to Claude Integration"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Compare SKUs
    compare_parser = subparsers.add_parser(
        "compare", help="Compare BOMs across multiple SKUs"
    )
    compare_parser.add_argument(
        "skus", nargs="+", help="SKUs to compare"
    )
    compare_parser.add_argument(
        "--claude", action="store_true", help="Use Claude for analysis"
    )
    compare_parser.set_defaults(func=compare_skus)
    
    # Validate single product
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a single product's data"
    )
    validate_parser.add_argument("sku", help="SKU to validate")
    validate_parser.set_defaults(func=validate_product)
    
    # Validate multiple products
    validate_bulk_parser = subparsers.add_parser(
        "validate-bulk", help="Validate multiple products"
    )
    validate_bulk_parser.add_argument(
        "skus", nargs="+", help="SKUs to validate"
    )
    validate_bulk_parser.add_argument(
        "--claude", action="store_true", help="Use Claude for analysis"
    )
    validate_bulk_parser.set_defaults(func=validate_products)
    
    # Interactive mode
    interactive_parser = subparsers.add_parser(
        "interactive", help="Interactive BOM analysis with Claude"
    )
    interactive_parser.add_argument("sku", help="SKU to analyze")
    interactive_parser.set_defaults(func=interactive_mode)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
