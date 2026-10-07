# Restoring the ALI Studio Pro source tree

The repository contains the complete 4.6.0 source export split into 85 ordered Markdown parts.

To reconstruct the original 588-file text source tree locally:

    python scripts/extract_project.py

The files will be written under `restored-project/` using the paths embedded in the export.

This repository does not contain the original 220 MB binary ZIP or native model binaries; those require a binary-capable upload path. Hermes remains inactive.