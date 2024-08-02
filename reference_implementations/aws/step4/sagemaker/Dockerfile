# Base image for inference environment
FROM nvidia/cuda:11.7.1-cudnn8.2.4-devel-ubuntu20.04 AS base

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy user-provided code
COPY handler.py ./

# Environment variable for model data path (set by SageMaker)
ENV MODEL_DATA_DIR /opt/ml/model

# Final image for serving
FROM base AS serving

# Copy user code from build stage
COPY --from=build handler.py ./

WORKDIR /app

ENTRYPOINT ["python", "handler.py"]

