# Architecture document ingestion (experimental)

Run `python3 adapters/architecture-ingest/ingest.py design.pdf --output parsed.json`.

Supported: `.pdf`, `.docx`, `.json`, `.md`, `.txt`, `.yaml`, `.yml`. Legacy `.doc` is **not supported yet** and must use an explicitly isolated conversion adapter; never mislabel DOC as DOCX.

Optional parser dependencies: `pypdf` for PDF, `python-docx` for DOCX, `PyYAML` for YAML. JSON/Markdown/TXT use Python standard library. No parser dependency enters the Rust core. Input bytes are SHA-256 hashed; extracted sections retain page, paragraph, table-row or line location. Structured JSON/YAML currently retain only a root pointer, not field-level paths.

Limits: 20 MiB file, 500 PDF pages, 2 million extracted characters. No OCR, images, scanned-PDF interpretation, embedded attachments or external URLs. PDF table structure may be lost. No requirement extraction or architectural correctness claim. Treat extracted content as **untrusted data**, never executable instructions. Parser sandboxing and adversarial-document hardening remain release blockers for this optional feature.
