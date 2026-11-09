# Website analytics

Admin pages (requires `traffic.view_visit`):

- `/admin/traffic/visit/`: totals, sources and daily counts.
- `/admin/traffic/visit/sessions/`: paginated visits, filtered by date, campaign
  link, channel and optionally an anonymous browser identifier.
- `/admin/traffic/visit/sessions/<uuid>/`: ordered page views and cumulative
  active time per page. Lead links additionally require lead view/change access.

An identifier represents one browser cookie, not a verified person. Clearing
cookies, using private browsing or switching devices produces another identifier.
No IP address, page content or form values are recorded by the tracker. The source
hostname is retained, not its full URL or search query.

Active time is approximate: the tracker counts a visible, focused page while the
last interaction was less than 60 seconds ago. Heartbeats are sent every 15 seconds
and on visibility/navigation events. Delivery can be blocked or interrupted.
Zero seconds does not prove an immediate departure. Staff, recognized bots and
browsers requesting DNT/GPC are excluded. Data is retained for 180 days.

Channel classification uses `sources.py`: explicit UTM media override referrers;
recognized search/social hostnames are classified when no campaign tags override
them. An unrecognized host is a referral, and a missing referrer with no tags is
direct/unknown. Search referrers alone cannot reliably distinguish untagged paid
ads from organic results. Use `utm_medium=cpc` for paid search, `organic` for
explicit organic campaigns, and `qr` for printed QR links. `utm_term` is a supplied
campaign label, not an independently observed search query.

The journal reads the existing Visit/PageView tables and needs no additional
migration or frontend build. Historical telemetry starts when the tracker was
enabled; earlier visits cannot be reconstructed by this feature.

Tests: `python manage.py test traffic` and `node --test traffic/tracker.test.cjs`.
