"""
Digital Product Auto-Publisher Agent — Main CLI Entry Point.
Usage:
    python main.py --product <path_to_product> [--dry-run] [--auto-approve]
"""
import sys
import argparse
from pathlib import Path
from core.ingest import ProductIngestionEngine
from core.publisher import PublisherOrchestrator
from core.reporter import PublishReporter

def main():
    parser = argparse.ArgumentParser(description="Digital Product Auto-Publisher Agent")
    parser.add_argument("--product", type=str, default="Ultimate_Investment_Portfolio_Tracker_Pro.xlsx",
                        help="Path to product file (.xlsx, .zip, .pdf)")
    parser.add_argument("--prompt", "--generate", dest="prompt", type=str, default=None,
                        help="AI Prompt: Automatically generate a brand new digital product/template from scratch")
    parser.add_argument("--format-type", type=str, default="spreadsheet", choices=["spreadsheet", "document", "code"],
                        help="Type of product to generate: spreadsheet, document, or code")
    parser.add_argument("--dry-run", action="store_true", help="Simulate listing generation and validation without deploying live")
    parser.add_argument("--auto-approve", action="store_true", help="Bypass manual confirmation prompt")
    parser.add_argument("--no-api", "--browser", dest="no_api", action="store_true", 
                        help="Zero-API mode: Upload via automated browser sessions without developer API keys")
    parser.add_argument("--outdir", type=str, default="output", help="Directory to store reports")

    args = parser.parse_args()

    # Autonomous AI Product Generation Mode
    if args.prompt:
        from core.product_generator import ProductGenerator
        gen = ProductGenerator()
        product_path = gen.generate_product(args.prompt, asset_type=args.format_type)
    else:
        product_path = Path(args.product)
        if not product_path.is_absolute():
            # Check current directory or default scratch
            if not product_path.exists():
                default_scratch = Path(r"C:\mnt\data") / product_path.name
                if default_scratch.exists():
                    product_path = default_scratch
                else:
                    prod_scratch = Path(r"C:\Users\HP\.gemini\antigravity\scratch\portfolio_tracker") / product_path.name
                    if prod_scratch.exists():
                        product_path = prod_scratch

    print("=" * 80)
    print(" DIGITAL PRODUCT AUTO-PUBLISHER AGENT (v2.0)")
    print("=" * 80)
    print(f"Target Product : {product_path}")
    print(f"Mode           : {'[DRY-RUN SIMULATION]' if args.dry_run else '[LIVE DISTRIBUTION]'}")

    # 1. Ingestion & Analysis
    ingest_engine = ProductIngestionEngine(str(product_path))
    product_meta = ingest_engine.analyze()
    print(f"Product Loaded : {product_meta.title}")
    print(f"Type           : {product_meta.product_type}")
    print(f"Bundle Package : {product_meta.bundle_zip_path}")

    # 2. Orchestrate Publishing
    orchestrator = PublisherOrchestrator(
        product=product_meta,
        auto_approve=args.auto_approve,
        dry_run=args.dry_run,
        no_api=args.no_api
    )
    results = orchestrator.run()

    # 3. Generate Reports
    reporter = PublishReporter(product=product_meta, results=results, output_dir=args.outdir)
    report_text = reporter.generate_report()
    print("\nExecution finished successfully.")

if __name__ == "__main__":
    main()
