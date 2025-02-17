python -m calwarn \
  --token="$(cat ~/Sync/keys/telegram/calwarn)" \
  --chat_id="-1002495133954" \
  --ics="https://www.skysports.com/calendars/football/fixtures/teams/arsenal" \
  --tmpl='{{SUMMARY}} at {{LOCATION}}, {e.start}' \
  --spec='days=7,location=Emirates Stadium'
