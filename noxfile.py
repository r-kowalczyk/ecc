import tempfile
import nox

KNOWN_SAFETY_VULNERABILITIES = [
    # ADVISORY: Langchain is vulnerable to CVE-2023-39659: An issue in
    # langchain-ai/ langchain allows a remote attacker to execute arbitrary code
    # via a crafted script to the PythonAstREPLTool._run
    "60433",  # langchain version <=0.0.335
]

# options
nox.options.sessions = (
    "ruff",
    "bandit",
    "safety",
    "mypy",
)
nox.options.reuse_existing_virtualenvs = True
SILENT_DEFAULT = True
SILENT_CODE_MODIFIERS = False

# targets
PACKAGE_LOCATION = "."
CODE_LOCATIONS = PACKAGE_LOCATION
PYTHON_VERSIONS = ["3.12"]
PYPY3_VERSION = "pypy3"
LATEST_PYTHON = PYTHON_VERSIONS[-1]

# A common exclusion pattern for ipynb files.
IPYNB_EXCLUDE = "--exclude"
IPYNB_PATTERN = ".*\\.ipynb$"


@nox.session(python=LATEST_PYTHON, tags=["lint"])
def ruff(session: nox.Session) -> None:
    """Lint with ruff."""
    # If no arguments are provided, use CODE_LOCATIONS and exclude ipynb files.
    args = session.posargs or [CODE_LOCATIONS, IPYNB_EXCLUDE, IPYNB_PATTERN]
    _install(session, "ruff")
    _run(session, "ruff", "check", *args)


@nox.session(python=LATEST_PYTHON, tags=["format"])
def black(session: nox.Session) -> None:
    """Reformat with black."""
    args = session.posargs or [CODE_LOCATIONS, IPYNB_EXCLUDE, IPYNB_PATTERN]
    _install(session, "black")
    _run_code_modifier(session, "black", *args)


@nox.session(python=LATEST_PYTHON, tags=["format"])
def isort(session: nox.Session) -> None:
    """Reformat the import order with isort."""
    args = session.posargs or [CODE_LOCATIONS, IPYNB_EXCLUDE, IPYNB_PATTERN]
    _install(session, "isort")
    _run_code_modifier(session, "isort", *args)


@nox.session(python=["3.8.18"], tags=["security"])
def bandit(session: nox.Session) -> None:
    """Scan for common security issues with bandit."""
    args = session.posargs or CODE_LOCATIONS  # Bandit may not support --exclude in the same way.
    _install(session, "bandit")
    _run(session, "bandit", *args)


@nox.session(python=PYPY3_VERSION, tags=["security"])
def safety(session: nox.Session) -> None:
    """Scan dependencies for insecure packages."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "pip-compile",
            "--output-file",
            requirements.name,
            external=True,
            silent=SILENT_DEFAULT,
        )
        session.install("safety")
        session.run(
            "safety",
            "check",
            f"--ignore={','.join(KNOWN_SAFETY_VULNERABILITIES)}",
            f"--file={requirements.name}",
            "--full-report",
            silent=SILENT_DEFAULT,
        )


@nox.session(python=PYTHON_VERSIONS, tags=["typecheck"])
def mypy(session: nox.Session) -> None:
    """Verify types using mypy (so it is static)."""
    # Mypy supports the --exclude option.
    args = session.posargs or [CODE_LOCATIONS, "--exclude", IPYNB_PATTERN]
    _install(session, "mypy")
    _install(session, "types-requests")
    session.run("mypy", "--ignore-missing-imports", "--explicit-package-bases", *args)


@nox.session(python=LATEST_PYTHON, tags=["documentation"])
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    _install(session, "sphinx")
    _run(session, "sphinx-build", "docs", "docs/_build")


def _install(session: nox.Session, *args: str) -> None:
    session.install("nox")
    session.install(*args)


def _run(
    session: nox.Session,
    target: str,
    *args: str,
    silent: bool = SILENT_DEFAULT,
) -> None:
    session.run(target, *args, external=True, silent=silent)


def _run_code_modifier(session: nox.Session, target: str, *args: str) -> None:
    _run(session, target, *args, silent=SILENT_CODE_MODIFIERS)
