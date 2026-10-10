
import pyotp
import pandas as pd
from growwapi import GrowwAPI

# Provide the specific TOTP credentials from your Groww developer portal
user_api_key = "eyJraWQiOiJaTUtjVXciLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjI1NzI3OTg5NTksImlhdCI6MTc4NDM5ODk1OSwibmJmIjoxNzg0Mzk4OTU5LCJzdWIiOiJ7XCJ0b2tlblJlZklkXCI6XCJiMWU3NjRlNy0zYzY4LTRhMTEtYjNiNi02ODU5NWQ0NmJjY2RcIixcInZlbmRvckludGVncmF0aW9uS2V5XCI6XCJlMzFmZjIzYjA4NmI0MDZjODg3NGIyZjZkODQ5NTMxM1wiLFwidXNlckFjY291bnRJZFwiOlwiYTBlMDQxYzYtNmExMS00M2RhLTkzODUtYTIwYzFhYzE5ZTllXCIsXCJkZXZpY2VJZFwiOlwiYTE0OTliOGQtMGViOS01ODQ0LWI5NTgtMmMxYWExMWMxNzdiXCIsXCJzZXNzaW9uSWRcIjpcIjg1YzgxYTc0LTBjMjAtNGY0Ni05OGQ1LTU5Mjc1NDBkMjUxZFwiLFwiYWRkaXRpb25hbERhdGFcIjpcIno1NC9NZzltdjE2WXdmb0gvS0EwYkpmL0tkY3RSYURjWFJxS2pWMDYxY2hSTkczdTlLa2pWZDNoWjU1ZStNZERhWXBOVi9UOUxIRmtQejFFQisybTdRPT1cIixcInJvbGVcIjpcImF1dGgtdG90cFwiLFwic291cmNlSXBBZGRyZXNzXCI6XCIyNDA1OjIwMToyOjU4NjE6NmNkMToyYjZhOjk4NGY6NzVhNywxNzIuNzAuMTkxLjE3MywzNS4yNDEuMjMuMTIzXCIsXCJ0d29GYUV4cGlyeVRzXCI6MjU3Mjc5ODk1OTEwMixcInZlbmRvck5hbWVcIjpcImdyb3d3QXBpXCJ9IiwiaXNzIjoiYXBleC1hdXRoLXByb2QtYXBwIn0.FIt3dTbFQxMyqvWbmi3p4exB_isSZVs8S2Ia5C5eBiMk-izsyJIcgs4I_EOUupef6640ShdXFjnqQYWYCVeQeA"      # This acts as your API Key here
user_secret = "DGy%kAODm&W%zo6cA!(0YQnt83mBZ-6M"  # The alphanumeric secret key string

print("Ready to Groww!")

try:
    access_token = GrowwAPI.get_access_token(api_key=user_api_key, secret=user_secret)
    groww = GrowwAPI(access_token)
    print("✓ Success: Programmatic login session authenticated successfully!")

    historical_candles_response = groww.get_historical_candles(
        exchange=groww.EXCHANGE_NSE,
        segment=groww.SEGMENT_CASH,
        groww_symbol="NSE-RELIANCE",
        start_time="2026-07-15 09:15:00",
        end_time="2026-07-19 15:30:00",
        candle_interval=groww.CANDLE_INTERVAL_MIN_30
    )
    print(historical_candles_response)

except Exception as e:
    print(f"\n[ERROR]: {e}")