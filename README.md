# QuakeWatch

A small, focused earthquake monitor — with a personal angle: it defaults to
the **Lake Kivu / Albertine Rift region** (Rwanda and eastern DR Congo),
a real, seismically active area near the Rwanda-DRC border, before
letting you widen the search worldwide.

This isn't a gimmick app. Real earthquakes happen in this region — including
one recorded 10 km from Cyangugu, Rwanda — and knowing recent activity in
your area has genuine, practical value.

## Features

- **Region toggle** — "Near Rwanda (Lake Kivu / Rift Valley)" or "Worldwide"
- **Minimum magnitude filter** — Any / 2.5+ / 4.5+ / 6.0+
- **Time range filter** — past day / week / month / year
- **Sort** — most recent first, or strongest first
- Each result shows location, magnitude (color-coded), depth, time,
  a plain-language note on likely impact, and a link to the full USGS report
- Friendly error handling if the data source is unreachable or returns
  something unexpected

## API used

[USGS Earthquake Hazards Program](https://earthquake.usgs.gov/) —
the FDSN Event Query API (`earthquake.usgs.gov/fdsnws/event/1/query`).
Public and free, **no API key required**. All credit for the underlying
earthquake data goes to USGS.

## Running it locally

```bash
git clone https://github.com/EnzoAsaph/quakewatch.git
cd quakewatch
python3 -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000`. No login, no API key, no config needed —
it works out of the box.

## Deployment

The app runs on two identical servers (`web-01`, `web-02`), each running the
app under `gunicorn` as a `systemd` service (`deploy/quakewatch.service`) on
port 5000, so it survives reboots and restarts automatically if it crashes.

The load balancer (`lb-01`) runs HAProxy. A dedicated frontend/backend pair
was **added** to the existing `haproxy.cfg` (see
`deploy/haproxy-quakewatch-snippet.cfg`) — it does not touch or replace the
HAProxy configuration already used for the other course project on this
same server, it just listens on a different port (`5000`) and round-robins
between `web-01:5000` and `web-02:5000`.

**Access the deployed app via the load balancer:**

```
http://3.87.222.148:5000/
```

To verify traffic is actually being balanced, each response carries an
`X-Served-By` header naming the server that handled it:

```bash
curl -sI http://3.87.222.148:5000/ | grep -i x-served-by
```

Run that a few times — it alternates between `7081-web-01` and
`7081-web-02`.

### Deployment steps taken

1. Packaged the app (`app.py`, `templates/`, `static/`, `requirements.txt`)
   and copied it to both web servers.
2. Installed Python 3's `venv`/`pip`, created a virtual environment on each
   server, and installed dependencies into it.
3. Installed the `quakewatch.service` systemd unit
   (`deploy/quakewatch.service`) on each server, which runs
   `gunicorn -w 2 -b 0.0.0.0:5000 app:app`, enabled on boot.
4. Opened port `5000` in each server's firewall (`ufw`).
5. Appended a new `frontend`/`backend` block to lb-01's `haproxy.cfg`
   (`deploy/haproxy-quakewatch-snippet.cfg`), binding port `5000` and
   load-balancing (round robin) across both web servers.
6. Verified end-to-end through the load balancer's public IP, and
   confirmed alternation with the `X-Served-By` header.

## No login required

This app has no user accounts, authentication, or API keys to configure —
it's fully public and requires no credentials to access or run.

## Challenges

- The Lake Kivu region genuinely doesn't have earthquakes every week —
  a short default time window would often show nothing on this specific
  region, which isn't a bug, just reality. Added a "past year" option so
  the regional view reliably has real historical data to show.
- Keeping the new load balancer configuration for this app **additive**
  to the existing HAProxy setup (rather than editing the frontend already
  graded for another course project), by giving it its own port instead
  of sharing port 80/443.

## Credits

- Earthquake data: [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/)
- Built with [Flask](https://flask.palletsprojects.com/) and
  [Requests](https://requests.readthedocs.io/)

## Demo video

[Add your demo video link here]
