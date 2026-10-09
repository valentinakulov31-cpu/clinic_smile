# Outgoing Mail: ulybnis24.ru

Host: `201.24.63.92`. Sender: `noreply@ulybnis24.ru`.
SMTP hostname: `mail.ulybnis24.ru`.

Postfix listens only on `127.0.0.1:25`. OpenDKIM listens on
`127.0.0.1:8891`. There is no public relay, SMTP password or new inbox.
Existing inbound mail remains with Timeweb. Keep the current MX records.

## DNS Changes

TTL 3600 is suitable. Names below are relative to `ulybnis24.ru`.

| Type | Name | Value |
| --- | --- | --- |
| A | mail | 201.24.63.92 |
| TXT | @ | v=spf1 ip4:201.24.63.92 include:_spf.timeweb.ru ~all |
| TXT | _dmarc | v=DMARC1; p=none; adkim=r; aspf=r |
| TXT | site202610._domainkey | DKIM value below |

Replace the existing SPF value `v=spf1 include:_spf.timeweb.ru ~all`;
do not create a second SPF record. Keep `mx1.timeweb.ru` and `mx2.timeweb.ru`.

DKIM TXT value (one logical record; a DNS panel may split it into quoted chunks):

```text
v=DKIM1; h=sha256; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAt1VML65uLF1Dy9qiLnJ58GE51POYFPOnVnEWTXGGnfprLSCxRidL9tdKsInXt571nRuMx+wrWySdB0EjKVGqxbUdXv9fQd8RaAzMP/Ff9IBJu99G+bKcNj8tW17VycaamV9/2EU9UCRsggb2V77Xg5CSOy7v5oqImpzvZkov+uSD+WvU/S3+beCKOIrJNrPnYBzFHEmvQVfwsXblAuAEytlGcZ3R/E5/Ry97FglG9e5IhnBCq0Paotao7+Ds1hoqt+LFn26vG8JAvCnrVd7fQJAGx0pywR+id8n/oUev0H7B2Hx0gk6BCUM5EfZe+9lTiOwwN+Qr8Cx/kOlRGpk24wIDAQAB
```

In the VPS provider panel, change reverse DNS (PTR) of `201.24.63.92` to
`mail.ulybnis24.ru`. This is separate from the domain's DNS zone. Publish
the A record before requesting the PTR change.

Create or confirm `noreply@ulybnis24.ru` at the existing mail provider so
delivery failure reports have a monitored destination. Do not redirect the
domain's MX to this server.

## Application

Production environment settings:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=127.0.0.1
EMAIL_PORT=25
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=0
EMAIL_USE_SSL=0
EMAIL_TIMEOUT=10
DEFAULT_FROM_EMAIL=noreply@ulybnis24.ru
```

Recipients are stored in the private `SiteSettings.request_notification_emails`
field. Edit them in the Django admin's site settings, one address per line.
An empty list disables notifications. The public settings API excludes them.
The former `REQUEST_NOTIFICATION_EMAIL` environment variable is no longer used.

The application saves each request before submitting its notification to
Postfix. SMTP failures are logged without rejecting the saved request. Once
Postfix accepts a message it queues and retries temporary delivery failures.
Messages not accepted by local SMTP require manual follow-up from the admin;
there is no application-level retry queue. Existing requests are not emailed
retroactively.

## Server Configuration

Versioned config is in `deploy/smtp/`. Apply each `postfix-overrides.cf` entry
using `postconf -e`, install `opendkim.conf` in `/etc`, and install
`trusted.hosts` in `/etc/opendkim`. Validate with `postfix check` and
`opendkim -n -x /etc/opendkim.conf` before restarting the services.

The 2048-bit private signing key is stored only on the server at
`/etc/opendkim/keys/ulybnis24.ru/site202610.private`, owned by `opendkim`
with mode 0600. Back it up securely; never commit it. Original package
configuration is backed up in `/root/clinic-smtp-backup-20261009`.

After DNS is published, check A, SPF, DKIM, DMARC and PTR, then run:

```sh
opendkim-testkey -d ulybnis24.ru -s site202610 -vvv
postqueue -p
journalctl -u opendkim --since today
```

Use an explicitly approved recipient for an external test and inspect its
received headers for SPF/DKIM/DMARC results. DNS and local signing checks alone
do not prove inbox delivery or IP reputation.

References: [Postfix basic configuration](https://www.postfix.org/BASIC_CONFIGURATION_README.html)
and [OpenDKIM configuration](https://manpages.debian.org/bookworm/opendkim/opendkim.conf.5.en.html).
