# =====================
# This is a Sample script that places a Buy order, waits 10 seconds, and then places a Sell order.
# =====================

import time
from growwapi import GrowwAPI

# =====================
# STEP 1: Setup
# =====================

# === Setup Groww API ===
# Please use the "Generate API key" option on the API keys page to obtain the API key and Secret.

user_api_key = "eyJraWQiOiJaTUtjVXciLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjI1NzI3OTg5NTksImlhdCI6MTc4NDM5ODk1OSwibmJmIjoxNzg0Mzk4OTU5LCJzdWIiOiJ7XCJ0b2tlblJlZklkXCI6XCJiMWU3NjRlNy0zYzY4LTRhMTEtYjNiNi02ODU5NWQ0NmJjY2RcIixcInZlbmRvckludGVncmF0aW9uS2V5XCI6XCJlMzFmZjIzYjA4NmI0MDZjODg3NGIyZjZkODQ5NTMxM1wiLFwidXNlckFjY291bnRJZFwiOlwiYTBlMDQxYzYtNmExMS00M2RhLTkzODUtYTIwYzFhYzE5ZTllXCIsXCJkZXZpY2VJZFwiOlwiYTE0OTliOGQtMGViOS01ODQ0LWI5NTgtMmMxYWExMWMxNzdiXCIsXCJzZXNzaW9uSWRcIjpcIjg1YzgxYTc0LTBjMjAtNGY0Ni05OGQ1LTU5Mjc1NDBkMjUxZFwiLFwiYWRkaXRpb25hbERhdGFcIjpcIno1NC9NZzltdjE2WXdmb0gvS0EwYkpmL0tkY3RSYURjWFJxS2pWMDYxY2hSTkczdTlLa2pWZDNoWjU1ZStNZERhWXBOVi9UOUxIRmtQejFFQisybTdRPT1cIixcInJvbGVcIjpcImF1dGgtdG90cFwiLFwic291cmNlSXBBZGRyZXNzXCI6XCIyNDA1OjIwMToyOjU4NjE6NmNkMToyYjZhOjk4NGY6NzVhNywxNzIuNzAuMTkxLjE3MywzNS4yNDEuMjMuMTIzXCIsXCJ0d29GYUV4cGlyeVRzXCI6MjU3Mjc5ODk1OTEwMixcInZlbmRvck5hbWVcIjpcImdyb3d3QXBpXCJ9IiwiaXNzIjoiYXBleC1hdXRoLXByb2QtYXBwIn0.FIt3dTbFQxMyqvWbmi3p4exB_isSZVs8S2Ia5C5eBiMk-izsyJIcgs4I_EOUupef6640ShdXFjnqQYWYCVeQeA"
user_secret = "DGy%kAODm&W%zo6cA!(0YQnt83mBZ-6M"


access_token = GrowwAPI.get_access_token(api_key = user_api_key, secret = user_secret) 
# Use access_token to initiate GrowwAPi
groww = GrowwAPI(access_token)
print("✅ Ready to Groww")

# =====================
# STEP 2: Place BUY Order
# =====================

trading_symbol = "IDEA"  #Vodafone Idea Ltd
quantity = 1    #Set the quantity you want to buy 
 

#Ensure you have sufficient funds in your Groww account for this order

try:
    # Place a MARKET BUY order
    print(f"Placing MARKET BUY order for {trading_symbol}")
    buy_order_id = groww.place_order(
        trading_symbol=trading_symbol, 
        quantity=quantity, 
        validity=groww.VALIDITY_DAY,
        exchange=groww.EXCHANGE_NSE, 
        segment=groww.SEGMENT_CASH,
        product=groww.PRODUCT_MIS,
        order_type=groww.ORDER_TYPE_MARKET,
        transaction_type=groww.TRANSACTION_TYPE_BUY
    )

    print(f"✅ BUY order placed for {trading_symbol}. Order ID: {buy_order_id['groww_order_id']}") 
    # This will print the order ID of the placed order

except Exception as e: 
    print(f"❌ Failed to place BUY order: {e}")
    exit(1)

# =====================
# STEP 3: Wait 10 seconds
# =====================
print("⏳ Waiting for 10 secs before placing SELL order...")
time.sleep(10)

# =====================
# STEP 4: Place SELL Order
# =====================

#Place a MARKET SELL order
try:
    print(f"Placing MARKET SELL order for {trading_symbol}")

    sell_order_id = groww.place_order(
        trading_symbol=trading_symbol,
        quantity=quantity,
        validity=groww.VALIDITY_DAY,
        exchange=groww.EXCHANGE_NSE,
        segment=groww.SEGMENT_CASH,
        product=groww.PRODUCT_MIS,
        order_type=groww.ORDER_TYPE_MARKET,
        transaction_type=groww.TRANSACTION_TYPE_SELL
    )

    print(f"✅ SELL order placed for {trading_symbol}. Order ID: {sell_order_id['groww_order_id']}")  
    # This will print the order ID of the placed order

except Exception as e:
    print(f"❌ Failed to place SELL order: {e}")