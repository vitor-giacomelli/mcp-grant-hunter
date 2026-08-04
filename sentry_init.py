import sentry_sdk

sentry_sdk.init(
    dsn="https://1bc8e13cdf47a46a0379612c5a9d3687@o4511829492695040.ingest.us.sentry.io/4511834641858560",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

division_by_zero = 1 / 0
