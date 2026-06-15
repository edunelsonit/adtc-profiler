# adtc-profiler runtime image.
#
# Multi-stage: stage 1 builds llama.cpp from a pinned commit for reproducibility,
# stage 2 ships only the runtime + the profiler Python package. Aiming for a
# slim image (<800 MB) so cloud VMs can pull it quickly.
#
# Build (locally or via Cloud Build):
#   docker build -t adtc-profiler:latest -f profiler/Dockerfile profiler/

# -----------------------------------------------------------------------------
# Stage 1: build llama.cpp (CPU-only, for parity with Standard Laptop profile)
# -----------------------------------------------------------------------------
FROM debian:bookworm-slim AS llama-build

ARG LLAMACPP_REF=master
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch "${LLAMACPP_REF}" \
      https://github.com/ggerganov/llama.cpp.git /src/llama.cpp \
    && cd /src/llama.cpp \
    && cmake -B build \
        -DBUILD_SHARED_LIBS=OFF \
        -DGGML_NATIVE=OFF \
        -DGGML_AVX=OFF \
        -DGGML_AVX2=OFF \
        -DGGML_AVX512=OFF \
        -DGGML_FMA=OFF \
        -DGGML_F16C=OFF \
        -DGGML_BLAS=OFF \
        -DGGML_CUDA=OFF \
        -DGGML_METAL=OFF \
    && cmake --build build --config Release --target llama-bench llama-cli llama-server -j2

# -----------------------------------------------------------------------------
# Stage 2: profiler runtime
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl ca-certificates lm-sensors libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# llama-bench + llama-cli + llama-server on PATH
COPY --from=llama-build /src/llama.cpp/build/bin/llama-bench  /usr/local/bin/
COPY --from=llama-build /src/llama.cpp/build/bin/llama-cli    /usr/local/bin/
COPY --from=llama-build /src/llama.cpp/build/bin/llama-server /usr/local/bin/

# Install the profiler package (no editable install — final image)
WORKDIR /opt/adtc-profiler
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

WORKDIR /work
ENTRYPOINT ["adtc-profiler"]
