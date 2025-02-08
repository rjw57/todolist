from social_core.exceptions import AuthForbidden


def enforce_hosted_domain(backend, user, response, *args, **kwargs):
    """
    A pipeline for use with django-social-auth's Google OAuth2 support which enforces that the
    signed in user is a member of one of the WHITELISTED_HOSTED_DOMAINS.

    """
    hosted_domain = response.get("hd")
    whitelist = backend.setting("WHITELISTED_HOSTED_DOMAINS", None)
    if whitelist is not None and hosted_domain not in whitelist:
        raise AuthForbidden(backend)
