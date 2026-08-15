from pathlib import Path

from ai_qe.repository.models import (
    SourceFile,
)


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    "site-packages",
    "node_modules",
    "dist",
    "build",
}


LANGUAGE_BY_SUFFIX = {
    ".py": "python",
}


def should_ignore(
    path: Path,
) -> bool:
    return any(
        part in IGNORED_DIRECTORIES
        for part in path.parts
    )


def discover_source_files(
    repository_root: Path,
) -> list[SourceFile]:
    files: list[SourceFile] = []

    for path in repository_root.rglob("*"):
        if not path.is_file():
            continue

        if should_ignore(
            path.relative_to(repository_root)
        ):
            continue

        language = LANGUAGE_BY_SUFFIX.get(
            path.suffix.lower()
        )

        if language is None:
            continue

        files.append(
            SourceFile(
                path=str(
                    path.relative_to(
                        repository_root
                    )
                ),
                language=language,
                size_bytes=path.stat().st_size,
            )
        )

    return sorted(
        files,
        key=lambda item: item.path,
    )