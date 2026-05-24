import re

TSHIRT_AND_SHORTS_ICON_PATH = "images/tshirt_and_shorts.png"
TSHIRT_AND_LONG_PANTS_ICON_PATH = "images/tshirt_and_long_pants.png"
LONG_SHIRT_AND_LONG_PANTS_ICON_PATH = "images/long_shirt_and_long_pants.png"
UNKNOWN_CLOTHING = "images/unknown_clothing.png"


def choose_clothing_icon(forecast, date):
  # Extract Min temperature
  min_match = re.search(r"Min\s+(\d+)", forecast)
  min_temp = int(min_match.group(1)) if min_match else None

  # Extract Max temperature
  max_match = re.search(r"Max\s+(\d+)", forecast)
  max_temp = int(max_match.group(1)) if max_match else None

  if max_temp is None:
    return UNKNOWN_CLOTHING


  # Between May and November, always wear long pants
  if is_april_to_november(date):
    if max_temp < 21:
      return LONG_SHIRT_AND_LONG_PANTS_ICON_PATH
    
    if max_temp < 26:
       return TSHIRT_AND_LONG_PANTS_ICON_PATH

    return LONG_SHIRT_AND_LONG_PANTS_ICON_PATH


  if max_temp < 19:
    return LONG_SHIRT_AND_LONG_PANTS_ICON_PATH

  if max_temp >= 24:
    return  TSHIRT_AND_SHORTS_ICON_PATH

  return TSHIRT_AND_LONG_PANTS_ICON_PATH


def is_april_to_november(date) -> bool:
  return 4 <= date.month <= 11

