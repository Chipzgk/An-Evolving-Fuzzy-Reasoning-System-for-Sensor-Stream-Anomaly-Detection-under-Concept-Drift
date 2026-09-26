# Phase 10 — Complexity, Adaptation Metrics và Phân tích theo Cửa sổ Thời gian

## 1. Mục tiêu

Hoàn tất nhóm metric mà roadmap ban đầu yêu cầu nhưng chưa đo: **Number of fuzzy rules**, **Inference latency**, **Drift detection delay** và **Adaptation time**. Đồng thời phân tích kết quả theo từng đoạn thời gian (trước drift / chưa thích nghi / sau thích nghi) và vẽ lại biểu đồ tổng kết dạng grouped bar.

- Notebook: [`notebooks/10_complexity_and_adaptation_metrics.ipynb`](../notebooks/10_complexity_and_adaptation_metrics.ipynb)
- Kết quả: `results/10_structure.csv`, `results/10_latency.csv`, `results/10_adaptation_metrics.csv`, `results/10_window_metrics.csv`, `results/10_window_c_vs_control_reference.csv`
- Hình: `figures/10_final_metrics_grouped.png`, `figures/10_window_c_vs_control_reference.png`

## 2. Độ phức tạp cấu trúc

| | Static | Evolving (Sudden/Gradual) |
| --- | ---: | ---: |
| Số luật trước → sau | 12 → 12 | 12 → 12 |
| Số MF đầu vào | 15 | 15 (6 MF của RPM/Torque được tịnh tiến) |
| Số lần thích nghi | 0 | 1 |
| Tham số bị thay đổi | 0 | 2 số thực (ΔRPM, ΔTorque) |

Cơ chế Phase 7 **không thêm/bớt luật**. Thí nghiệm rule add/remove được làm riêng ở Phase 12.

## 3. Inference latency

Đo bằng `time.perf_counter()` quanh bước chấm điểm của từng mẫu, 2.000 mẫu × 5 lần lặp (lấy median theo lần lặp). Phần cứng: Intel Core i7-1355U, Python 3.10, trong môi trường Linux ảo hóa.

| FIS | Mean (ms) | Median (ms) | p95 (ms) | p99 (ms) | Throughput (mẫu/s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Static (MF giải tích) | 0.068 | 0.065 | 0.086 | 0.102 | ≈ 14 600 |
| Evolving (MF trên lưới sau thích nghi) | 0.081 | 0.079 | 0.095 | 0.110 | ≈ 12 300 |

- Toàn bộ pipeline prequential (duyệt pandas + fuzzy + ADWIN + quản lý buffer): **≈ 0.167 ms/mẫu**.
- Một lần thích nghi (ước lượng Δ + tịnh tiến 6 MF): **≈ 0.141 ms**.

**Diễn giải:** Evolving chậm hơn Static khoảng 19% mỗi mẫu, do tra `np.interp` trên lưới 1000 điểm thay vì công thức giải tích. Cả hai đều dưới 0.2 ms/mẫu. Dữ liệu AI4I không có tần số lấy mẫu thật nên **không thể kết luận "đáp ứng thời gian thực"** cho một dây chuyền cụ thể. Chỉ có thể nói chi phí tính toán rất nhỏ so với các chu kỳ lấy mẫu cảm biến công nghiệp thông thường (mili-giây đến giây). Latency đo trong máy ảo, trên máy khác có thể khác.

## 4. Adaptation metrics

| | Sudden Drift | Gradual Drift |
| --- | ---: | ---: |
| Drift bắt đầu / đạt cực đại | t = 1000 / 1000 | t = 800 / 1200 |
| ADWIN phát hiện | t = 1183 | t = 1247 |
| **Detection delay** (tính từ lúc drift đạt cực đại) | **183 mẫu** | **47 mẫu** |
| Thích nghi xong | t = 1383 | t = 1447 |
| **Detection → adapted** (= W) | 200 mẫu | 200 mẫu |
| **Drift onset → adapted** | **383 mẫu** | **647 mẫu** |
| ΔRPM / ΔTorque ước lượng (thực tế tiêm: −150 / +8) | −156.21 / +7.30 | −161.96 / +8.05 |
| Mean score cửa sổ hậu thích nghi: Static / Evolving / Control | 0.4628 / 0.3260 / 0.3243 | 0.4647 / 0.3157 / 0.3229 |
| **Recovery ratio** = (Static − Evolving)/(Static − Control) | **0.988** | **1.051** |

Recovery ratio ≈ 1 nghĩa là sau thích nghi, mặt bằng điểm bất thường trở về gần như đúng mức của luồng không drift. Với Gradual, tỉ số > 1 cho thấy **hơi over-correct**: điểm bị hạ thấp hơn Control một chút, phù hợp với việc ΔRPM ước lượng (−162) lớn hơn độ dịch thật (−150).

Lưu ý: "Adaptation time" ở đây bị chi phối bởi thiết kế. Nó luôn bằng detection delay + W. Chưa có thí nghiệm thay đổi W (độ nhạy theo W là hướng mở rộng).

## 5. Phân tích theo cửa sổ thời gian

Đoạn A = trước drift, B = drift đã xảy ra nhưng chưa thích nghi xong, C = sau thích nghi.

| Scenario | Đoạn | n | lỗi | Static TP/FP/FN | Static F1 | Static FPR | Evolving TP/FP/FN | Evolving F1 | Evolving FPR |
| --- | --- | ---: | ---: | --- | ---: | ---: | --- | ---: | ---: |
| Sudden | A | 1000 | 17 | 3/22/14 | 0.143 | 0.022 | 3/22/14 | 0.143 | 0.022 |
| Sudden | B | 384 | 7 | 4/28/3 | 0.205 | 0.074 | 4/28/3 | 0.205 | 0.074 |
| Sudden | C | 616 | 15 | 11/64/4 | 0.244 | 0.106 | 8/6/7 | 0.552 | 0.010 |
| Gradual | A | 800 | 15 | 2/19/13 | 0.111 | 0.024 | 2/19/13 | 0.111 | 0.024 |
| Gradual | B | 648 | 10 | 6/39/4 | 0.218 | 0.061 | 6/39/4 | 0.218 | 0.061 |
| Gradual | C | 552 | 14 | 10/55/4 | 0.253 | 0.102 | 6/3/8 | 0.522 | 0.006 |

- Ở A và B, hai hệ **trùng nhau hoàn toàn**, đúng giao thức test-then-adapt.
- Đoạn B là **"chi phí" của độ trễ**: FPR của cả hai hệ đã tăng lên 6–7% trong 384–648 mẫu trước khi thích nghi xong.
- Số ca lỗi mỗi đoạn chỉ 7–17, nên Recall theo đoạn rất nhiễu: một ca lỗi ứng với 6–14 điểm phần trăm.

### 5.1. So với tham chiếu "không drift" trên cùng cửa sổ C

Static có Recall cao hơn Evolving ở đoạn C (0.73 so với 0.53 ở Sudden). Nhưng đây **không phải do Static phát hiện tốt hơn**: drift (RPM giảm, Torque tăng) đẩy *mọi* điểm số lên, nên cả ca lỗi thật lẫn mẫu bình thường đều vượt τ, và FP tăng khoảng 10 lần. Tham chiếu công bằng hơn là *hệ Static trên luồng Control ở cùng cửa sổ*: hệ thống sẽ hoạt động thế nào nếu không có drift. Tham chiếu này là oracle, chỉ dùng để đánh giá.

| Scenario (cửa sổ C) | Hệ | TP | FP | FN | Precision | Recall | F1 | FPR |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sudden (1384–1999) | Static trên luồng drift | 11 | 64 | 4 | 0.147 | 0.733 | 0.244 | 0.106 |
| | **Evolving trên luồng drift** | **8** | **6** | **7** | **0.571** | **0.533** | **0.552** | **0.010** |
| | Control reference (không drift) | 8 | 6 | 7 | 0.571 | 0.533 | 0.552 | 0.010 |
| Gradual (1448–1999) | Static trên luồng drift | 10 | 55 | 4 | 0.154 | 0.714 | 0.253 | 0.102 |
| | **Evolving trên luồng drift** | **6** | **3** | **8** | **0.667** | **0.429** | **0.522** | **0.006** |
| | Control reference (không drift) | 7 | 5 | 7 | 0.583 | 0.500 | 0.538 | 0.009 |

**Đây là kết quả rõ nhất của đề tài:** sau thích nghi, hệ Evolving trên luồng Sudden **khớp chính xác** hành vi của hệ gốc trên dữ liệu không drift (cùng TP/FP/FN trong cửa sổ C). Với Gradual thì khớp gần đúng: kém 1 TP và ít hơn 2 FP, phù hợp với việc over-correct nhẹ đã nêu ở mục 4.

Cách nói đúng: *cơ chế thích nghi **khôi phục hành vi phát hiện của hệ trước drift**, chứ không làm hệ thống tốt hơn hệ gốc.* "Recall giảm so với Static" thực chất là Static bị drift làm "báo động tràn lan" nên bắt được nhiều lỗi hơn một cách ngẫu nhiên, đi kèm FPR 10%.

Giới hạn: kết luận này dựa trên 15 và 14 ca lỗi, một kịch bản drift nhân tạo cho mỗi loại, một seed dữ liệu. Chưa có kiểm định thống kê về mức ý nghĩa.

## 6. Biểu đồ tổng kết

`figures/10_final_metrics_grouped.png` vẽ Precision/Recall/F1/FPR toàn luồng cho E1–E5b dạng cột đặt cạnh nhau, thay cho biểu đồ stacked bar ở Cell 8.15. `figures/10_window_c_vs_control_reference.png` minh họa mục 5.1.

## 7. Kết luận Phase 10

- Mọi metric trong roadmap ban đầu đều đã có số liệu: detection (P/R/F1/FPR), adaptation (detection delay, adaptation time, recovery), complexity (rules, latency).
- Luận điểm chính được đóng khung lại cho chính xác hơn: **Evolving khôi phục hành vi của hệ không drift**, bằng chứng là cửa sổ C khớp với Control reference.
