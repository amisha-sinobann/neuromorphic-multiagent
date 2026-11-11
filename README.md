# Neuromorphic AI Multi-Agent Document Reviewer

Multi-agent system that **sees → thinks → recalls → checks → synthesizes** research text so hallucinations and common factual mistakes in neuromorphic AI writing are caught.

## Quick start (one command)

```bash
cd neuromorphic-multiagent
./start.sh
```

Then open **http://localhost:8000** in your browser.

(If `./start.sh` is not executable: `bash start.sh`)

### Manual start

```bash
cd neuromorphic-multiagent/backend
export PYTHONPATH=.
pip install -r requirements.txt   # first time only
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://localhost:8000**

## What you get

- Built-in dark UI (no separate frontend needed)
- Upload `.txt` / `.pdf` / `.docx` **or** paste text
- 5 agents with visible reasoning (anti-hallucination design)
- Flags overclaims, hardware myths (TrueNorth vs Loihi learning, “SNNs always replace GPUs”, etc.)

## Test text

Paste this:

```
Neuromorphic computing always replaces GPUs because spiking neural networks are more accurate and use zero energy when idle. Intel Loihi and IBM TrueNorth both support rich on-chip learning with STDP. SNNs guarantee better energy efficiency in all cases.
```

You should see multiple high-severity issues.

## Project layout

```
neuromorphic-multiagent/
├── start.sh                 # run this
├── backend/
│   ├── main.py              # FastAPI + serves UI
│   ├── agents/              # Viewer, Thinker, Recall, Checker, Synthesizer
│   ├── knowledge/           # neuromorphic facts + common mistakes
│   ├── services/            # PDF/DOCX text extraction
│   └── static/index.html    # UI
└── frontend/                # optional Next.js version (needs npm install)
```

## Optional Next.js frontend

If you prefer the React UI:

```bash
cd frontend
npm install
npm run dev
```

Point it at `http://localhost:8000` (already configured).

## Requirements

- Python 3.10+
- `pip install fastapi uvicorn python-multipart pypdf python-docx`
