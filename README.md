# AI Commerce Demo

A realistic demo e-commerce website that showcases AI over structured business data.

## Stack

- Frontend: React, Vite, TailwindCSS, React Router
- Backend: FastAPI
- Database: SQLite
- AI: Groq API preferred, with Mistral API support

## Project layout

- `frontend/` - storefront, dashboard, and chat UI
- `backend/` - FastAPI API, SQLite layer, analytics, and AI tool orchestration
- `database/` - generated SQLite database file
- `public/` - shared static assets and demo notes

## Run locally

1. Install backend dependencies:

   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```

2. Start the backend:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Install frontend dependencies:

   ```bash
   cd frontend
   npm install
   ```

4. Start the frontend:

   ```bash
   npm run dev
   ```

5. Optional AI configuration:

   - `AI_PROVIDER=groq`
   - `GROQ_API_KEY=...`
   - `GROQ_MODEL=llama-3.1-8b-instant`
   - `AI_PROVIDER=mistral`
   - `MISTRAL_API_KEY=...`

## API endpoints

- `GET /products`
- `GET /products/{id}`
- `GET /dashboard`
- `GET /analytics`
- `POST /chat/customer`
- `POST /chat/admin`

## Notes

- The SQLite database is created and seeded automatically on backend startup.
- All seeded products use the same placeholder image at `/images/product.jpg`.
- The assistants answer only from SQLite-backed tool calls; they are designed to avoid hallucinations.
