# Phase 14 (Bonus) — Dashboard Smart Factory Monitoring và Explainability

## 1. Chạy demo

```bash
pip install -r requirements.txt
streamlit run app.py                 # mở http://localhost:8501
# tùy chọn: bắt đầu ở một thời điểm cụ thể
DEMO_T=1600 streamlit run app.py     # PowerShell: $env:DEMO_T=1600; streamlit run app.py
```

Mọi số liệu trên dashboard được **tính trực tiếp** bằng `src/`, cùng pipeline với notebook 09–13, không có số nào được gõ tay. Sidebar cho phép chọn kịch bản (Sudden / Gradual / Control), mức nhiễu và seed, hệ đang vận hành (Evolving / Static), thời điểm t, và nút **▶ Phát** để luồng chạy tự động.

Ảnh chụp màn hình (Sudden Drift, t = 1600): `figures/14_dashboard_screen1.png` … `screen5.png`.

## 2. Năm màn hình (theo "Demo dự kiến" của kế hoạch)

| Màn | Nội dung | Nguồn số liệu |
| --- | --- | --- |
| 1 · Giám sát luồng | Giá trị 5 cảm biến tại t, anomaly score, trạng thái ✓ NORMAL / ⚠ ANOMALY (icon + chữ, không chỉ dựa vào màu), đồ thị score 300 mẫu gần nhất với ngưỡng τ, cảnh báo và lỗi thật (ghi rõ là ground truth chỉ để đánh giá) | `PrequentialRunner` |
| 2 · Concept drift | Mô tả environment change mô phỏng; thông báo **"Concept drift detected at t = 1183"** chỉ xuất hiện khi t ≥ thời điểm ADWIN phát hiện; vùng buffer W = 200; trung bình trượt RPM/Torque | ADWIN live |
| 3 · Evolving fuzzy | MF của RPM/Torque trước (nét liền) và sau (nét đứt) thích nghi, ΔRPM/ΔTorque ước lượng (chỉ hiện khi đã thích nghi xong), số luật 12 → 12, bảng 12 luật IF–THEN | `events`, `grid_mfs` |
| 4 · Static vs Evolving | Bảng metric theo đoạn A/B/C tính tới thời điểm t, kèm **Control reference** ở đoạn C; FP tích lũy theo thời gian; grouped bar toàn luồng | `evaluate` |
| 5 · Explainability | Với mẫu tại t: term trội và độ thuộc của từng biến → các luật được kích hoạt kèm α → tập mờ đầu ra (max–min) và centroid = score → so với τ | `FuzzySystem.explain` |

Ví dụ màn 5 (Sudden, t = 1100, trước khi thích nghi):

```
Air Temp = 297.3 → LOW (1.00) · Process Temp = 308.2 → LOW (0.88) · Rpm = 1296 → LOW (1.00)
Torque = 61.5 → HIGH (1.00) · Tool Wear = 7 → LOW (1.00)
Luật kích hoạt: R5  IF rpm is LOW AND torque is HIGH THEN anomaly is MEDIUM   (α = 1.00)
→ centroid = 0.500 < τ = 0.67 → ✓ NORMAL
```

## 3. Kiểm thử

- Smoke test bằng `streamlit.testing.v1.AppTest`: 3 kịch bản × 2 hệ × 3–4 thời điểm, cộng thêm nhiễu 0.2. Không có exception.
- Score mà màn 5 giải thích **trùng** với score trong log prequential tại cùng t: đã kiểm tra ở t = 1300, 1600, 1999. Dashboard dùng đúng tri thức mà hệ thống có *tại thời điểm đó*: trước khi thích nghi dùng MF gốc, sau đó dùng MF đã dịch.
- Chụp màn hình bằng Chromium headless (Streamlit 1.64, River 0.26.1) để kiểm tra bố cục. Lỗi hiển thị ΔRPM/ΔTorque *trước khi* hệ thống thích nghi (lộ thông tin tương lai) đã được phát hiện và sửa ở bước này.

## 4. Giới hạn

- Dashboard là **mô phỏng phát lại** (replay) một luồng đã tính trước, không kết nối cảm biến thật.
- Vết cắt thẳng đứng ở mép phải của MF HIGH (RPM) sau khi dịch là artifact của việc dịch trên lưới hữu hạn (μ = 0 ngoài universe). Không có mẫu nào rơi vào vùng này trong mọi kịch bản đã chạy, kể cả khi có nhiễu: RPM lớn nhất sau thích nghi là 2521.8, còn điểm cắt ở ≥ 2724.
- Chạy trên Windows cần môi trường có `river` (xem README về `drift_env`).
