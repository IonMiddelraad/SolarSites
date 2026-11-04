import httpx

PVcalc_url = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc"
SHScalc_url = "https://re.jrc.ec.europa.eu/api/v5_3/SHScalc"

# api parameters
loss = 15
output_format = "json"

def send_PVcalc_request(latitude: float, longitude: float, peak_power: float):
    url = f"{PVcalc_url}?lat={latitude}&lon={longitude}&peakpower={peak_power}&loss={loss}&outputformat={output_format}"

    response = httpx.get(url)
    response.raise_for_status

    return response.json()