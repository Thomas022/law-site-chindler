import hashlib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.core.exceptions import PermissionDenied


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username or kwargs.get(get_user_model().USERNAME_FIELD)
        if not identifier or password is None:
            return None

        cache_key = self._cache_key(request, identifier)
        if cache.get(f"{cache_key}:locked"):
            raise PermissionDenied("Acesso temporariamente bloqueado.")

        resolved_username = self._resolve_username(identifier)
        user = super().authenticate(
            request, username=resolved_username, password=password, **kwargs
        )
        if user is not None:
            cache.delete_many([cache_key, f"{cache_key}:locked"])
            return user

        attempts = cache.get(cache_key, 0) + 1
        if attempts >= settings.LOGIN_MAX_ATTEMPTS:
            cache.set(
                f"{cache_key}:locked", True, timeout=settings.LOGIN_LOCKOUT_SECONDS
            )
            cache.delete(cache_key)
        else:
            cache.set(cache_key, attempts, timeout=settings.LOGIN_LOCKOUT_SECONDS)
        return None

    def _resolve_username(self, identifier):
        user_model = get_user_model()
        matches = list(
            user_model._default_manager.filter(email__iexact=identifier).values_list(
                user_model.USERNAME_FIELD, flat=True
            )[:2]
        )
        if len(matches) == 1:
            return matches[0]
        return identifier

    def _cache_key(self, request, identifier):
        address = "unknown"
        if request is not None:
            address = request.META.get("REMOTE_ADDR", "unknown")
        digest = hashlib.sha256(
            f"{address}|{identifier.strip().lower()}".encode("utf-8")
        ).hexdigest()
        return f"chindler-login:{digest}"
