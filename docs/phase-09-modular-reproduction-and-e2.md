# Phase 9 — Module hóa, Tái lập Kết quả và Thí nghiệm E2 (Control + Evolving)

## 1. Mục tiêu

Phase 8 để lại 2 khoảng trống chính: (1) thiếu thí nghiệm **E2 = Control + Evolving Fuzzy**, nên chưa có số liệu cho luận điểm "khi không có drift, Static và Evolving tương đương"; (2) notebook 08 **hard-code** mốc ADWIN (`ADWIN_SUDDEN = 1183`, `ADWIN_GRADUAL = 1247`) lấy từ Phase 5 thay vì chạy lại detector. Phase 9 xử lý cả hai, đồng thời tách logic thành package `src/` như cấu trúc dự kiến ban đầu.

- Notebook: [`notebooks/09_modular_reproduction_and_e2.ipynb`](../notebooks/09_modular_reproduction_and_e2.ipynb)
- Kết quả: `results/09_experiment_matrix.csv`, `results/09_false_alarm_stress.csv`
- Hình: `figures/09_score_trajectories_all.png`

## 2. Package `src/`

| Module | Nội dung | Nguồn |
| --- | --- | --- |
| `src/data.py` | Nạp dữ liệu, split tuần tự 6000/2000/2000, tạo 3 luồng Control/Sudden/Gradual; hàm tiêm noise và missing (dùng ở Phase 11) | Phase 1.5, 4, 8.3 |
| `src/fuzzy.py` | 15 MF, 12 luật Mamdani, ngưỡng τ = 0.67, suy diễn min–min–max + centroid; hàm `explain()` trả về luật được kích hoạt | Phase 2, 8.4–8.5 |
| `src/drift.py` | Bao ADWIN của River (δ = 0.002) | Phase 5 |
| `src/evolving.py` | Tịnh tiến MF dựa trên buffer $W=200$ + vòng lặp prequential *test → predict → detector → buffer/adapt* | Phase 7, 8.8 |
| `src/evaluation.py` | Confusion matrix, Precision/Recall/F1/FPR/FNR/Specificity/Balanced Accuracy | Phase 3, 8.9 |

Không thay đổi thuật toán nào so với notebook 08. Mục đích duy nhất là tái sử dụng và kiểm chứng.

## 3. Kết quả tái lập

| Kiểm tra | Kỳ vọng (Phase 5/8) | `src/` + ADWIN live | Kết quả |
| --- | --- | --- | --- |
| Mean static score Control / Sudden / Gradual | 0.315161 / 0.381982 / 0.382425 | 0.315161 / 0.381982 / 0.382425 | PASS |
| ADWIN Control | `[]` | `[]` | PASS |
| ADWIN Sudden | `[1183]` | `[1183]` | PASS |
| ADWIN Gradual | `[1247]` | `[1247]` | PASS |
| 5 confusion matrix đã đóng băng (Phase 8.9) | TP/TN/FP/FN | trùng khớp 5/5 | PASS |
| Độ dịch MF (Sudden) | ΔRPM = −156.2142, ΔTorque = +7.3015 | như kỳ vọng | PASS |

Vì chạy **ADWIN live** vẫn ra đúng 1183/1247, việc notebook 08 hard-code hai hằng số này không làm sai kết quả. Tuy vậy, từ Phase 9 trở đi mọi thí nghiệm đều chạy detector thật.

**Môi trường:** Phase 9 được thực thi trên Linux, Python 3.10.12, numpy 2.2.6, pandas 2.3.3, **river 0.22.0**. Phase 5 dùng river 0.26.1 trên Windows. Hai phiên bản River cho cùng mốc phát hiện trên dữ liệu này, nhưng đây là quan sát trên dữ liệu này, không phải bảo đảm chung.

## 4. Ma trận thực nghiệm đầy đủ (6/6 tổ hợp)

Toàn luồng $N=2000$, $\tau=0.67$, 39 mẫu lỗi:

| ID | Scenario | Model | TP | TN | FP | FN | Precision | Recall | F1 | FPR | Balanced Acc. |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 | Control | Static | 13 | 1927 | 34 | 26 | 0.2766 | 0.3333 | 0.3023 | 0.0173 | 0.6580 |
| **E2** | **Control** | **Evolving** | **13** | **1927** | **34** | **26** | **0.2766** | **0.3333** | **0.3023** | **0.0173** | **0.6580** |
| E3 | Sudden | Static | 18 | 1847 | 114 | 21 | 0.1364 | 0.4615 | 0.2105 | 0.0581 | 0.7017 |
| E4 | Sudden | Evolving | 15 | 1905 | 56 | 24 | 0.2113 | 0.3846 | 0.2727 | 0.0286 | 0.6780 |
| E5a | Gradual | Static | 18 | 1848 | 113 | 21 | 0.1374 | 0.4615 | 0.2118 | 0.0576 | 0.7020 |
| E5b | Gradual | Evolving | 14 | 1900 | 61 | 25 | 0.1867 | 0.3590 | 0.2456 | 0.0311 | 0.6639 |

## 5. E2 — Diễn giải

- ADWIN không phát cảnh báo nào trên Control, nên số lần thích nghi = 0 và quỹ đạo điểm của E2 **trùng tuyệt đối** E1 (sai khác lớn nhất = 0.0).
- Kết luận được phép rút ra: *trên luồng Control của thí nghiệm này, cơ chế Evolving không làm thay đổi hệ thống, vì detector không báo động giả.*
- Kết luận **không** được rút ra: "Evolving luôn vô hại khi không có drift". Tính vô hại phụ thuộc hoàn toàn vào việc detector không báo nhầm. Mục 6 cho thấy điều gì xảy ra nếu detector báo nhầm.

## 6. Stress test — Detector báo nhầm trên Control

Ép một cảnh báo giả (thay ADWIN bằng `FixedDetections`) trên luồng Control, không có drift thật:

| Báo nhầm tại t | Thích nghi tại t | ΔRPM | ΔTorque | TP | FP | FN | F1 | FPR |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — (E1) | — | 0 | 0 | 13 | 34 | 26 | 0.3023 | 0.0173 |
| 300 | 500 | −32.56 | +1.046 | 8 | 27 | 31 | 0.2162 | 0.0138 |
| 700 | 900 | −33.29 | +0.348 | 8 | 29 | 31 | 0.2105 | 0.0148 |
| 1000 | 1200 | +2.09 | −0.974 | 13 | 36 | 26 | 0.2955 | 0.0184 |
| 1400 | 1600 | −21.00 | +0.692 | 10 | 32 | 29 | 0.2469 | 0.0163 |

**Phát hiện quan trọng:** một lần thích nghi không cần thiết **không vô hại**. Ở 3/4 trường hợp, TP giảm từ 13 xuống 8–10 và F1 giảm tới 0.09. Nguyên nhân: độ dịch được tính so với **tâm MF MEDIUM thiết kế** (RPM: 1551.33 rpm), không so với phân phối gần nhất. Trong khi đó, trung bình RPM của từng cửa sổ 200 mẫu trên Control dao động khoảng 1518–1553 rpm, nên cơ chế luôn "kéo" MF dù không có drift. Đây là giới hạn của heuristic, cần nêu trong báo cáo. Hướng cải thiện (chưa thực hiện): chỉ dịch khi $|\Delta_v|$ vượt một ngưỡng có ý nghĩa. Phase 11 thử nghiệm một biến thể như vậy (auto variable selection).

## 7. Đính chính tài liệu các phase trước

1. **Phase 7, mục 3.3:** các con số trung gian bị ghi sai, còn độ dịch cuối cùng thì đúng. Giá trị thực:
   - Tâm MF MEDIUM: $C_{\text{RPM}} = 1551.3342$ (không phải 1538.00), $C_{\text{Torque}} = 40.0000$ (không phải 39.94).
   - Trung bình buffer Sudden: RPM = 1395.12, Torque = 47.3015. Trung bình buffer Gradual: RPM = 1389.375, Torque = 48.053.
   - Độ dịch $\Delta = -156.2142 / +7.3015$ (Sudden) và $-161.9592 / +8.0530$ (Gradual) **đúng**, nên kết quả thực nghiệm không bị ảnh hưởng.
2. **Phase 8, mục 2.1:** split Train/Validation đã được sửa về 6000/2000 (đính chính ghi ngay trong doc Phase 8).
3. **Phase 8 notebook:** mốc ADWIN là hằng số lấy từ Phase 5 chứ không phải chạy lại. Phase 9 đã chạy lại và xác nhận trùng.

## 8. Kết luận Phase 9

- Ma trận thực nghiệm core đã **đủ 6/6** tổ hợp (E1–E5b).
- Toàn bộ kết quả đóng băng được tái lập chính xác bằng pipeline module hóa và ADWIN chạy thật.
- Luận điểm "khi không có drift, Static ≈ Evolving" đã có số liệu, **kèm điều kiện** detector không báo nhầm. Stress test cho thấy báo nhầm có thể làm giảm Recall.
