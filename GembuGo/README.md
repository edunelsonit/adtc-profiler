# GembuGo — Offline AI Learning Platform

GembuGo is a learning platform for the Africa Deep Tech Challenge 2026. Its on-device tutor answers student questions with a quantized GGUF model through `llama.cpp`; questions and answers never leave the laptop.

## Challenge fit

**Domain:** Coding Assistants / programming tutoring. The tutor explains concepts, generates practice questions, and builds study plans without cloud APIs.

The architecture addresses intermittent connectivity, API cost, student privacy, 8 GB RAM, and integrated graphics. Use a 1B–3B 4-bit instruct GGUF model to stay below the 7 GB peak-RAM target; `llama.cpp` provides efficient CPU inference and GGUF quantization.

## Run the app

### Requirements

- Python 3.11 or newer (the web app has no Python package dependencies)
- Optional: a local `llama.cpp` `llama-cli` binary and an instruct GGUF model for the Offline AI tutor

The course catalogue, lessons, quizzes, certificates, and profile work without a model. The model is only needed to answer tutor messages.

### Read documents aloud and get summaries

Open **Document reader** in the sidebar and upload a TXT, Markdown, CSV, DOCX, or PDF file (up to 5 MB). GembuGo extracts the text locally, produces a short extractive summary, and can read either the summary or the document through the browser’s built-in text-to-speech voice.

TXT, Markdown, CSV, and DOCX support uses only the Python standard library. PDF text extraction additionally requires the local `pdftotext` command (provided by the `poppler-utils` package on Debian/Ubuntu). Scanned or password-protected PDFs cannot be read unless they contain extractable text.

### Run with Docker

Build and run the app container from the repository root:

```bash
docker build -t gembugo ./GembuGo
docker run --rm -p 8000:8000 gembugo
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). To enable the tutor, mount a local model into the container and set `MODEL_PATH`:

```bash
docker run --rm -p 8000:8000 \
  -v /absolute/path/model.gguf:/models/model.gguf:ro \
  -e MODEL_PATH=/models/model.gguf \
  -e LLAMA_CLI=/path/in/container/to/llama-cli \
  gembugo
```

The base image intentionally does not bundle a model or `llama.cpp`; supply a model and a compatible `llama-cli` image extension when enabling inference.

### Start without the AI tutor

```bash
cd GembuGo
python3 server.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in a browser. The tutor will clearly show that a model has not been configured; it will never send a question to a cloud service.

### Start with a local GGUF model

Build or download `llama.cpp` and a suitably licensed instruct GGUF model, then point GembuGo to both files:

```bash
cd GembuGo
MODEL_PATH=/absolute/path/model.gguf \
LLAMA_CLI=/absolute/path/llama-cli \
python3 server.py
```

For example, if `llama-cli` is already on your `PATH`, you only need:

```bash
MODEL_PATH=/absolute/path/model.gguf python3 server.py
```

Use `PORT` to choose a different local port:

```bash
PORT=8080 python3 server.py
```

Then open `http://127.0.0.1:8080`.

### Confirm the tutor is ready

Select **Offline AI tutor** in the sidebar. A green status dot and “Local model ready” confirm that GembuGo can run the model. The tutor invokes `llama-cli` only on your machine, and the server listens only on `127.0.0.1`.

### Troubleshooting

- **“Local model not configured”**: confirm that `MODEL_PATH` is the full path to an existing `.gguf` file, then restart the server.
- **“Unable to respond” or a server error**: confirm that `LLAMA_CLI` points to an executable `llama-cli` binary. If it is on your `PATH`, omit `LLAMA_CLI`.
- **Port already in use**: start with another port, such as `PORT=8080 python3 server.py`.
- **Slow responses or memory pressure**: use a 1B–3B 4-bit instruct GGUF model and adjust your `llama.cpp` setup for the available hardware.

## Benchmark submission plan

On the ADTC standard laptop, measure tokens/sec, peak RAM, CPU use, temperature/throttling, and quality on the published validation prompts with the submitted model, context size, and thread configuration. Target ≥15 TPS, under 7 GB peak RAM, and no throttling.
