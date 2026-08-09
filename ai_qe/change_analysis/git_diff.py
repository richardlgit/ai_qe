import subprocess
from dataclasses import dataclass


@dataclass
class GitChange:
    file_path: str
    diff: str


def get_changed_files(
    base_revision: str,
    target_revision: str,
) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            base_revision,
            target_revision,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def get_file_diff(
    base_revision: str,
    target_revision: str,
    file_path: str,
) -> str:
    result = subprocess.run(
        [
            "git",
            "diff",
            base_revision,
            target_revision,
            "--",
            file_path,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return result.stdout


def get_git_changes(
    base_revision: str,
    target_revision: str,
) -> list[GitChange]:
    changed_files = get_changed_files(
        base_revision=base_revision,
        target_revision=target_revision,
    )

    return [
        GitChange(
            file_path=file_path,
            diff=get_file_diff(
                base_revision=base_revision,
                target_revision=target_revision,
                file_path=file_path,
            ),
        )
        for file_path in changed_files
    ]