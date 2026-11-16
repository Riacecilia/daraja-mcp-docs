from pathlib import Path
import sys

# Locate daraja/docs safely relative to this script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "daraja_docs"
MAX_PAGE_CHARS = 50000
WARN_SECTION_WORDS = 260
MAX_SECTION_WORDS = 300

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
    "authentication",
    "headers",
    "payload",
}

def strip_frontmatter(lines: list[str]) -> list[str]:
    #Skip the top YAML block so it isn't counted as section content
    if len(lines) >= 3 and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return lines[index+1:]
    return lines

def count_clean_words(section_lines: list[str]) -> int:
    # Strip markdown table dividers and pipes, then count real words
    words= []
    for line in section_lines:
        stripped= line.strip()
        if stripped.startswith ("|") and set(stripped) <= {"|", "-", ":", " "}:
            continue
        clean_line = line.replace("|", " ").replace("`", " ")
        words.extend(clean_line.split())
    return len(words)

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

    # Strip YAML frontmatter before checking sections and headings
    body_lines = strip_frontmatter(raw_text.splitlines())

    in_code_block = False
    previous_heading_level = 0
    current_section = "(Intro before first heading)"
    section_lines: list[str] = []   

    def check_section_budget(title: str, lines_buffer: list[str]) -> None:
        nonlocal errors, warnings
        word_count = count_clean_words(lines_buffer)
        est_tokens = int(word_count * 1.33)
        if word_count > MAX_SECTION_WORDS:
            print(f"  [ERROR] Rule 2 (Chunk Size): '{title}' has {word_count} words (~{est_tokens} tokens). Max is {MAX_SECTION_WORDS} words.")
            errors += 1
        elif word_count > WARN_SECTION_WORDS:
            print(f"  [WARN]  Rule 2 (Chunk Size): '{title}' has {word_count} words (~{est_tokens} tokens). Approaching {MAX_SECTION_WORDS} limit.")
            warnings += 1

    for line in body_lines:
        stripped = line.strip()

        #Toggle code block state so '# comments' inside code aren't treated as headings
        if stripped.startswith("```"):
            in_code_block= not in_code_block
            section_lines.append(line)
            continue

        # Check Markdown headings outside code blocks
        if not in_code_block and stripped.startswith("#"):
            hashes= len(stripped) - len(stripped.lstrip("#"))
            if hashes > 0 and len(stripped) > hashes and stripped[hashes] == " ":
                heading_text= stripped[hashes+1 :].strip()

                # Rule 3: No H4-H6 headings
                if hashes >=4:
                    print(f" [ERROR] Rule 3 (Deep Heading): H{hashes} found ('{stripped}'). Only H1-H3 allowed.")
                    errors += 1

                # Rule 4: No skipped heading levels (e.g., H1 -> H3)
                if previous_heading_level > 0 and hashes > previous_heading_level + 1:
                    print(f"  [WARN]  Rule 4 (Skipped Level): '{stripped}' jumps from H{previous_heading_level} to H{hashes}.")
                    warnings += 1
                previous_heading_level = hashes

                # Rule 5: No generic standalone headings
                if hashes in (2, 3) and heading_text.lower() in GENERIC_HEADINGS:
                    print(f"  [WARN]  Rule 5 (Generic Heading): '{stripped}' is too generic. Include the API/endpoint name.")
                    warnings += 1

                #Rule 2: When a new H2 or H3 begins, score the previous section
                if hashes in (2,3):
                    check_section_budget(current_section, section_lines)
                    current_section= stripped
                    section_lines= []
                    continue

        section_lines.append(line)

    # Check the final section at the bottom of the file
    check_section_budget(current_section, section_lines)

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
