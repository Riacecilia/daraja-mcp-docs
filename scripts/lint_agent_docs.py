from pathlib import Path
import sys

# Locate daraja/docs safely relative to this script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "daraja_docs"
MAX_PAGE_CHARS = 50000


def check_file(file_path: Path) -> tuple[int, int]:
    errors = 0
    warnings= 0 

    raw_text= file_path.read_text(encoding="utf-8")
    char_count = len(raw_text)
    approx_tokens= char_count // 4

    # Rule 1: Page size ceiling
    if char_count > MAX_PAGE_CHARS:
        print(f" [ERROR] Rule 1 (Page Size): {char_count:,} chars (~{approx_tokens:,} tokens) exceeds {MAX_PAGE_CHARS} limit.")
        errors +=1

    return errors, warnings

def main()-> None:
    if not DOCS_DIR.is_dir():
        print(f"Error: Could not find folder at {DOCS_DIR}")
        sys.exit(1)

    md_files = sorted(DOCS_DIR.glob("*.md"))
    print(f"Linting {len(md_files)} files in '{DOCS_DIR.name}/'...\n")

    total_errors = 0
    total_warnings= 0

    for md_file in md_files:
        print(f"Checking {md_file.name}:")
        file_errors, file_warnings = check_file(md_file)
        if file_errors == 0 and file_warnings == 0:
            print(" [OK] Passed.")
        total_errors += file_errors
        total_warnings += file_warnings

    print(f"\nSummary: {total_errors} error(s), {total_warnings} warning(s)")
    if total_errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
