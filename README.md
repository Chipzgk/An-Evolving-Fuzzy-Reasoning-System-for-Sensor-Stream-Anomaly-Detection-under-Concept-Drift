# An Evolving Fuzzy Reasoning System for Sensor Stream Anomaly Detection under Concept Drift

**Hệ thống mờ tự tiến hóa phát hiện bất thường dưới Concept Drift.** Đồ án môn Hệ thống thông minh (Thạc sĩ CNTT).

Hệ suy diễn mờ Mamdani (5 cảm biến, 12 luật) chấm điểm bất thường cho từng mẫu của luồng dữ liệu cảm biến. ADWIN theo dõi chuỗi điểm để phát hiện trôi dạt mà không cần nhãn. Khi có cảnh báo, hệ thống thu một buffer 200 mẫu không nhãn rồi tịnh tiến hàm thuộc (MF) của các biến bị trôi dạt, giữ nguyên luật và ngưỡng.

> **Phạm vi khoa học.** Dữ liệu AI4I 2020 không có concept drift tự nhiên. Drift trong đề tài là **dịch chuyển phân phối cảm biến có kiểm soát** (tiêm vào RPM và Torque). Nhãn không đổi, nên $P(Y|X)$ không được chứng minh là thay đổi. Xem `docs/phase-08…` §3.3.

## Pipeline

```
Sensor stream → Static/Evolving Mamdani FIS → anomaly score A(t) → τ = 0.67 → Normal / Anomaly
                                       ↑                     ↓
                     MF translation ← buffer W=200 ← ADWIN (unsupervised)
```

## Cấu trúc

```
data/ai4i2020.csv            UCI AI4I 2020 (10 000 mẫu)
src/                         package dùng lại cho mọi notebook từ Phase 9
  data.py fuzzy.py drift.py evolving.py evaluation.py
notebooks/01 … 08            Phase 1–8 (đã đóng băng, chạy bằng kernel drift_env)
notebooks/09 …               Phase 9+ (import src/)
docs/phase-XX-*.md           báo cáo từng phase
results/*.csv, figures/*.png kết quả và hình của Phase 9+
scripts/reproduce_core.py    tái lập bảng E1–E5b trong ~10 giây
```

## Cài đặt và chạy

```bash
pip install -r requirements.txt
python scripts/reproduce_core.py      # kiểm tra nhanh: phải in "ALL FROZEN RESULTS REPRODUCED"
jupyter notebook notebooks/           # chạy notebook theo thứ tự số
```

**Lưu ý Windows:** trên máy tác giả, extension Rust của `river` bị Windows Smart App Control chặn trong môi trường Anaconda base (Python 3.13). Phase 5 trở đi dùng conda env riêng:

```bash
conda create -n drift_env python=3.11 && conda activate drift_env
pip install -r requirements.txt && python -m ipykernel install --user --name drift_env --display-name "Python (drift_env)"
```

Notebook 09 trở đi đã được thực thi lại trên Linux (Python 3.10, river 0.22) và cho kết quả trùng khớp với Phase 5–8 (river 0.26.1).

## Kết quả chính (toàn luồng N = 2000, 39 ca lỗi, τ = 0.67)

| ID | Scenario | Model | TP | FP | FN | Precision | Recall | F1 | FPR |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 | Control | Static | 13 | 34 | 26 | 0.277 | 0.333 | 0.302 | 0.017 |
| E2 | Control | Evolving | 13 | 34 | 26 | 0.277 | 0.333 | 0.302 | 0.017 |
| E3 | Sudden | Static | 18 | 114 | 21 | 0.136 | 0.462 | 0.211 | 0.058 |
| E4 | Sudden | Evolving | 15 | 56 | 24 | 0.211 | 0.385 | 0.273 | 0.029 |
| E5a | Gradual | Static | 18 | 113 | 21 | 0.137 | 0.462 | 0.212 | 0.058 |
| E5b | Gradual | Evolving | 14 | 61 | 25 | 0.187 | 0.359 | 0.246 | 0.031 |

Ở cửa sổ sau thích nghi, hệ Evolving trên luồng Sudden **khớp chính xác** hệ gốc trên luồng không drift (TP 8 / FP 6 / FN 7). Xem `docs/phase-10…` §5.1.

## Tài liệu theo phase

| Phase | Nội dung |
| --- | --- |
| 1, 1.5 | Khám phá dữ liệu, giao thức split tuần tự |
| 2.1–2.4 | Thiết kế MF, luật, động cơ Mamdani |
| 3 | Chọn ngưỡng trên Validation, đánh giá Static |
| 4 | Luồng Control / Sudden / Gradual |
| 5 | ADWIN trên chuỗi điểm bất thường |
| 6 | Giao thức prequential, phạm vi thích nghi |
| 7 | Evolving FIS (tịnh tiến MF dựa trên buffer) |
| 8 | Tái tạo độc lập, audit, trực quan hóa |
| 9 | Module hóa `src/`, ADWIN live, **E2**, stress test báo động nhầm |
| 10 | Latency, adaptation time, phân tích theo cửa sổ |

Dữ liệu: S. Matzka, *AI4I 2020 Predictive Maintenance Dataset*, UCI Machine Learning Repository, https://doi.org/10.24432/C5HS5C
