# run project tasks
[group('project')]
project: project-environment (project-run "tuning") (project-run "training") (project-run "promotion") (project-run "inference") (project-run "evaluations") (project-run "explanations")

# export environment file
[group('project')]
project-environment: project-requirements
    #!/usr/bin/env python3
    import json
    with open(".python-version", "r") as reader:
        python = reader.read().strip()  # version
    configuration = {"python": python}
    with open("requirements.txt", "r") as reader:
        dependencies = []
        for line in reader.readlines():
            dependency = line.split(" ")[0].strip()
            if "pywin32" in dependency or "#" in dependency:
                continue
            dependencies.append(dependency)
    configuration["dependencies"] = dependencies
    with open("python_env.yaml", "w") as writer:
        json.dump(configuration, writer, indent=4)
        writer.write("\n")  # add new line at the end

# export requirements file
[group('project')]
project-requirements:
    uv export --format=requirements-txt --no-dev --no-hashes \
        --no-editable --no-emit-project --output-file=requirements.txt

# run project job using mlflow
[group('project')]
project-run job:
    uv run mlflow run --experiment-name={{REPOSITORY}} --run-name={{capitalize(job)}} -P conf_file=confs/{{job}}.yaml .
