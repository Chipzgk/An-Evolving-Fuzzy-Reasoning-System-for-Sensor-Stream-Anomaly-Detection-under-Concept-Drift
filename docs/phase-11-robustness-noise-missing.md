# Phase 11 (Bonus) — Robustness: Drift + Noise (E6), Drift + Missing (E7), bỏ oracle chọn biến

## 1. Mục tiêu và thiết lập

- Notebook: [`notebooks/11_robustness_noise_missing.ipynb`](../notebooks/11_robustness_noise_missing.ipynb)
- Kết quả: `results/11_*.csv`. Hình: `figures/11_noise_robustness.png`, `figures/11_missing_robustness.png`
- Giữ nguyên τ = 0.67, W = 200, ADWIN δ = 0.002, 12 luật. Mỗi cấu hình chạy **5 seed**, báo cáo mean (± std).
- **E6 — nhiễu:** cộng $\mathcal{N}(0,(\sigma\cdot\text{std}_{train})^2)$ vào cả 5 cảm biến, với σ ∈ {0.05, 0.10, 0.20, 0.30}, rồi clip theo miền vật lý.
- **E7 — missing:** mỗi giá trị cảm biến mất độc lập với xác suất p ∈ {0.05, 0.10, 0.20} (MCAR). Điền bằng **LOCF** (giá trị hợp lệ gần nhất trong quá khứ, không nhìn tương lai); mẫu đầu luồng nếu mất thì dùng median của Train.

## 2. E6 — Drift + Noise

| σ | Scenario | Static F1 | Evolving F1 | Static FPR | Evolving FPR | Static Recall | Evolving Recall | ADWIN phát hiện (mean t) |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.05 | Sudden | 0.217 | **0.275** | 0.058 | **0.028** | 0.477 | 0.385 | 1183.0 |
| 0.05 | Gradual | 0.219 | **0.251** | 0.057 | **0.031** | 0.477 | 0.369 | 1253.4 |
| 0.10 | Sudden | 0.221 | **0.266** | 0.058 | **0.028** | 0.487 | 0.369 | 1183.0 |
| 0.10 | Gradual | 0.224 | **0.244** | 0.058 | **0.032** | 0.492 | 0.364 | 1272.6 |
| 0.20 | Sudden | 0.227 | **0.257** | 0.057 | **0.028** | 0.492 | 0.354 | 1183.0 |
| 0.20 | Gradual | 0.228 | **0.236** | 0.056 | **0.033** | 0.492 | 0.354 | 1285.4 |
| 0.30 | Sudden | 0.223 | **0.231** | 0.056 | **0.029** | 0.477 | 0.323 | 1195.8 |
| 0.30 | Gradual | **0.227** | 0.222 | 0.055 | **0.033** | 0.482 | 0.333 | 1311.0 |

Số seed (trên 5) mà Evolving tốt hơn Static:

| σ | Sudden: FPR thấp hơn / F1 cao hơn | Gradual: FPR thấp hơn / F1 cao hơn |
| ---: | :---: | :---: |
| 0.05 | 5 / 5 | 5 / 5 |
| 0.10 | 5 / 5 | 5 / 5 |
| 0.20 | 5 / 4 | 5 / 5 |
| 0.30 | 5 / 4 | 5 / 3 |

**Quan sát:**
- **ADWIN bền với nhiễu trong phạm vi đã thử:** trên luồng Control, 0 cảnh báo ở mọi mức nhiễu và mọi seed. Trên luồng drift, không có cảnh báo nào trước khi drift bắt đầu. Riêng Gradual, độ trễ phát hiện tăng theo nhiễu (t ≈ 1253 → 1311).
- **Mức giảm FPR giữ ổn định** (khoảng một nửa) ở mọi mức nhiễu: 20/20 cấu hình × seed đều cho Evolving FPR thấp hơn.
- **Lợi thế F1 giảm dần khi nhiễu tăng.** Ở σ = 0.30, Gradual Evolving có F1 trung bình *thấp hơn* Static (0.222 so với 0.227), chỉ thắng 3/5 seed. Nguyên nhân: nhiễu làm Recall của Evolving giảm nhanh hơn, trong khi Static giữ Recall cao nhờ mặt bằng điểm bị drift đẩy lên.
- Trên Control, nhiễu làm cả hai hệ giảm như nhau (F1 0.302 → 0.242 ở σ = 0.30). Đây là suy giảm của bản thân FIS, không liên quan tới cơ chế evolving.

## 3. E7 — Drift + Missing Data (LOCF)

| p | Scenario | Static F1 | Evolving F1 | Static FPR | Evolving FPR | Static Recall | Evolving Recall |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.05 | Control | 0.286 | 0.286 | 0.016 | 0.016 | 0.297 | 0.297 |
| 0.05 | Sudden | 0.211 | **0.261** | 0.055 | **0.026** | 0.441 | 0.349 |
| 0.05 | Gradual | 0.212 | **0.244** | 0.054 | **0.030** | 0.441 | 0.349 |
| 0.10 | Control | 0.274 | 0.274 | 0.014 | 0.014 | 0.272 | 0.272 |
| 0.10 | Sudden | 0.214 | **0.254** | 0.052 | **0.024** | 0.431 | 0.323 |
| 0.10 | Gradual | 0.215 | **0.241** | 0.051 | **0.029** | 0.431 | 0.333 |
| 0.20 | Control | 0.271 | 0.271 | 0.011 | 0.011 | 0.246 | 0.246 |
| 0.20 | Sudden | 0.219 | **0.259** | 0.047 | **0.022** | 0.415 | 0.313 |
| 0.20 | Gradual | 0.220 | **0.240** | 0.047 | **0.025** | 0.415 | 0.308 |

**Quan sát:**
- Missing + LOCF chủ yếu làm **giảm Recall** của cả hai hệ (Control: 0.333 → 0.246 ở p = 0.2). Khi giá trị bị điền bằng quá khứ, những đột biến ngắn ở chính mẫu lỗi có thể bị "xóa".
- ADWIN vẫn không báo động giả nào trên Control. Trên Sudden với p = 0.2, thời điểm phát hiện trung bình là t ≈ 1176.6: vẫn sau khi drift bắt đầu, nhưng sớm hơn trường hợp dữ liệu sạch.
- Chiều hướng Evolving so với Static (FPR giảm khoảng một nửa, F1 tăng) được giữ nguyên ở mọi mức missing đã thử.
- LOCF là cách xử lý đơn giản nhất. Chưa thử cách xử lý "fuzzy-native", ví dụ bỏ qua luật chứa biến bị thiếu.

## 4. Bỏ oracle "drift nằm ở RPM/Torque" — kết quả âm tính

Phase 6/7 **chọn trước** RPM và Torque để thích nghi, vì biết đó là hai kênh bị tiêm drift. Khi triển khai thật, hệ thống không biết điều này. Mục này thử hai quy tắc tự động, đều không dùng nhãn và không dùng mốc tiêm:

- **Chọn biến `auto`:** dịch biến $v$ nếu $z_v = |\bar{x}_{buffer,v} - \text{ref}_v| / \text{std}_{train,v} > k$.
- **Điểm tham chiếu:** `design` = tâm MF MEDIUM (như Phase 7), hoặc `warmup` = trung bình 500 mẫu đầu luồng (giả định máy bắt đầu ở trạng thái bình thường).

| Tham chiếu | Chọn biến | Sudden: biến được dịch | Sudden F1 / FPR | Gradual F1 / FPR |
| --- | --- | --- | ---: | ---: |
| design | **oracle (Phase 7)** | rpm, torque | **0.273 / 0.029** | 0.246 / 0.031 |
| design | auto k = 0.3 hoặc 0.5 | air, process, rpm, torque | 0.263 / 0.031 | 0.231 / 0.035 |
| design | auto k = 1.0 | (không biến nào) | 0.211 / 0.058 | 0.212 / 0.058 |
| warmup | oracle | rpm, torque | 0.268 / 0.030 | **0.256 / 0.032** |
| warmup | auto k = 0.3 hoặc 0.5 | air, process, rpm, torque | 0.246 / 0.042 | 0.239 / 0.044 |
| warmup | auto k = 1.0 | **chỉ process_temp** | **0.152 / 0.105** | **0.149 / 0.107** |

Trên Control, không có adaptation nào được kích hoạt, nên mọi biến thể đều bằng E1.

**Diễn giải:**
- Quy tắc chọn biến tự động **không phân biệt được** drift tiêm vào (RPM/Torque) với **xu hướng nhiệt độ tự nhiên** của AI4I. Nhiệt độ trong đoạn Test lệch khỏi Train (KS-test ở Phase 3), và còn trôi ngay trong luồng. Theo `design`, $z_{air} = 0.95$ còn lớn hơn $z_{RPM} = 0.85$.
- Hệ quả: auto luôn dịch thêm MF nhiệt độ, và kết quả kém hơn oracle. Trường hợp xấu nhất (`warmup`, k = 1.0) chỉ dịch Process temperature mà bỏ sót RPM/Torque, khiến FPR còn **tệ hơn cả Static** (0.105 so với 0.058).
- **Kết luận trung thực:** kết quả tốt của Phase 7 **phụ thuộc vào việc biết trước kênh bị drift**. Đây là giới hạn cần ghi rõ trong báo cáo. Một cơ chế tự chọn biến đáng tin cậy (ví dụ kiểm định phân phối từng biến so với cửa sổ tham chiếu có hiệu chỉnh đa kiểm định, hoặc phân tích đóng góp của từng biến vào độ lệch điểm số) là hướng phát triển tiếp theo.
- Tham chiếu `warmup` ước lượng độ dịch **sát thực tế hơn**: ΔRPM = −139.9 so với độ dịch thực đo được khoảng −136 (Phase 4), trong khi `design` cho −156.2. Nhờ vậy Gradual đạt F1 tốt hơn (0.256, TP 15). Với Sudden thì F1 thấp hơn chút (0.268 so với 0.273), nên chưa thể nói `warmup` tốt hơn tuyệt đối.

### 4.1. Stress test báo động nhầm: `design` so với `warmup`

Trung bình trên 4 thời điểm báo nhầm (t = 300, 700, 1000, 1400) trên Control. Tham chiếu E1: TP 13, FP 34, F1 0.302.

| Tham chiếu | Chọn biến | TP (mean / min) | FP (mean) | F1 (mean / min) |
| --- | --- | ---: | ---: | ---: |
| design | oracle | 9.75 / 8 | 31.0 | 0.242 / 0.210 |
| warmup | oracle | 11.75 / 10 | 33.5 | 0.277 / 0.250 |
| design | auto k = 0.5 | 13.5 / 13 | 39.5 | 0.294 / 0.274 |
| warmup | auto k = 0.5 | 14.0 / 13 | 48.3 | 0.279 / 0.254 |

Với cùng cách chọn biến oracle, `warmup` **giảm tác hại của báo động nhầm** (F1 trung bình 0.277 so với 0.242), vì khi không có drift thật thì độ dịch ước lượng nhỏ hơn. Quy tắc auto ít làm giảm TP nhưng lại tăng FP.

## 5. Kết luận Phase 11

1. Dưới nhiễu và missing ở mức vừa phải, **chiều hướng chính giữ nguyên**: Evolving giảm FPR khoảng một nửa ở mọi seed, ADWIN không báo động giả trên Control.
2. Lợi thế F1 **mất dần ở nhiễu cao** (σ = 0.3 với Gradual): cơ chế không bền vô điều kiện.
3. **Giới hạn quan trọng nhất được lộ ra:** Phase 7 dựa vào việc biết trước biến bị drift. Quy tắc chọn biến tự động đơn giản thất bại trên AI4I do xu hướng nhiệt độ tự nhiên. Không được mô tả hệ thống là "tự động hoàn toàn".
