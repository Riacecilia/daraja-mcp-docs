from pathlib import Path
import sys

# Locate daraja/docs safely relative to this script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "daraja_docs"
MAX_PAGE_CHARS = 50000

GENERIC_HEADINGS = {
    "overview",
    "parameters",
    "request",
    "response",
    "responses", 
    "errors", 
    "error codes",
    "example",
    "examples",
    "authentification",
    "headers",
    "payload",
}


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

    # Rules 3, 4 and 5: Heading checks
    in_code_block = False
    previous_heading_level = 0   

    for line in raw_text.splitlines():
        stripped = line.strip()

        #Toggle code block state so '# comments' inside code aren't treated as headings
        if stripped.startswith("```"):
            in_code_block= not in_code_block
            continue

        # Check Markdown headings outside code blocks
        if not in_code_block and stripped.startswith("#"):
            hashes= len(stripped) - len(stripped.lstrip("#"))
            if hashes > 0 and len(stripped) > hashes and stripped[hashes] == " ":
                heading_text= stripped[hashes+1 :].strip()

                # Rule 3: No H4-H6 headings
                if hashes >=4:
                    print(f" [ERROR] Rule 3 (Deep Heading): H{hashes} found ('{stripped}'). Only H1-H3 allowed.")

                # Rule 4: No skipped heading levels (e.g., H1 -> H3)
                if previous_heading_level > 0 and hashes > previous_heading_level + 1:
                    print(f"  [WARN]  Rule 4 (Skipped Level): '{stripped}' jumps from H{previous_heading_level} to H{hashes}.")
                    warnings += 1
                previous_heading_level = hashes

                # Rule 5: No generic standalone headings
                if hashes in (2, 3) and heading_text.lower() in GENERIC_HEADINGS:
                    print(f"  [WARN]  Rule 5 (Generic Heading): '{stripped}' is too generic. Include the API/endpoint name.")
                    warnings += 1

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
