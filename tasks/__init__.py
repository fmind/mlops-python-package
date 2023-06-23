"""Task collections for the project."""
# pylint: disable=redefined-builtin
# mypy: ignore-errors

# %% IMPORTS

from invoke import Collection

from . import bump, check, clean, dag, docker, docs, format, install, package

# %% NAMESPACES

ns = Collection()

# %% COLLECTIONS

ns.add_collection(bump)
ns.add_collection(check)
ns.add_collection(clean)
ns.add_collection(dag, default=True)
ns.add_collection(docker)
ns.add_collection(docs)
ns.add_collection(format)
ns.add_collection(install)
ns.add_collection(package)
