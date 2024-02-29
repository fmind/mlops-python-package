# https://docs.docker.com/engine/reference/builder/

# Define
FROM python:3.12

# Install
COPY dist/* .
RUN pip install --no-cache-dir *.whl

# Execute
CMD ["bikes", "--help"]
