# Stage 1: builder — installs sklearn, runs script, saves output
FROM python:3.11-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir scikit-learn
COPY compute.py .
RUN python compute.py > output.txt

# Stage 2: runtime — only carries the output file
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/output.txt .
CMD ["cat", "output.txt"]