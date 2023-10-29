FROM duffn/python-poetry:3.10-slim-1.1.12-2022-01-21
WORKDIR /app
#COPY pyproject.toml poetry.lock ./
# RUN poetry install
COPY . .
RUN poetry install
CMD ["sh"]
