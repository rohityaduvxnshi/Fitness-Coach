# Cloudflare Tunnel local workflow

1. Run backend on `http://localhost:8000`.
2. Run frontend on `http://localhost:4200`.
3. Copy `proxy.conf.cloudflared.example.json` into the Angular app root as `proxy.conf.cloudflared.json`.
4. Start Angular with the proxy config.
5. Install `cloudflared`.
6. Run:

```bash
cloudflared tunnel --url http://localhost:4200
```

Share the generated `trycloudflare.com` URL.

Preferred flow: expose only the frontend and proxy API requests to the backend locally.
