"""Cross-platform CLI; no shell activation required."""

import argparse
import json
from pathlib import Path
from zipfile import BadZipFile

from openpyxl.utils.exceptions import InvalidFileException

from .report import analyse_workbook, export_report
from .workbook import inspect_workbook


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only workbook inspection and equipment EDA")
    parser.add_argument("command", choices=["inspect", "analyse"])
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Local artifact directory")
    parser.add_argument("--real-data", action="store_true", help="Remove synthetic label; does not establish validity")
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            info = inspect_workbook(args.input)
            args.output.mkdir(parents=True, exist_ok=True)
            target = args.output / "inventory.json"
            if target.is_symlink() or target.resolve() == args.input.resolve():
                raise ValueError("Output must not overwrite or link to the input.")
            target.write_text(json.dumps(info, indent=2), encoding="utf-8")
            print(f"Inventoried {len(info['sheets'])} sheets. No formula recalculation performed.")
            return 0
        report = analyse_workbook(args.input, synthetic=not args.real_data)
        export_report(report, args.output)
        errors = int((report.issues["severity"] == "error").sum())
        print(f"Extracted {len(report.hours)} shift records; {len(report.issues)} issues ({errors} errors).")
        print("Outputs are local; review issues before interpretation. Other sections are not yet extracted.")
        return 1 if errors else 0
    except (OSError, ValueError, BadZipFile, InvalidFileException) as error:
        parser.exit(2, f"Unable to complete: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
