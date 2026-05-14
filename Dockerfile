FROM python:3.12-slim

WORKDIR /app

# Install deps
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/
RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "pushfyp.web.main:app", "--host", "0.0.0.0", "--port", "8000"]
