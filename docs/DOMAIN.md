# Domain and HTTPS

Canonical website: https://ulybnis24.ru/
Admin: https://ulybnis24.ru/admin/

On 2026-10-09, authoritative Timeweb DNS and the Google/Cloudflare resolvers
returned `201.24.63.92` for the website. Both apex and `www` have A records;
there is no AAAA record. Django originally rejected the domain with HTTP 400
because production's allowed hosts contained only the server IP and localhost.

## Server Settings

The versioned `deploy/nginx.conf` is installed at
`/etc/nginx/sites-available/clinic_smile`. It serves the existing frontend,
proxies API/admin to the existing Unix socket, and preserves the static/media
location precedence. HTTP and HTTPS `www` redirect to the canonical HTTPS
domain with status 308, preserving the path and query string. Old HTTP links
using the IP also redirect there. Sign in again on the domain; cookies from
the IP address are not shared with it.

The backend production environment uses:

```dotenv
DJANGO_ALLOWED_HOSTS=ulybnis24.ru,www.ulybnis24.ru,201.24.63.92,localhost,127.0.0.1
DJANGO_BEHIND_PROXY=1
DJANGO_SECURE_COOKIES=1
```

Nginx overwrites `X-Forwarded-Proto` with the actual connection scheme. Django
trusts that header only when the explicit proxy setting is enabled; Gunicorn
is accessible only through its local Unix socket. HTTPS admin forms retain
same-origin CSRF checks, and session/CSRF cookies require HTTPS. No broad
CSRF-origin wildcard or public backend listener is needed.

## Certificate Renewal

Let's Encrypt certificates cover `ulybnis24.ru` and `www.ulybnis24.ru`.
Certificate paths are under `/etc/letsencrypt/live/ulybnis24.ru/`.
Private keys and the ACME account remain on the server, outside Git.

Certbot uses the persistent webroot `/var/www/letsencrypt`; Nginx serves only
`/.well-known/acme-challenge/` from it over HTTP. Keep port 80 reachable for
renewals. `certbot.timer` runs renewals automatically. The versioned script
`deploy/renew-nginx.sh` is installed executable at
`/etc/letsencrypt/renewal-hooks/deploy/clinic-nginx`; it validates and reloads
Nginx after renewal.

The ACME account was registered without a contact email; timer health and
certificate expiry should be monitored by server operations.

```sh
certbot certificates
certbot renew --dry-run --run-deploy-hooks
systemctl status certbot.timer
nginx -t
```

DNS caching is independent of Nginx. Website A records do not activate email
authentication: mail A, SPF, DKIM, DMARC and provider-side PTR are documented
separately in [SMTP.md](SMTP.md). Keep existing Timeweb MX records.

References: [Django proxy HTTPS setting](https://docs.djangoproject.com/en/5.2/ref/settings/#secure-proxy-ssl-header)
and [Certbot webroot and renewal](https://eff-certbot.readthedocs.io/en/stable/using.html#webroot).
