# https://docs.docker.com/engine/reference/builder/

FROM python:3.12
COPY dist/*.whl .
RUN pip install *.whl
CMD ["bikes", "--help"]
