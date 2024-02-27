"""Task collections for the project."""

# mypy: ignore-errors

# %% IMPORTS

from invoke import Collection

from . import carbons, checks, cleans, containers, dags, docs, formats, installs, packages

# %% NAMESPACES

ns = Collection()

# %% COLLECTIONS

ns.add_collection(carbons)
ns.add_collection(checks)
ns.add_collection(cleans)
ns.add_collection(dags, default=True)
ns.add_collection(containers)
ns.add_collection(docs)
ns.add_collection(formats)
ns.add_collection(installs)
ns.add_collection(packages)
