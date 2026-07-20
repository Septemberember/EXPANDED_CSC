# EX_CSC Dataset

This is the unified public EX_CSC dataset used by the artifact. It merges the
subject programs from EX_CSC_dataset into one dataset root, so
experiment scripts can use this directory directly:

```bash
--dataset-root dataset/EX_CSC_dataset
```

Each subject directory contains the original Java program, mutant Java
programs, FSF inputs when available, and provenance notes. The merged
`mutants_manifest.jsonl` contains the concatenated mutant manifest entries from
all the unified dataset.

Batch-level validation, quality, and provenance notes are retained under
`metadata/` for traceability, but the executable dataset layout is intentionally
flat:

```text
EX_CSC_dataset/
  mutants_manifest.jsonl
  SubjectName/
    SubjectName.java
    SubjectName_M1.java
    ...
    FSF/
      SubjectName_FSF.txt
  metadata/
```

Subject count: 42
