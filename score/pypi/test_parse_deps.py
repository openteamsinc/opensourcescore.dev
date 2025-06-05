import pytest
from .parse_deps import parse_deps, parse_dep


def test_parse_dep_simple_name_only():
    result = parse_dep("python-dotenv")
    assert result.name == "python-dotenv"
    assert result.specifiers == []
    assert result.include_check is None


def test_parse_dep_single_specifier():
    result = parse_dep("blinker>=1.9.0")
    assert result.name == "blinker"
    assert result.specifiers == [">=1.9.0"]
    assert result.include_check is None


def test_parse_dep_multiple_specifiers():
    result = parse_dep("package>=1.0,<2.0,!=1.5")
    assert result.name == "package"
    assert result.specifiers == [">=1.0", "<2.0", "!=1.5"]
    assert result.include_check is None


def test_parse_dep_with_include_check():
    result = parse_dep('importlib-metadata>=3.6.0; python_version < "3.10"')
    assert result.name == "importlib-metadata"
    assert result.specifiers == [">=3.6.0"]
    assert result.include_check == 'python_version < "3.10"'


def test_parse_dep_no_specifier_with_include_check():
    result = parse_dep('python-dotenv; extra == "dotenv"')
    assert result.name == "python-dotenv"
    assert result.specifiers == []
    assert result.include_check == 'extra == "dotenv"'


def test_parse_dep_complex_name():
    result = parse_dep("some-package_name.with.dots>=1.0")
    assert result.name == "some-package_name.with.dots"
    assert result.specifiers == [">=1.0"]
    assert result.include_check is None


def test_parse_dep_various_operators():
    result = parse_dep("package~=1.4.2")
    assert result.name == "package"
    assert result.specifiers == ["~=1.4.2"]
    assert result.include_check is None


def test_parse_deps_empty_list():
    result = parse_deps([])
    assert result == []


def test_parse_deps_none():
    result = parse_deps(None)
    assert result == []


def test_parse_deps_multiple_dependencies():
    deps = [
        "blinker",
        "click>=8.1.3,>2.0",
        'importlib-metadata>=3.6.0; python_version < "3.10"',
        'python-dotenv; extra == "dotenv"',
    ]
    result = parse_deps(deps)

    assert len(result) == 4
    assert result[0].name == "blinker"
    assert result[0].specifiers == []
    assert result[0].include_check is None

    assert result[1].name == "click"
    assert result[1].specifiers == [">=8.1.3", ">2.0"]
    assert result[1].include_check is None

    assert result[2].name == "importlib-metadata"
    assert result[2].specifiers == [">=3.6.0"]
    assert result[2].include_check == 'python_version < "3.10"'

    assert result[3].name == "python-dotenv"
    assert result[3].specifiers == []
    assert result[3].include_check == 'extra == "dotenv"'


def test_parse_dep_invalid_string():
    with pytest.raises(ValueError, match="Invalid dependency string"):
        parse_dep("123invalid")
