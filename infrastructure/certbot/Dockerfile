# Patched certbot + GoDaddy DNS plugin.
#
# Why this exists: miigotu/certbot-dns-godaddy:latest (frozen Jan 2024) ships
# dns-lexicon 3.17.x, whose GoDaddy provider calls the API with the FULL
# requested name as the zone. For subdomain wildcards like
# '*.qa.afcsacramento.org' that means GET /v1/domains/qa.afcsacramento.org,
# which GoDaddy 404s because only 'afcsacramento.org' is a registered zone
# (certbot aborts on the first 404 instead of falling back — see miigotu
# discussion #75). dns-lexicon >=3.18 strips subdomain parts via tldextract
# and queries the real root zone, so upgrading it fixes the issue.
#
# Build:  docker build -t certbot-godaddy-fixed infrastructure/certbot
# Run:    docker compose --profile certbot run --rm certbot
#         (or override the domains, e.g.
#          docker compose --profile certbot run --rm certbot \
#            certbot certonly ... -d 'qa.afcsacramento.org' -d '*.qa.afcsacramento.org')

FROM miigotu/certbot-dns-godaddy:latest

RUN pip install --no-cache-dir -U "dns-lexicon==3.25.*"
