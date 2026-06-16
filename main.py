from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(title="ZaloPay Clean History API")

# Cấu hình cố định thông tin tài khoản của bạn
ZALOPAY_URL = "https://sapi.zalopay.vn/v2/history/transactions"
HEADERS = {
    "Host": "sapi.zalopay.vn",
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_11 like Mac OS X) AppleWebKit/8615.8.1.10.2, Copyright 2003-2023 Apple Inc. (KHTML, like Gecko) Mobile/20H351 ZaloPayClient/11.6.1 ZaloPayWebClient/11.6.1 OS/16.7.11 Platform/ios Secured/true",
    "Cookie": "_ga=GA1.1.859283574.1763961477; _ga_XWW4JEB21X=GS2.1.s1781625575$o254$g1$t1781625579$j56$l0$h0; X-DRSITE=off; zalo_id=; zlp_token=3vSqzAySPUYc5s4UpgYb6KyWUHbfrPxzYuZE6C3SD2VYVFMAd7RQpXk6Z8xPJdkzGfpu3AtireHP5jnmDjKsjbvgPjvJdyk8Zy7nWcrHFocYEyyP2DDAsCmuKVcrXwXAT1mfsHY5n3wg4iNJAQ5272qfQDfjmXQoNSi7pzNdpkzG34M36jYm6; has_device_id=0",
    "Connection": "keep-alive"
}

@app.get("/api/transactions/received")
def get_received_transactions(limit: int = 20):
    """
    API tự động gọi lên ZaloPay, lọc lấy các giao dịch tiền dương (+) 
    và trả về dữ liệu JSON đã rút gọn.
    """
    try:
        # Gọi sang ZaloPay lấy data gốc
        params = {"page_size": limit}
        response = requests.get(ZALOPAY_URL, headers=HEADERS, params=params)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Không thể kết nối API ZaloPay hoặc Token hết hạn.")
            
        result = response.json()
        transactions = result.get("data", {}).get("items", [])
        
        # Mảng chứa danh sách kết quả sau khi lọc sạch
        clean_list = []
        
        for item in transactions:
            amount = item.get("amount", 0)
            sign = item.get("sign", 1) # 1 thường là dấu +, -1 là dấu -
            
            # Chỉ lấy giao dịch nhận tiền (số dương)
            if amount > 0 and sign == 1:
                clean_list.append({
                    "trans_id": item.get("trans_id", "N/A"),
                    "time": item.get("time_str", "N/A"),
                    "amount": amount,
                    "description": item.get("description", item.get("title", "Không có nội dung"))
                })
                
        return {
            "success": True,
            "total_received": len(clean_list),
            "data": clean_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

# Lệnh để chạy API trực tiếp bằng file này
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
