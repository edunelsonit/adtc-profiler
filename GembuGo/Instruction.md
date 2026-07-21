# Running GembuGo

GembuGo is a local learning application. Its learning content and document reader run without internet access. The optional AI tutor uses a GGUF model on the same machine.

## Option 1: Run with Python

Requirements:

- Python 3.11 or newer
- Optional for PDF uploads: `pdftotext` (`poppler-utils` on Debian/Ubuntu)
- Optional for the AI tutor: `llama.cpp`'s `llama-cli` and a local instruct GGUF model

From the repository root:

```bash
cd GembuGo
python3 server.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

To use another port:

```bash
PORT=8080 python3 server.py
```

Then open `http://127.0.0.1:8080`.

## Enable the offline AI tutor

Start the server with the full paths to a GGUF model and `llama-cli`:

```bash
cd GembuGo
MODEL_PATH=/absolute/path/model.gguf \
LLAMA_CLI=/absolute/path/llama-cli \
python3 server.py
```

If `llama-cli` is already on your `PATH`, omit `LLAMA_CLI`:

```bash
MODEL_PATH=/absolute/path/model.gguf python3 server.py
```

In the app, open **Offline AI tutor**. “Local model ready” confirms the configuration is working.

## Option 2: Run with Docker

Build the image from the repository root:

```bash
docker build -t gembugo ./GembuGo
docker run --rm -p 8000:8000 gembugo
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The Docker image includes PDF text extraction, but does not include a GGUF model or `llama-cli`.

## Use the document reader

1. Open **Document reader** from the sidebar.
2. Upload a TXT, Markdown, CSV, DOCX, or PDF file up to 5 MB.
3. Review the generated summary.
4. Select **Read summary** or **Read document** to use the browser’s text-to-speech voice.

Uploaded documents are processed locally and are not saved by GembuGo. Scanned or password-protected PDFs may not contain extractable text.

## Troubleshooting

- **Port already in use:** use `PORT=8080 python3 server.py`.
- **Tutor says model is not configured:** ensure `MODEL_PATH` points to an existing `.gguf` file, then restart the server.
- **Tutor returns an error:** check that `LLAMA_CLI` points to an executable `llama-cli` binary.
- **PDF cannot be read locally:** install `poppler-utils`, or use the Docker image which already includes it.
