from firebase_admin import messaging

from .models import FCMDevice


def send_fcm_multicast(tokens, title, body):
    if tokens:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            tokens=tokens,
        )
        return messaging.send_each_for_multicast(message)
    return None


def deactivate_invalid_tokens(tokens, response):
    """Помечает невалидные FCM токены как не активные."""
    invalid_tokens = []

    for idx, resp in enumerate(response.responses):
        if not resp.success:
            error_code = resp.exception.code if resp.exception else None

            if error_code in [
                "registration-token-not-registered",
                "invalid-argument",
            ]:
                invalid_tokens.append(tokens[idx])

    if invalid_tokens:
        FCMDevice.objects.filter(
            token__in=invalid_tokens
        ).update(is_active=False)

