"""
Gathers airport weather conditions to reply to an SMS with the latest update.
"""

from lib import data_grabber
from numbers import Number

# Script version
__version__ = "4" # formatted bar_hg to 2 sig figs (##.##)

CONSENT_MESSAGE = "Your SMS request provides consent to send the reply."

def get_wx(airport):
    metar_json = data_grabber.get_data(airport)
    try:
        name = metar_json['data'][0]['station']['name']
    except (KeyError, IndexError):
        return f"AirPuff Error: Unknown Airport {airport.upper()}"

    try:
        date_obs = metar_json['data'][0]['observed']
    except (KeyError, IndexError):
        date_obs = 'NA'

    try:
        flt_cat = metar_json['data'][0]['flight_category']
    except (KeyError, IndexError):
        flt_cat = "UNKNO"

    try:
        win_deg = metar_json['data'][0]["wind"].get('degrees', 0)
        win_spd_kts = metar_json['data'][0]["wind"].get('speed_kts', 0)
    except (KeyError, IndexError, TypeError):
        win_deg, win_spd_kts = 0, 0

    try:
        vis_mi = metar_json['data'][0]['visibility']['miles']
        if "Greater than 10" in vis_mi:
            vis_mi = "10+"  # Shortened format
    except (KeyError, IndexError):
        vis_mi = "UNKNO"

    try:
        ceil_code = metar_json['data'][0]['clouds'][0]['code']
        ceil_ft = metar_json['data'][0]['clouds'][0].get('feet', '12000')
    except (KeyError, IndexError):
        ceil_code, ceil_ft = "UNKNO", "12000"

    try:
        bar_hg = metar_json['data'][0]['barometer']['hg']
        # Format to two decimal places if bar_hg is a number
        bar_hg = f"{float(bar_hg):.2f}" if isinstance(bar_hg, Number) else 'UNKNO'
    except (KeyError, IndexError, ValueError, TypeError):
        bar_hg = 'UNKNO'

    airpuff_reply = (
        f"{airport.upper()}-{flt_cat.upper()}-{bar_hg}-{win_deg:03d}@"
        f"{win_spd_kts}-{vis_mi}mi-{ceil_code}|{ceil_ft}ft"
    )
    return airpuff_reply

