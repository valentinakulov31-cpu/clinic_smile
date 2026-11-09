from datetime import timedelta
import json
import re
import uuid
from urllib.parse import urlsplit

from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import CampaignLink, PageView, UTM_FIELDS, Visit

COOKIE_AGE = 90 * 86400
SESSION_AGE = 30 * 60


def campaign_redirect(request, slug):
    link = get_object_or_404(CampaignLink, slug=slug, is_active=True)
    response = HttpResponseRedirect(link.target_url())
    response["Cache-Control"] = "no-store"
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


def read_cookie(request, name, age):
    try:
        return request.get_signed_cookie(name, salt="traffic", max_age=age)
    except (KeyError, signing.BadSignature):
        return None


def visit_for_request(request):
    value = read_cookie(request, "clinic_visit", SESSION_AGE)
    try:
        visit_id = uuid.UUID(value) if value else None
    except (ValueError, TypeError):
        return None
    return Visit.objects.filter(pk=visit_id, last_seen__gte=timezone.now() - timedelta(seconds=SESSION_AGE)).first()


def clean_text(value, limit=120):
    return re.sub(r"[\x00-\x1f\x7f]", "", value)[:limit] if isinstance(value, str) else ""


def ignored(request):
    return (request.user.is_staff or request.headers.get("DNT") == "1"
            or request.headers.get("Sec-GPC") == "1"
            or bool(re.search(r"bot|crawler|spider|headless|preview|slurp", request.headers.get("User-Agent", ""), re.I)))


def set_cookie(response, name, value, age):
    response.set_signed_cookie(name, value, salt="traffic", max_age=age,
                               secure=settings.PUBLIC_SITE_URL.startswith("https:"), httponly=True, samesite="Lax")


@csrf_exempt
@require_POST
def event(request):
    # Public write-only telemetry, deliberately separate from admin sessions and CORS.
    if request.headers.get("Origin") != settings.PUBLIC_SITE_URL:
        return HttpResponse(status=403)
    if ignored(request):
        return HttpResponse(status=204)
    if request.content_type != "application/json" or len(request.body) > 4096:
        return HttpResponse(status=400)
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)
    ip = request.META.get("HTTP_X_REAL_IP", request.META.get("REMOTE_ADDR", ""))
    key = "traffic-rate:" + salted_hmac("traffic-rate", ip).hexdigest()
    if cache.add(key, 1, 60):
        count = 1
    else:
        try:
            count = cache.incr(key)
        except ValueError:
            count = 1
    if count > 180:
        return HttpResponse(status=429)
    try:
        response = record(data, request)
    except IntegrityError:
        # A concurrent replay of the same random page ID must not become a 500.
        response = HttpResponse(status=409)
    response["Cache-Control"] = "no-store"
    return response


@transaction.atomic
def record(data, request):
    now = timezone.now()
    if data.get("event") == "heartbeat":
        try:
            page_id = signing.loads(data.get("token", ""), salt="traffic-page", max_age=86400)
            seconds = data["active_seconds"]
            if type(seconds) is not int or seconds < 0:
                raise ValueError
            page = PageView.objects.select_for_update().get(pk=uuid.UUID(page_id))
        except (signing.BadSignature, ValueError, TypeError, KeyError, PageView.DoesNotExist):
            return HttpResponse(status=400)
        seconds = min(seconds, max(0, int((now - page.started_at).total_seconds())), 4 * 3600)
        delta = max(0, seconds - page.active_seconds)
        if delta:
            page.active_seconds += delta
            page.save(update_fields=["active_seconds"])
            Visit.objects.filter(pk=page.visit_id).update(active_seconds=F("active_seconds") + delta, last_seen=now)
        response = HttpResponse(status=204)
        # Refresh only this visit; a late beacon from an older tab must not change attribution.
        if read_cookie(request, "clinic_visit", SESSION_AGE) == str(page.visit_id):
            set_cookie(response, "clinic_visit", str(page.visit_id), SESSION_AGE)
        return response
    if data.get("event") != "page":
        return HttpResponse(status=400)
    try:
        page_id = uuid.UUID(data.get("page_id", ""))
        path = urlsplit(clean_text(data.get("path"), 500)).path
    except (ValueError, TypeError, AttributeError):
        return HttpResponse(status=400)
    if not path.startswith("/") or path.startswith("//") or path.split("/")[1].lower() in {"admin", "api", "static", "media", "r"}:
        return HttpResponse(status=400)
    visitor = read_cookie(request, "clinic_visitor", COOKIE_AGE) or uuid.uuid4().hex
    visitor_key = salted_hmac("traffic-visitor", visitor, algorithm="sha256").hexdigest()
    previous_page = PageView.objects.select_related("visit").filter(pk=page_id).first()
    if previous_page:
        if previous_page.visit.visitor_key != visitor_key:
            return HttpResponse(status=409)
        visit = previous_page.visit
    else:
        tags = {field: clean_text(data.get(field)) for field in UTM_FIELDS}
        link = CampaignLink.objects.filter(slug=clean_text(data.get("cl")), is_active=True).first()
        if link:
            tags = {field: getattr(link, field) for field in UTM_FIELDS}
        visit = visit_for_request(request)
        if visit and (visit.visitor_key != visitor_key or (link and visit.link_id != link.pk)
                      or (any(tags.values()) and any(getattr(visit, k) != v for k, v in tags.items()))):
            visit = None
        if not visit:
            try:
                host = urlsplit(clean_text(data.get("referrer"), 2048)).hostname or ""
            except ValueError:
                host = ""
            if host == urlsplit(settings.PUBLIC_SITE_URL).hostname:
                host = ""
            visit = Visit.objects.create(visitor_key=visitor_key, link=link, started_at=now, last_seen=now,
                                         landing_path=path, referrer_host=host[:253], **tags)
        PageView.objects.create(id=page_id, visit=visit, path=path, started_at=now)
        Visit.objects.filter(pk=visit.pk).update(page_count=F("page_count") + 1, last_seen=now)
    response = JsonResponse({"token": signing.dumps(str(page_id), salt="traffic-page")})
    set_cookie(response, "clinic_visitor", visitor, COOKIE_AGE)
    set_cookie(response, "clinic_visit", str(visit.pk), SESSION_AGE)
    return response
