# Domify

An AI-powered real estate search platform for the Sofia, Bulgaria property market. Instead of filling out rigid filter forms, users describe what they want in natural language — in Bulgarian — and the system finds the most relevant listings using semantic search.

---

## What It Does

The platform lets users type queries like *"Покажи ми двустаен апартамент под 2500 EUR/m2 на 3-ти етаж"* and returns ranked property listings that match their intent. It combines structured constraint filtering (price, size, room count, floor) with vector similarity search to surface the most semantically relevant results from a large corpus of scraped Sofia listings.

---

## Value

- **Natural language search** — no dropdowns, no sliders; just describe what you want
- **Bilingual-ready architecture** — query parsing and UI built around Bulgarian property terminology
- **Semantic ranking** — results are ranked by meaning, not just keyword overlap
- **Real market data** — continuously scraped from [imoti.net](https://www.imoti.net), the largest Bulgarian real estate portal
- **Full pipeline ownership** — from raw HTML scraping to cleaned data to vector embeddings, everything runs in-house

---

## Functionalities

### Natural Language Query Understanding
Queries are parsed with regex patterns to extract hard constraints:
- **Total price** — 5–7 digit numbers with optional currency (EUR / BGN)
- **Price per m²** — 3–5 digit numbers followed by `/m2` or `/м2`
- **Property size** — values in `кв.м`, `m2`, or `sqm`
- **Room count** — Bulgarian property type terms (`едностаен`, `двустаен`, `тристаен`, `четиристаен`, `многостаен`)
- **Floor number** — supports ordinal suffixes (`-ви`, `-ри`, `-ти`) and total-floor notation (`3/8`)

### Multi-Stage Search Pipeline
1. Extract hard constraints from the query
2. Filter the SQLite database to a candidate set that satisfies those constraints
3. Embed the full query using OpenAI `text-embedding-3-small`
4. Run vector similarity search (cosine) in Qdrant, filtered to the candidate set
5. Enrich results with image URLs and listing links from SQLite
6. Return ranked listings to the frontend

### Web Scraping & Data Collection
- **Harvester** — scrapes imoti.net listing pages, extracts title, link, and alt text
- **Worker** — visits each listing's detail page and extracts: description, price/m², size, floor, energy class, broker commission, extras/amenities
- **Status tracking** — each record moves through `pending → processing → done` states in SQLite
- **Backfill** — separate passes to recover missing image URLs and extras

### Data Transformation Pipeline
- **Cleaning** — numeric and boolean type coercion, validation
- **Transformation** — extracts neighborhood from listing title, classifies estate type (apartment, garage, land parcel, shop), parses room count from Bulgarian terminology, calculates total price in EUR
- **Output** — `ads_cleaned` SQLite table with normalized, analysis-ready data

### Vector Database Population
- Reads from `ads_cleaned`, generates embeddings in batches of 20
- Upserts into a Qdrant cloud collection (`listings`, cosine distance, 1536 dimensions)
- Payload includes: `hash_id`, `title`, `neighborhood`, `price_m2_eur`, `size_m2`, `floor`, `description`, `extras`

### Chat Interface (Frontend)
- Conversational search UI
- Pre-populated Bulgarian query suggestions
- Listing cards with image, title, neighborhood, size, room count, price, and external link
- Loading states and real-time feedback

---

## Tech Stack

### Backend (Python)

| Layer | Technology |
|---|---|
| API framework | FastAPI 0.135, Uvicorn 0.43 |
| Data processing | Pandas 3.0, NumPy 2.4 |
| Web scraping | BeautifulSoup4, Requests, Chardet |
| AI / Embeddings | OpenAI API (`text-embedding-3-small`) |
| Vector database | Qdrant Cloud (qdrant-client 1.17) |
| Relational database | SQLite3 |
| Exploration | Jupyter notebooks, Seaborn |

### Frontend (TypeScript / React)

| Layer | Technology |
|---|---|
| Framework | React 18, TypeScript 5, Vite 5 |
| Routing | React Router DOM 6 |
| Server state | TanStack React Query 5 |
| UI components | Shadcn/ui (Radix UI primitives) |
| Styling | TailwindCSS 3 |
| Forms | React Hook Form 7, Zod |
| Charts | Recharts |
| Icons | Lucide React |
| Testing | Vitest, Playwright |
| Package manager | Bun |

---

## Architecture

```
┌─────────────────────────────────────────┐
│              React Frontend             │
│   ChatInterface  ←→  ListingCard        │
│         ↓                               │
│   api.ts → POST /search                 │
└─────────────────┬───────────────────────┘
                  │ HTTP (port 8000)
┌─────────────────▼───────────────────────┐
│           FastAPI Backend               │
│                                         │
│  /search                                │
│    1. Extract hard constraints (regex)  │
│    2. Filter SQLite → candidate IDs     │
│    3. Embed query (OpenAI)              │
│    4. Vector search (Qdrant, filtered)  │
│    5. Enrich from SQLite                │
│    6. Return ranked Listing[]           │
└──────┬───────────────┬──────────────────┘
       │               │
┌──────▼──────┐  ┌─────▼──────────┐
│  SQLite DB  │  │  Qdrant Cloud  │
│ ads_raw     │  │  "listings"    │
│ ads_cleaned │  │  cosine, 1536d │
└─────────────┘  └────────────────┘
```

### Data Ingestion Pipeline

```
imoti.net
  └─ Harvester (list pages) → ads_raw [pending]
      └─ Worker (detail pages) → ads_raw [done]
          └─ Transformation → ads_cleaned
              └─ Embeddings → Qdrant
```

---

## Project Structure

```
├── backend/
│   ├── api/                  # FastAPI app, search service
│   ├── agent/                # LLM integration
│   ├── scraper/              # Harvester, worker, SQLite storage
│   ├── data_transformation/  # Cleaning and transformation pipeline
│   ├── vector_db/            # Embedding generation and Qdrant management
│   ├── retrieval/            # Hard constraint extraction logic
│   └── exploration/          # Jupyter notebooks for EDA
└── frontend/
    └── src/
        ├── pages/            # Index, NotFound
        ├── components/       # ChatInterface, ListingCard, UI primitives
        ├── api/              # API client
        └── hooks/            # Custom React hooks
```
