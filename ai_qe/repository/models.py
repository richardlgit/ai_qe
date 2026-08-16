from dataclasses import dataclass, field

test_component_map: dict[
    str,
    list[str],
] = field(
    default_factory=dict
)

@dataclass
class SourceFile:
    path: str
    language: str
    size_bytes: int


@dataclass
class DiscoveredTest:
    name: str
    test_file: str
    test_type: str = "unknown"


@dataclass
class ComponentDependency:
    component: str
    imported_by_files: list[str] = field(
        default_factory=list
    )


@dataclass
class DiscoveredComponent:
    name: str
    root_path: str
    files: list[str] = field(
        default_factory=list
    )
    dependencies: list[
        ComponentDependency
    ] = field(
        default_factory=list
    )

@dataclass
class RepositoryInventory:
    repository_name: str
    repository_root: str
    languages: list[str]

    source_files: list[SourceFile] = field(
        default_factory=list
    )

    tests: list[DiscoveredTest] = field(
        default_factory=list
    )

    components: list[
        DiscoveredComponent
    ] = field(
        default_factory=list
    )

    test_component_map: dict[
        str,
        list[str],
    ] = field(
        default_factory=dict
    )