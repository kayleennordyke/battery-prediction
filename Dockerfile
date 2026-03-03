# battery-prediction: sweep/job generation
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy repo
COPY . .

# Default: shell; run sweep with: python -m bdt.sim.sweep configs/sweep.yaml
ENV PYTHONPATH=/app
CMD ["bash"]
