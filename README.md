# Phase 2 RAG API — Deployment Guide

This folder is a standalone version of your Phase 2 notebook's RAG + Urdu
generation logic, packaged as a normal Flask web service so it can run on
Render or Railway instead of Colab + ngrok.

**Why not the fine-tuned Qwen2 model too?** It needs a GPU / several GB RAM
that free/hobby web hosting doesn't give you. Your notebook already falls
back to Groq when the fine-tuned model isn't available (Cell 7,
`USE_FINETUNED = False` branch) — this deployment always uses that Groq path.
Keep the notebook for local fine-tuning experiments/demo; use this service
for the live API Phase 3 talks to.

## Files
- `app.py` — the Flask service (`/retrieve`, `/generate-urdu`, `/health`)
- `traffic_laws.py` — your 8 Pakistani traffic laws (from notebook Cell 2)
- `requirements.txt`, `Procfile` — deployment config
- `.env.example` — copy to `.env` for local testing only

## 1. Get a Groq API key (yours is now public — get a fresh one)
Since your old key was exposed in the notebook, go to
https://console.groq.com, revoke the old one, and generate a new one.
Never paste it directly into code — always use an environment variable
(both platforms below let you set this in their dashboard).

## 2. Push this folder to a GitHub repo
```bash
cd phase2-deploy
git init
git add .
git commit -m "Phase 2 RAG API"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## 3A. Deploy on Render
1. Go to https://dashboard.render.com → **New** → **Web Service**.
2. Connect your GitHub repo.
3. Settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1`
   - **Instance type**: at least the free/starter tier with 512MB+ RAM (embedding model needs ~500MB)
4. Under **Environment** → **Environment Variables**, add:
   - `GROQ_API_KEY` = your new Groq key
5. Click **Create Web Service**. First deploy takes a few minutes (downloading the embedding model). Render gives you a permanent URL like `https://your-service.onrender.com`.
6. Test it:
   ```bash
   curl https://your-service.onrender.com/health
   ```
7. Note: Render's free tier spins down after inactivity, so the first request after idling will be slow (~30-50s cold start) while it reloads the embedding model. If your FYP demo needs instant response, either keep it "warm" with a scheduled ping, or use the paid tier for the demo day.

## 3B. Deploy on Railway
1. Go to https://railway.app → **New Project** → **Deploy from GitHub repo**.
2. Select this repo. Railway auto-detects Python and uses the `Procfile`.
3. Go to your service → **Variables** tab, add:
   - `GROQ_API_KEY` = your new Groq key
4. Go to **Settings** → **Networking** → **Generate Domain** to get a public URL like `https://your-service.up.railway.app`.
5. Test it:
   ```bash
   curl https://your-service.up.railway.app/health
   ```
Railway doesn't sleep on the free trial credit the way Render's free tier does, but the trial credit is time/usage limited — check your usage in the dashboard.

## 4. Point Phase 3 at the deployed URL
In your Node backend's `.env`:
```
RAG_API_URL=https://your-service.onrender.com
```
(or the Railway URL). No more updating this every time Colab restarts —
that was the ngrok limitation from notebook Cell 13.

## 5. Test the two routes directly
```bash
curl -X POST https://your-service.onrender.com/retrieve \
  -H "Content-Type: application/json" \
  -d '{"violation_type": "No Helmet"}'

curl -X POST https://your-service.onrender.com/generate-urdu \
  -H "Content-Type: application/json" \
  -d '{"violation_type": "No Helmet", "law_section": "Section 139 - Motor Vehicles Ordinance 1965", "fine_amount": 500}'
```

## Local testing before deploying
```bash
cd phase2-deploy
pip install -r requirements.txt
cp .env.example .env   # then edit .env with your real key
export $(cat .env | xargs)
python app.py
# in another terminal:
curl http://localhost:5000/health
```
