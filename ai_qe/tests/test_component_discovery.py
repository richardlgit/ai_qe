from pathlib import Path

from ai_qe.repository.component_discovery import (
    discover_components,
)
from ai_qe.repository.models import (
    SourceFile,
)



def test_nested_components_are_discovered(
    tmp_path: Path,
):
    services_dir = (
        tmp_path
        / "sample_app"
        / "services"
    )

    clients_dir = (
        tmp_path
        / "sample_app"
        / "clients"
    )

    services_dir.mkdir(parents=True)
    clients_dir.mkdir(parents=True)

    (
        services_dir
        / "order_service.py"
    ).write_text(
        "",
        encoding="utf-8",
    )

    (
        clients_dir
        / "payment_client.py"
    ).write_text(
        "",
        encoding="utf-8",
    )

    source_files = [
        SourceFile(
            path=(
                "sample_app/services/"
                "order_service.py"
            ),
            language="python",
            size_bytes=1,
        ),
        SourceFile(
            path=(
                "sample_app/clients/"
                "payment_client.py"
            ),
            language="python",
            size_bytes=1,
        ),
    ]

    components = discover_components(
        repository_root=tmp_path,
        source_files=source_files,
    )

    names = {
        component.name
        for component in components
    }

    assert names == {
        "sample_app.services",
        "sample_app.clients",
    }


def test_component_dependency_is_discovered(
    tmp_path: Path,
):
    package_a = (
        tmp_path / "package_a"
    )

    package_b = (
        tmp_path / "package_b"
    )

    package_a.mkdir()
    package_b.mkdir()

    (
        package_a / "service.py"
    ).write_text(
        "from package_b.client import Client\n",
        encoding="utf-8",
    )

    (
        package_b / "client.py"
    ).write_text(
        "class Client: pass\n",
        encoding="utf-8",
    )

    source_files = [
        SourceFile(
            path="package_a/service.py",
            language="python",
            size_bytes=1,
        ),
        SourceFile(
            path="package_b/client.py",
            language="python",
            size_bytes=1,
        ),
    ]

    components = discover_components(
        repository_root=tmp_path,
        source_files=source_files,
    )

    component_a = next(
        component
        for component in components
        if component.name
        == "package_a"
    )

    assert len(
        component_a.dependencies
    ) == 1

    assert (
        component_a.dependencies[
            0
        ].component
        == "package_b"
    )

def test_nested_component_dependency_is_discovered(
    tmp_path: Path,
):
    services_dir = (
        tmp_path
        / "sample_app"
        / "services"
    )

    clients_dir = (
        tmp_path
        / "sample_app"
        / "clients"
    )

    services_dir.mkdir(
        parents=True
    )

    clients_dir.mkdir(
        parents=True
    )

    (
        services_dir / "order_service.py"
    ).write_text(
        (
            "from sample_app.clients.payment_client "
            "import PaymentClient\n"
        ),
        encoding="utf-8",
    )

    (
        clients_dir / "payment_client.py"
    ).write_text(
        "class PaymentClient: pass\n",
        encoding="utf-8",
    )

    source_files = [
        SourceFile(
            path=(
                "sample_app/services/"
                "order_service.py"
            ),
            language="python",
            size_bytes=1,
        ),
        SourceFile(
            path=(
                "sample_app/clients/"
                "payment_client.py"
            ),
            language="python",
            size_bytes=1,
        ),
    ]

    components = discover_components(
        repository_root=tmp_path,
        source_files=source_files,
    )

    services = next(
        component
        for component in components
        if component.name
        == "sample_app.services"
    )

    assert len(
        services.dependencies
    ) == 1

    assert (
        services.dependencies[0].component
        == "sample_app.clients"
    )    