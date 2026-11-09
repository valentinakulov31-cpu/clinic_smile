# First-party campaign analytics

## Admin workflow

The Statistics app contains Campaign links and Statistics. Create a named link,
choose a unique ASCII slug (for example `banner1`), a site-relative destination
(`/` or `/services`), and source/medium/campaign tags. The public URL is
`https://ulybnis24.ru/r/banner1`. Download its PNG or SVG QR from the saved object
or list. SVG is suitable for print. Destination and tags can change without
changing the printed QR. The slug is read-only after creation. Disable a link
instead of deleting it; disabled links return 404.

The report filters by visit start date in Asia/Krasnoyarsk and optional campaign
link. It shows visits, approximate unique browsers, pageviews, average active
time per visit and non-canceled attributed leads. Source rows and daily totals
use the same date filter. Sources are capped at the 100 largest groups.

## Measurement and limitations

- A visit starts when the browser executes the tracker, not when a camera scans
  the QR. Redirect-only traffic is not counted. Cookies and JS are required.
- Session inactivity timeout: 30 minutes. New campaign attribution starts a new
  visit. Attribution is the campaign at the beginning of the current visit.
- Visitors are approximate distinct first-party browser identifiers, not people.
  Clearing cookies, browser privacy settings and different devices affect totals.
- Activity is accumulated only while the page is visible, focused and the last
  interaction was within 60 seconds. Heartbeats every 15 seconds and on hide
  transmit cumulative totals, so retries cannot double-count time. Closing a
  browser may lose the last heartbeat. This is measured active time, not proof
  of reading or exact elapsed time. Multiple focused tabs are not deduplicated.
- The backend verifies signed page tokens and caps active seconds at elapsed
  page time and four hours. Telemetry is best-effort and cannot be fraud-proof.
- Admin sessions, known bot user-agents, DNT and Global Privacy Control are
  excluded. A shared admin browser will not generate normal visitor statistics.
- Analytics failure never blocks form submission. A signed visit cookie links
  a successful lead to its visit without exposing patient details in reports.
- Existing historical visits cannot be reconstructed by this tracker.

## Data minimization and operations

Only path (not query or fragment), referrer hostname (not its full URL), the five
UTM fields, link, timestamps and counters are stored. Do not put personal data
into campaign labels. Random first-party cookies live for 90 days (visitor) and
30 minutes (visit); both are signed, HttpOnly, SameSite=Lax and Secure on HTTPS.
The database stores an HMAC of the visitor token, not a raw IP or browser
fingerprint. IP is used only for an in-memory, short-lived rate-limit key.
Analytics endpoints accept same-origin JSON only, despite the general API CORS
policy. Reports/QR downloads require Django admin permissions.

Run `manage.py prune_traffic` daily to delete visits/pageviews older than 180 days.
Campaign links and leads are retained; expired lead attribution becomes null.
The operator must reflect the implemented first-party analytics in its site
privacy/cookie notices and applicable consent process. No third-party analytics
provider receives this data.

## Deployment

Additive migrations create traffic tables and a nullable lead foreign key.
Deploy backend and collectstatic before the frontend script reference. The
frontend loads `/static/traffic/tracker-v1.js`. Nginx must proxy `/r/` to Django.
Keep `/api/`, `/admin/`, `/static/` and existing media/font locations unchanged.
Back up the database, source and nginx config before migration. Code rollback
does not require dropping new tables or losing collected analytics.

Checks: `python manage.py test clinic appointments traffic` and
`node --test traffic/tracker.test.cjs`. QR generation uses the maintained
[qrcode package](https://pypi.org/project/qrcode/); page-exit reporting follows
[sendBeacon guidance](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/sendBeacon).
