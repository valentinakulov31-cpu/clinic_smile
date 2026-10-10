# Production: 2026-10-10

The deployed source remains the `production-2026-10-10-cors` tag. A subsequent
production environment update on 2026-10-10 sets `CORS_ALLOW_ALL_ORIGINS=1`
at the owner's request. `/api/` responds with `Access-Control-Allow-Origin: *`
for any origin, including localhost and LAN development addresses. Preserve
this environment setting when preparing future releases. Admin CSRF and
cross-origin credential restrictions are unchanged. No migrations were added.

If `CORS_ALLOW_ALL_ORIGINS=0`, the explicit `CORS_ALLOWED_ORIGINS` list and
`CORS_ALLOW_LOCALHOST` setting apply again. `CORS_ALLOW_LOCALHOST=1` allows
HTTP/HTTPS on `localhost`, `127.0.0.1` and `[::1]` with any port.

Local clients should use `https://ulybnis24.ru/api/` directly, including the
trailing slash on endpoints, or the frontend repository's development proxy.
Use the canonical HTTPS domain as the API base URL to avoid redirects.

## Previous Release: 2026-10-09

The `production-2026-10-09-https` tag adds the domain and HTTPS configuration
on top of the notification release. See [DOMAIN.md](DOMAIN.md).

The `production-2026-10-09` tag records the source for the email-notification
release. It adds private, validated admin recipients and a local SMTP backend.
Migration `0006_site_settings_notification_emails` only adds a JSON column;
it does not replace or reseed existing content. See [SMTP.md](SMTP.md) for
DNS activation and outgoing mail operations.

## Previous Snapshot: 2026-10-05

The `production-2026-10-05` Git tag records the backend source running on
`201.24.63.92`. All 44 deployed source files were compared with the local source
using SHA-256 after normalizing CRLF/LF line endings. They matched. The nginx
configuration in `deploy/nginx.conf` also matched the live configuration.

## Current Deployment

- Website: https://ulybnis24.ru/
- Admin: https://ulybnis24.ru/admin/
- Backend release: `/opt/clinic_smile/releases/20261010-cors`
- Previous backend release: `/opt/clinic_smile/releases/20261009-domain`
- Active backend link: `/opt/clinic_smile/app`
- Python environment: `/opt/clinic_smile/venv`
- Service: `clinic_smile` (gunicorn under systemd)
- Database: PostgreSQL
- Uploaded files: `/opt/clinic_smile/shared/media`
- Frontend repository: https://github.com/Markywa/ulibnis
- Frontend release: `/opt/ulibnis_front/releases/20261009-fonts`
- Previous frontend release: `/opt/ulibnis_front/releases/20261009-notifications`
- Active frontend link: `/opt/ulibnis_front/current`
- Pre-release database, uploads and nginx backup: `/opt/clinic_smile/backups/20261009-notifications`
- Pre-HTTPS environment and nginx backup: `/opt/clinic_smile/backups/20261009-domain`
- Pre-CORS database, environment and source backup: `/opt/clinic_smile/backups/20261010-cors`
- Environment backup before allowing all API origins: `/opt/clinic_smile/backups/20261010-cors-all`

Production secrets remain in the server's `.env`. Database contents, uploaded
files, environment files and test uploads must not be committed.

## Source Reconciliation

This backend was originally deployed from a working directory containing
uncommitted changes based on `de07d87`. GitHub subsequently contained the
divergent commits `39ebb71` and `12704d2`. Their service-block schema and migration
history do not match the live database.

The production snapshot is authoritative for the current application. The
reconciliation merge preserves the earlier GitHub commits in history while
retaining the verified production tree. It does not apply the divergent
migrations or replace live database contents. Any feature from those commits
must be ported separately onto the current schema.

## Verification

On 2026-10-05, `python manage.py test clinic appointments --noinput` passed all
27 tests using an isolated local test database. The deployed API, admin login,
admin static files and media were also checked during the frontend release.

## Future Releases

1. Commit and push the intended source. Record the exact commit being deployed.
2. Build and test from a clean checkout of that commit.
3. Back up PostgreSQL and uploads, and inspect the migration plan.
4. Prepare a new release directory with the existing server environment and
   shared media. Collect static files and apply only reviewed migrations.
5. Switch the active release link, restart the service and check API, admin,
   static files and frontend behavior. Keep the previous release for rollback.

Do not use `migrate --fake`, reseed production, or replace the database to resolve
the historical migration divergence.
