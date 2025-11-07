# 🧠 Demo NLP AI — Food & Restaurant Recommendation

## 📌 Introduction

Đây là **bản demo NLP AI** viết bằng Python, xử lý input đầu vào bằng **KeyBERT** để **trích xuất từ khóa tiếng Việt**, sau đó so sánh với **tags** được gắn trong **database nhà hàng / món ăn**.

> ⚠️ **Lưu ý:** Đây chỉ là **Proof of Concept (PoC)** – data vẫn là **raw**, nên kết quả có thể **chưa hoàn toàn chính xác**.

---

## ⚙️ Implementation Guide

### 🐍 1. Python version

KeyBERT hiện **chưa hỗ trợ Python 3.13**,  
nên **bắt buộc** chạy bằng **Python 3.11** để tránh lỗi thư viện.

📥 **Tải Python 3.11:**  
🔗 [https://www.python.org/downloads/release/python-3119/](https://www.python.org/downloads/release/python-3119/)

Khi cài nhớ tick:

* ✅ *Add Python to PATH*  
* ✅ *Install for all users*


### 🧱 2. Tạo môi trường ảo (virtual environment)

Trong thư mục project (ví dụ `D:\Python\Data`), chạy:

```bash
py -3.11 -m venv .venv
```

Kích hoạt môi trường ảo:

```bash
.\.venv\Scripts\Activate.ps1
```

Nếu thấy prompt chuyển thành:

```bash
(.venv) PS D:\Data
```

là đã kích hoạt thành công.


### 📦 3. Cài thư viện cần thiết

Sau khi .venv kích hoạt, cài toàn bộ dependencies bằng:

```bash
pip install -r requirements.txt
```

### 🚀 4. Chạy demo NLP AI

Chạy demo gợi ý nhà hàng:

```bash
python recomRes.py
```

Chạy demo gợi ý món ăn / đồ uống:

```bash
python recomFood.py
```
---
### 🧩 Notes

Vì đây là bản PoC, AI model chỉ ở mức thử nghiệm, nên kết quả còn đơn giản.

Dữ liệu nhà hàng và món ăn chỉ mang tính minh họa, không phải dữ liệu thật.

Có thể máy sẽ chạy chậm. Nếu chạy chậm, hãy kiểm tra xem torch có dùng GPU chưa:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```
