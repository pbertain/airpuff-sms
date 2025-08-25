"""
Gathers airport weather conditions to reply to an SMS with the latest update.
"""

import logging
from numbers import Number
from lib import data_grabber

# Script version
__version__ = "5"  # Fixed data parsing issues

CONSENT_MESSAGE = "Your SMS request provides consent to send the reply."

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_wx(airport):
    """
    Fetches weather information for the given airport.

    Args:
        airport (str): ICAO/IATA airport code.

    Returns:
        str: Formatted weather response.
    """
    try:
        metar_json = data_grabber.get_data(airport)
    except Exception as e:
        logger.error(f"Failed to fetch data for {airport.upper()}: {str(e)}")
        return f"AirPuff Error: Could not retrieve data for {airport.upper()}"

    try:
        name = metar_json.get('data', [{}])[0].get('station', {}).get('name', "Unknown")
    except IndexError:
        name = "Unknown"

    date_obs = metar_json.get('data', [{}])[0].get('observed', 'NA')
    flt_cat = metar_json.get('data', [{}])[0].get('flight_category', 'UNKNO')

    wind_data = metar_json.get('data', [{}])[0].get('wind', {})
    win_deg = wind_data.get('degrees', 0)
    win_spd_kts = wind_data.get('speed_kts', 0)

    vis_mi = metar_json.get('data', [{}])[0].get('visibility', {}).get('miles', "UNKNO")
    if isinstance(vis_mi, str) and "Greater than 10" in vis_mi:
        vis_mi = "10+"  # Shortened format

    clouds = metar_json.get('data', [{}])[0].get('clouds', [{}])
    ceil_code = clouds[0].get('code', "UNKNO") if clouds else "UNKNO"
    ceil_ft = clouds[0].get('feet', "12000") if clouds else "12000"

    try:
        bar_hg = metar_json.get('data', [{}])[0].get('barometer', {}).get('hg', 'UNKNO')
        bar_hg = f"{float(bar_hg):.2f}" if isinstance(bar_hg, Number) else 'UNKNO'
    except (ValueError, TypeError):
        bar_hg = 'UNKNO'

    airpuff_reply = (
        f"{airport.upper()}-{flt_cat.upper()}-{bar_hg}-{win_deg:03d}@"
        f"{win_spd_kts}-{vis_mi}mi-{ceil_code}|{ceil_ft}ft"
    )

    return airpuff_reply

