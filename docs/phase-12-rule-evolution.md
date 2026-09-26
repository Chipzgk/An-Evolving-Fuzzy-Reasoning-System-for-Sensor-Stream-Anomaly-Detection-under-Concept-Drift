# Phase 12 (Bonus) — Rule-level Evolution: Thêm / Bớt Luật với Nhãn Phản hồi Trễ

## 1. Mục tiêu và khác biệt về thiết lập

Theo thứ tự độ khó của kế hoạch ban đầu (1. cập nhật MF, 2. cập nhật luật, 3. thêm/bớt luật), Phase 7 mới làm bước 1. Phase này thử bước 3.

- Notebook: [`notebooks/12_rule_evolution.ipynb`](../notebooks/12_rule_evolution.ipynb), module `src/rule_evolution.py`
- Kết quả: `results/12_naive_rule_add.csv`, `results/12_validation_grid.csv`, `results/12_test_rule_evolution.csv`. Hình: `figures/12_rule_count_timeline_validation.png`

> [!IMPORTANT]
> Để biết một luật "tốt" hay "xấu" thì phải biết cảnh báo của nó đúng hay sai, tức là **cần nhãn**. Phase 12 giả định nhãn của $x_t$ về hệ thống sau `label_delay` bước (0 hoặc 200), ví dụ sau khi kiểm tra hoặc sửa chữa máy. Nhãn chỉ được dùng để sửa rule base **từ lúc nó về trở đi**, còn $x_t$ đã được chấm điểm bằng rule base cũ (prequential). Đây là thiết lập **có giám sát trễ**, khác bản chất với cơ chế **không giám sát** của Phase 7. Không được gộp hai cơ chế thành một tuyên bố "hệ thống tự tiến hóa không cần nhãn".

## 2. Cơ chế

- **ADD:** khi một ca lỗi bị bỏ sót (score < τ), lấy term trội (khác MEDIUM) của từng biến ở mẫu đó và sinh các luật ứng viên `IF <2–3 term> THEN anomaly is HIGH`. Một ứng viên chỉ được thêm khi qua **quality gate** trên các mẫu đã có nhãn trong quá khứ (cửa sổ 1000 mẫu): kích hoạt mạnh (α ≥ 0.5) ít nhất 3 lần, trúng ít nhất 2 ca lỗi, precision ≥ ngưỡng. Mỗi sự kiện thêm tối đa 1 luật, tổng tối đa 30 luật.
- **REMOVE:** luật có hệ quả MEDIUM/HIGH bị bỏ khi, trong ≥ 20 cảnh báo mà nó kích hoạt mạnh, tỉ lệ cảnh báo đúng < ngưỡng. Luật LOW không bao giờ bị bỏ.

## 3. Kết quả

### 3.1. Không có quality gate thì thêm luật bị overfit

Nếu thêm luật ngay từ một mẫu lỗi bị bỏ sót (chỉ để minh họa, chạy trên Test, MF adaptation bật):

| Scenario | Luật thêm | Luật cuối | TP | FP | F1 | FPR | Tham chiếu MF-only F1 / FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Control | 14 | 26 | 17 | 122 | 0.191 | 0.062 | 0.302 / 0.017 |
| Sudden | 14 | 26 | 20 | 182 | 0.166 | 0.093 | 0.273 / 0.029 |
| Gradual | 12 | 24 | 22 | 213 | 0.161 | 0.109 | 0.246 / 0.031 |

TP tăng (bắt thêm 2–8 ca lỗi), nhưng FP tăng gấp 3–4 lần. Nhiều luật sinh ra chứa `air_temp is LOW`, do nhiệt độ của đoạn Test vốn thấp tự nhiên, nên chúng bắt nhầm mẫu bình thường. Đây là lý do cần quality gate.

### 3.2. Chọn siêu tham số trên Validation

Lưới 5 (remove) × 3 (add) cấu hình, MF adaptation luôn bật, chạy trên 3 luồng Validation (mỗi luồng 45 ca lỗi, tiêm drift theo cùng giao thức). Năm cấu hình tốt nhất theo F1 trung bình:

| Remove (precision <) | Add gate (precision ≥) | F1 Control | F1 Sudden | F1 Gradual | Mean F1 | Mean FPR | Luật cuối |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| off | **0.3** | 0.204 | 0.213 | 0.208 | **0.208** | 0.043 | 14 / 14 / 14 |
| 0.10 | 0.2 | 0.202 | 0.199 | 0.208 | 0.203 | 0.055 | 14 / 14 / 14 |
| 0.10 | off | 0.211 | 0.194 | 0.198 | 0.201 | 0.037 | 12 / 12 / 10 |
| off (MF-only) | off | 0.211 | 0.194 | 0.178 | 0.194 | 0.041 | 12 / 12 / 12 |
| 0.15 | off | 0.268 | 0.125 | 0.119 | 0.171 | 0.018 | 10 / 7 / 7 |

Cấu hình được chọn là **add gate 0.3, không remove**. Trên Validation, nó thêm đúng 2 luật, đọc được như tri thức chuyên gia:

- `N1: IF process_temp is HIGH AND torque is HIGH AND tool_wear is HIGH THEN anomaly is HIGH` (trong lịch sử: kích hoạt 5 lần, 3 ca lỗi)
- `N2: IF air_temp is HIGH AND process_temp is HIGH AND torque is HIGH THEN anomaly is HIGH` (kích hoạt 10 lần, 3 ca lỗi)

Hai luật này nâng F1 trên Sudden và Gradual của Validation (0.194 → 0.213 và 0.178 → 0.208) nhưng làm giảm nhẹ F1 trên Control (0.211 → 0.204). Ngưỡng remove cao (≥ 0.15) xóa luôn các luật phát hiện chính (R4, R5, R8) và làm Recall sụp đổ. Cơ chế remove **rất nhạy** với ngưỡng.

### 3.3. Áp dụng lên Test

Với cấu hình đã chọn (add gate 0.3, delay 0 hoặc 200), **không có luật nào được thêm hay bỏ trên cả 3 luồng Test**, nên kết quả trùng khớp với MF-only (E2/E4/E5b) và Static (E1/E3/E5a). Lý do: Test chỉ có 39 ca lỗi, và không ứng viên nào đạt đồng thời ≥ 2 ca lỗi trúng và precision ≥ 0.3 trên dữ liệu đã có nhãn.

> [!NOTE]
> Khi khám phá trước (không dùng để kết luận, vì đó là nhìn vào Test), ngưỡng remove 0.10 xóa luật R5 ở t = 759 và thay đổi kết quả Test: Gradual MF + Rule F1 = 0.252 so với 0.246; Sudden F1 = 0.248 so với 0.273. Tác động không nhất quán giữa hai kịch bản. Cấu hình này cũng không được chọn trên Validation. Khi bỏ R5 (hệ quả MEDIUM), centroid dịch lên phía HIGH, nên hiệu ứng thực chất giống **hạ ngưỡng** hơn là "loại bỏ tri thức sai".

## 4. Kết luận Phase 12

1. Cơ chế thêm/bớt luật **đã được cài đặt và chạy được**, đồng thời giải thích được: mỗi thay đổi đều in ra dạng IF–THEN kèm bằng chứng lịch sử.
2. **Kết quả thực nghiệm trên Test là trung tính:** cấu hình chọn một cách công bằng trên Validation không kích hoạt thay đổi nào trên Test. Không có bằng chứng rằng rule evolution cải thiện hệ thống trong bài toán này.
3. Hai bài học có giá trị cho báo cáo: (a) thêm luật từ một mẫu đơn lẻ sẽ overfit, nên cần quality gate; (b) bớt luật trong hệ Mamdani với centroid có tác dụng phụ giống thay đổi ngưỡng. Nguyên nhân gốc là dữ liệu lỗi quá ít (39–45 ca mỗi luồng) để học luật online một cách tin cậy.
