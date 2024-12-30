"""Constants used in bot detection and user agent analysis."""

# Operating systems that indicate mobile devices
MOBILE_OS = {
    'iOS',
    'Android',
    'Windows Phone',
    'BlackBerry'
}

# Browser/UA strings that indicate bots
BOT_INDICATORS = {
    'Bot',
    'Spider',
    'Crawler',
    'Robot',
    'Apache-HttpClient',
    'Python-urllib',
    'curl',
    'Wget'
}

# Required browser headers for fingerprinting
BROWSER_HEADERS = [
    'accept-language',
    'accept-encoding',
    'sec-fetch-dest',
    'sec-fetch-mode',
    'sec-fetch-site',
    'sec-ch-ua'
]