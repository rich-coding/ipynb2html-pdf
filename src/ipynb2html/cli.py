import argparse
import logging
import sys

from .converter import NotebookConverter


def main():
    parser = argparse.ArgumentParser(description="Convert Jupyter Notebooks to HTML or PDF.")
    parser.add_argument("input", help="Path to the .ipynb file")
    parser.add_argument(
        "--to", choices=["html", "pdf"], default="html", help="Output format (default: html)"
    )
    parser.add_argument(
        "--install", action="store_true", help="Install missing dependencies automatically"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    converter = NotebookConverter(install_missing=args.install)
    try:
        final_path = converter.convert(args.input, output_format=args.to)
        print(f"Success! File saved at: {final_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
