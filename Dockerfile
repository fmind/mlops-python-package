# https://docs.docker.com/engine/reference/builder/

# Define
FROM python:3.11

# Install
COPY dist/*.whl .
RUN pip install --no-cache-dir *.whl

# Execute
CMD ["wines", "--help"]
