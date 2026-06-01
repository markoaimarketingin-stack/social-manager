Deployment checklist — Social Manager (backend)

1) Environment
- Create a `.env` file from `.env.example` and fill in all required values.
- Ensure `JWT_SECRET_KEY` is a strong random value (e.g., `openssl rand -hex 32`).
- Set `FRONTEND_URL` to your frontend origin and `BACKEND_URL` to your backend public URL.
- Update `CORS_ORIGINS` to include your frontend origin.

2) Database
- For production, use Postgres. Set `SOCIAL_MANAGER_DB_URL=postgresql://user:pass@host:5432/dbname`.
- Run migrations (Alembic) before starting the app.

3) Dependencies
- Create a Python 3.11+ virtualenv and install:

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

4) Run (development)
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8088 --reload
```

5) Run (production)
- Use a process manager (systemd, supervisor) and a production ASGI server such as `uvicorn` behind a reverse proxy.
- Example systemd service (replace paths and user):

```ini
[Unit]
Description=Social Manager API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/srv/social-manager/backend
EnvironmentFile=/srv/social-manager/backend/.env
ExecStart=/srv/social-manager/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8088 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

6) OAuth apps
- Configure OAuth redirect URIs in provider consoles to point at `${BACKEND_URL}/api/auth/{platform}/callback`.
- Ensure the provider app credentials are set in `.env`.

7) Frontend
- The frontend should call `POST /api/users/login` and include `Authorization: Bearer <token>` for protected endpoints.
- For OAuth connect flows, call `GET /api/auth/{platform}/connect` with the Authorization header.

8) Notes
- The backend now signs OAuth `state` parameters as short-lived JWTs. Do not attempt to tamper with `state`.
- `JWT_SECRET_KEY` rotation requires reissue of tokens; plan carefully for key rotation.

If you want, I can run a final smoke-test against the running server now or help prepare deployment manifests (Docker, render, or vercel).