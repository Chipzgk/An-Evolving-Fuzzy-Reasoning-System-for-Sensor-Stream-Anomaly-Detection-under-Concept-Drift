# Phase 7 — Hệ Suy Luận Mờ Tự Tiến Hóa Dưới Dòng Trôi Dạt Cảm Biến (Evolving Fuzzy Reasoning System under Streaming Concept Drift)

## 1. Mục tiêu và Tóm tắt Khoa học

### 1.1. Mục tiêu Cốt lõi
Phase 7 là giai đoạn thực thi trung tâm của toàn bộ đề tài nghiên cứu, hiện thực hóa cơ chế thích nghi mờ trực tuyến (**Online Evolving Fuzzy Adaptation**) nhằm đối phó với hiện tượng dịch chuyển phân phối dữ liệu cảm biến thời gian thực, kế thừa trực tiếp các phát hiện và giao thức đã xác lập ở Phase 5 và Phase 6.

Mục tiêu nghiên cứu trọng tâm của Phase 7:
1. **Hiện thực hóa cơ chế thích nghi hàm thuộc tính hướng phát hiện (Detection-driven Adaptation):** Chỉ khởi động quy trình tích lũy mẫu và cập nhật tri thức mờ sau khi thuật toán trực tuyến ADWIN đã phát tín hiệu cảnh báo trôi dạt ($t_{\text{detect}} = 1183$ cho Sudden Drift và $t_{\text{detect}} = 1247$ cho Gradual Drift).
2. **Triệt tiêu hoàn toàn rò rỉ ranh giới trôi dạt (Zero Oracle Boundary Leakage):** Loại bỏ triệt để việc sử dụng các mốc tiêm trôi dạt vật lý giả định ($t = 1000$ hoặc $t = 800$); tham số thích nghi được ước lượng hoàn toàn độc lập từ bộ đệm thích nghi thời gian thực ($W = 200$ mẫu).
3. **Thích nghi hàm thuộc tính cục bộ (Localized Translation-based Adaptation):** Tịnh tiến vị trí các hàm thuộc tính (MFs) của hai kênh cảm biến bị trôi dạt (`Rotational speed [rpm]` và `Torque [Nm]`), bảo tồn nguyên vẹn các hàm thuộc tính của các cảm biến ổn định (`Air temperature`, `Process temperature`, `Tool wear`).
4. **Bảo tồn cấu trúc tri thức chuyên gia và ngưỡng quyết định:** Đóng băng tuyệt đối tập 12 luật Mamdani và ngưỡng phân loại $\tau = 0.67$ đã tối ưu từ tập Validation, bảo đảm khả năng giải thích và tính kiểm soát của hệ suy luận.
5. **Đánh giá hiệu năng đa tầng theo giao thức Prequential chuẩn:**
   - **Tầng 1 — Post-adaptation Evaluation:** Đánh giá độ nhạy và hành vi phân loại thuần túy trên phân phối mới sau khi hoàn tất thích nghi ($t > t_{\text{detect}} + 200$).
   - **Tầng 2 — Overall Streaming Performance:** Đánh giá toàn bộ dòng dữ liệu thời gian thực 2,000 mẫu theo giao thức Prequential (Test-Then-Adapt) nhằm phản ánh đúng thực tế vận hành hệ thống.
6. **Lượng hóa trung thực bản chất đánh đổi (Trade-off Analysis):** Phân tích khách quan mối quan hệ giữa việc triệt tiêu cảnh báo giả (False Positive Reduction) và nguy cơ gia tăng bỏ sót sự cố (Missed Failures / False Negatives).

> [!IMPORTANT]
> **Nguyên tắc bảo toàn tính toàn vẹn hệ thống:**
> - Toàn bộ mã nguồn, cấu hình, dữ liệu và tài liệu từ Phase 1 đến Phase 6 (`notebooks/01_...` đến `06_...`, `docs/phase-01...` đến `phase-06...`) được niêm phong, giữ nguyên vẹn 100%.
> - Phase 7 được triển khai hoàn chỉnh và khép kín trong notebook [`notebooks/07_evolving_fuzzy.ipynb`](file:///notebooks/07_evolving_fuzzy.ipynb).

---

### 1.2. Tuyên bố Tổng kết Khoa học (Executive Scientific Summary)

> *"Dưới các kịch bản dịch chuyển phân phối cảm biến có kiểm soát (controlled sensor-distribution drift scenarios), cơ chế thích nghi mờ trực tuyến dựa trên bộ đệm cục bộ không nhãn (detection-driven, buffer-only adaptation) đã giải quyết hiệu quả tình trạng bão hòa điểm số của hệ mờ tĩnh baseline. Bằng việc ước lượng độ dịch chuyển tâm cụm $\Delta_v = \bar{x}_{\text{buffer}, v} - C_{\text{MEDIUM}, v}$ trên cửa sổ $W = 200$ mẫu sau phát hiện, hệ thống đã tịnh tiến chính xác các hàm thuộc tính của `Rotational speed` ($\approx -156\text{ đến } -162\text{ rpm}$) và `Torque` ($\approx +7.3\text{ đến } +8.1\text{ Nm}$).*
> 
> *Trên tập đánh giá hậu thích nghi (Post-adaptation window), hệ thống Evolving Fuzzy đã cắt giảm vượt bậc số lượng cảnh báo giả: giảm $90.6\%$ FP ở Sudden Drift ($64 \to 6$) và giảm $94.5\%$ FP ở Gradual Drift ($55 \to 3$), đưa tỷ lệ báo động giả (FPR) từ mức nguy hại vận hành $> 10\%$ xuống chỉ còn $1.00\%$ (Sudden) và $0.56\%$ (Gradual), nâng Specificity lên trên $99\%$ và tăng gấp đôi F1-Score ($0.2444 \to 0.5517$ ở Sudden, $0.2532 \to 0.5217$ ở Gradual).*
> 
> *Trên quy mô toàn dòng luồng 2,000 mẫu theo giao thức Prequential thời gian thực, hệ thống Evolving ghi nhận mức giảm cảnh báo giả tương đối đạt $50.88\%$ ở Sudden Drift ($\Delta\text{FP} = -58$) và $46.02\%$ ở Gradual Drift ($\Delta\text{FP} = -52$). Tuy nhiên, việc giữ nguyên ngưỡng phân loại đóng băng $\tau = 0.67$ trong khi dịch chuyển mặt bằng phân phối điểm số đã tạo ra một sự đánh đổi vật lý có hệ thống: Recall toàn luồng giảm $7.69$ percentage points (Sudden: bỏ sót thêm 3 ca lỗi thật) và $10.26$ percentage points (Gradual: bỏ sót thêm 4 ca lỗi thật), kéo theo Balanced Accuracy giảm nhẹ từ $\approx 70.2\%$ xuống $67.8\%$ (Sudden) và $66.4\%$ (Gradual).*
> 
> *Kết quả này khẳng định: Cơ chế thích nghi mờ trực tuyến giải quyết xuất sắc bài toán triệt tiêu cảnh báo giả dưới tác động của trôi dạt cảm biến cơ học, đồng thời làm sáng tỏ bản chất đánh đổi giữa Precision và Recall trong các hệ thống giám sát công nghiệp khi ngưỡng phân loại được cố định."*

---

## 2. Kiến trúc Hệ Thống và Phương Pháp Luận Thích Nghi

### 2.1. Sơ đồ Kiến trúc Prequential Online Adaptation

```text
       ┌────────────────────────────────────────────────────────────────────────┐
       │             STREAMING SENSOR DATA (Test Partition: 2,000 mẫu)          │
       │  • Sudden: Drift tiêm tại t = 1000                                     │
       │  • Gradual: Drift tiêm chuyển tiếp t = 800 -> 1200                     │
       └───────────────────────────────────┬────────────────────────────────────┘
                                           │
                                           ▼ (Mẫu x_t đến theo thời gian thực)
       ┌────────────────────────────────────────────────────────────────────────┐
       │                    PHASE 1: INFERENCE & PREDICTION                     │
       │  • Nếu t <= t_detect + W : Chấm điểm bằng Static FIS Knowledge         │
       │  • Nếu t >  t_detect + W : Chấm điểm bằng Evolving FIS Knowledge       │
       │  • Tính điểm mờ A(t) qua Continuous Min-Max Centroid Defuzzification   │
       │  • Dự báo y_pred = [A(t) >= 0.67]                                      │
       │  • Ghi nhận kết quả đánh giá (Strict Test-Then-Adapt Protocol)          │
       └───────────────────────────────────┬────────────────────────────────────┘
                                           │
                                           ▼
       ┌────────────────────────────────────────────────────────────────────────┐
       │                PHASE 2: ADWIN DRIFT MONITORING (Phase 5)               │
       │  • Giám sát chuỗi điểm số A(t)                                         │
       │  • Tín hiệu kích hoạt (Drift Alert):                                   │
       │      * Sudden Drift:  t_detect = 1183 (Trễ: 183 mẫu)                   │
       │      * Gradual Drift: t_detect = 1247 (Trễ: 47 mẫu)                    │
       └───────────────────────────────────┬────────────────────────────────────┘
                                           │ (Khi ADWIN phát hiện trôi dạt)
                                           ▼
       ┌────────────────────────────────────────────────────────────────────────┐
       │               PHASE 3: ADAPTATION BUFFER (Phase 7.2 - 7.10)            │
       │  • Khởi tạo cửa sổ đệm W = 200 mẫu không gán nhãn:                     │
       │      * Sudden Buffer:  t = 1184 -> 1383                                │
       │      * Gradual Buffer: t = 1248 -> 1447                                │
       │  • Tuyệt đối KHÔNG sử dụng thông tin ranh giới tiêm (No Oracle)        │
       │  • Tính độ lệch dịch chuyển tâm cụm thực nghiệm:                       │
       │      Δ_v = Mean(Buffer_v) - Centroid(MF_MEDIUM, v)                     │
       └───────────────────────────────────┬────────────────────────────────────┘
                                           │ (Sau khi hoàn tất thu thập W mẫu)
                                           ▼
       ┌────────────────────────────────────────────────────────────────────────┐
       │             PHASE 4: LOCALIZED FUZZY MEMBERSHIP ADAPTATION             │
       │  • Tịnh tiến MFs: μ_new(u) = μ_old(u - Δ_v) cắt theo Universe          │
       │  • Chỉ áp dụng cho 2 biến trôi dạt: RPM và Torque                      │
       │  • Đóng băng 3 biến còn lại: Air Temp, Process Temp, Tool Wear         │
       │  • Đóng băng cấu trúc 12 luật chuyên gia và ngưỡng Tau = 0.67          │
       │  • Bàn giao tập tri thức Evolving MFs cho các bước suy diễn tiếp theo   │
       └────────────────────────────────────────────────────────────────────────┘
```

---

### 2.2. Các Quyết định Phương pháp luận Cốt lõi

#### Quyết định 1: Loại bỏ Oracle Boundary Leakage — Cơ chế Thích nghi Thuần Buffer (Buffer-Only Adaptation)
Trong các nghiên cứu mô phỏng, nguy cơ rò rỉ ranh giới trôi dạt (oracle boundary leakage) thường xảy ra khi thuật toán lấy dữ liệu trước mốc tiêm làm baseline tính toán độ lệch. Trong Phase 7:
- Hệ thống **tuyệt đối không biết** drift bắt đầu ở $t=1000$ hay $t=800$.
- Chỉ khi ADWIN cảnh báo trôi dạt, bộ đệm thích nghi $W = 200$ mẫu mới được kích hoạt để quan sát phân phối mới.
- Độ dịch chuyển của biến $v \in \{\text{RPM}, \text{Torque}\}$ được xác định hoàn toàn nội tại:
  $$\Delta_v = \bar{x}_{\text{buffer}, v} - C_{\text{MEDIUM}, v}$$
  trong đó $\bar{x}_{\text{buffer}, v}$ là giá trị trung bình cảm biến trong buffer, và $C_{\text{MEDIUM}, v} = \frac{\int u \cdot \mu_{\text{MEDIUM}}(u) du}{\int \mu_{\text{MEDIUM}}(u) du}$ là trọng tâm hình học của tập mờ `MEDIUM` ban đầu.

#### Quyết định 2: Thích nghi Dạng Tịnh tiến Hình học (Translation-based MF Adaptation)
Thay vì tái huấn luyện cụm mờ từ đầu làm mất liên kết với các luật chuyên gia:
- Các tập mờ `LOW`, `MEDIUM`, `HIGH` của RPM và Torque được tịnh tiến đồng bộ theo vectơ độ lệch $\Delta_v$:
  $$\mu_{\text{adapted}}(u) = \mu_{\text{base}}(u - \Delta_v)$$
- Xử lý giá trị ngoài biên: Giá trị nội suy ngoài phạm vi Universe of Discourse được gán mặc định bằng $0.0$, bảo đảm nghiêm ngặt điều kiện $\mu(u) \in [0, 1]$.

#### Quyết định 3: Bảo Toàn Tri Thức (Knowledge Preservation) & Ngăn Quên Thảm Khốc
- Đóng băng 9 hàm thuộc tính của 3 biến không trôi dạt (`air_temp`, `process_temp`, `tool_wear`).
- Giữ nguyên vẹn 12 luật Mamdani và cơ chế giải mờ trọng tâm (Centroid Defuzzification).
- Giữ nguyên ngưỡng phân loại $\tau = 0.67$ để đánh giá sự chuyển dịch nội tại của hệ thống.

---

## 3. Chi Tiết Thực Nghiệm Từng Bước (Phase 7.0 → 7.19)

Toàn bộ 20 bước thực nghiệm được thiết kế và thực thi tuần tự trong notebook [`notebooks/07_evolving_fuzzy.ipynb`](file:///notebooks/07_evolving_fuzzy.ipynb):

### 3.1. Phase 7.0 & 7.1 — Khởi Tạo và Đóng Băng Static Knowledge Baseline
- **Cell 7.0:** Nạp phân vùng Test stream (2,000 mẫu, index $0 \to 1999$), nạp Universes of Discourse (1,000 điểm lưới), 15 hàm thuộc tính Mamdani, 12 luật mờ, và ngưỡng $\tau = 0.67$.
- **Cell 7.1:** Khởi tạo bản sao độc lập `evolving_mfs` từ 15 hàm thuộc tính tĩnh.
  - *Kiểm chứng tính toàn vẹn:* Khớp tuyệt đối 15/15 MFs (`array_equal == True`).

### 3.2. Phase 7.2 & 7.3 — Thiết Lập Bộ Đệm Thích Nghi Thời Gian Thực (Adaptation Buffer)
- **Cell 7.2:** Cố định độ dài bộ đệm $W = 200$ mẫu:
  - Sudden Buffer: $t \in [1184, 1383]$ (UDI: $9185 \to 9384$).
  - Gradual Buffer: $t \in [1248, 1447]$ (UDI: $9249 \to 9448$).
- **Cell 7.3:** Khảo sát chẩn đoán thống kê trên buffer so với đường cơ sở trước phát hiện:
  - Sudden Buffer Mean: RPM $= 1381.79\text{ rpm}$ ($\Delta = -157.90\text{ rpm}$), Torque $= 47.24\text{ Nm}$ ($\Delta = +7.34\text{ Nm}$).
  - Gradual Buffer Mean: RPM $= 1376.04\text{ rpm}$ ($\Delta = -158.48\text{ rpm}$), Torque $= 47.99\text{ Nm}$ ($\Delta = +8.07\text{ Nm}$).
  - Các biến Air Temp, Process Temp, Tool Wear dao động ổn định trong biên độ ngẫu nhiên ($< 1\%$).

### 3.3. Phase 7.4 & 7.10 — Ước Lượng Độ Dịch Chuyển Thuần Buffer (Buffer-Only Shift Estimation)
- Nhằm tránh rò rỉ mốc tiêm drift ở Cell 7.4 (sử dụng $t < 1000$ và $t < 800$), **Cell 7.10** chuyển đổi hoàn toàn sang công thức ước lượng độ lệch từ trọng tâm hàm mờ `MEDIUM` ban đầu ($C_{\text{rpm\_medium}} = 1538.00\text{ rpm}$, $C_{\text{torque\_medium}} = 39.94\text{ Nm}$):
  - **Sudden Drift Buffer:**
    * $\Delta_{\text{RPM}} = 1381.7858 - 1538.0000 = -156.2142\text{ rpm}$.
    * $\Delta_{\text{Torque}} = 47.2415 - 39.9400 = +7.3015\text{ Nm}$.
  - **Gradual Drift Buffer:**
    * $\Delta_{\text{RPM}} = 1376.0408 - 1538.0000 = -161.9592\text{ rpm}$.
    * $\Delta_{\text{Torque}} = 47.9930 - 39.9400 = +8.0530\text{ Nm}$.

> [!WARNING]
> **Đính chính (Phase 9):** các giá trị trung gian ở mục 3.3 bị ghi sai. Tâm MF MEDIUM thực tế là $C_{RPM}=1551.3342$ và $C_{Torque}=40.0000$. Trung bình buffer Sudden = 1395.12 rpm / 47.3015 Nm; Gradual = 1389.375 rpm / 48.053 Nm. Các độ dịch cuối cùng ($-156.2142/+7.3015$ và $-161.9592/+8.0530$) là **đúng** và không ảnh hưởng kết quả. Xem `docs/phase-09-modular-reproduction-and-e2.md` §7.

### 3.4. Phase 7.5, 7.6 & 7.11 — Hiệu Chỉnh Hàm Tịnh Tiến và Kiểm Chứng Hình Học MFs
- **Cell 7.5 & 7.6:** Phát hiện và sửa lỗi đảo chiều tịnh tiến trong công thức nội suy. Trục nội suy chuẩn xác:
  ```python
  adapted_mf = np.interp(universe - shift, universe, base_mf, left=0.0, right=0.0)
  ```
- **Cell 7.11:** Tạo ra hai bộ tham số mờ thích nghi: `sudden_buffer_adapted_mfs` và `gradual_buffer_adapted_mfs`.
  - *Kiểm chứng tính bất biến (Protected MFs):* 9 hàm thuộc tính của Air, Process, Tool Wear giữ nguyên 100% (`PASS`).
  - *Kiểm chứng biến thiên:* 6 hàm thuộc tính của RPM và Torque thay đổi so với baseline (`PASS`).
  - *Miền xác định:* $100\%$ giá trị $\mu \in [0.0, 1.0]$ và hữu hạn (`PASS`).
  - *Hệ luật:* Cố định đủ 12 luật Mamdani (`PASS`).

### 3.5. Phase 7.7, 7.8, 7.9 & 7.12 — Tầng Suy Diễn Evolving Mamdani
- **Cell 7.7 & 7.8:** Phân tích mã nguồn suy diễn gốc, phát hiện việc hard-code hàm tính toán độ thuộc tĩnh.
- **Cell 7.9:** Xây dựng `compute_memberships_evolving(sample, mfs)` hỗ trợ truyền bộ tham số mờ động độc lập.
- **Cell 7.12:** Xây dựng bộ suy diễn `mamdani_inference_evolving(sample, adapted_mfs)` tích hợp bộ chuẩn hóa nhãn ngôn ngữ chữ hoa/thường (`normalized_term = term.lower()`), liên kết chặt chẽ giữa luật chuyên gia và từ điển độ thuộc.
  - *Sanity check trên mẫu đầu tiên sau phát hiện ($UDI = 9185$, $t = 1184$):*
    * Static Score: $0.209696$
    * Evolving Score: $0.223914$ ($\Delta = +0.014218$).
    * Tính hợp lệ: $S \in [0, 1]$ (`PASS`).

### 3.6. Phase 7.13 — Chẩn Đoán So Sánh Điểm Số Trong Adaptation Buffer
- Khảo sát 20 mẫu (10 mẫu đầu và 10 mẫu cuối) trong bộ đệm thích nghi:
  - Quan sát thấy rõ xu hướng: Các mẫu bình thường trước đây bị Static model đẩy điểm số lên mức trung gian $\approx 0.50$ hoặc $\approx 0.65$ do drift nay được Evolving model hạ điểm sâu về mức cơ sở $\approx 0.20$ (delta âm mạnh từ $-0.20$ đến $-0.45$).
  - Mẫu bất thường thực sự ($UDI = 9258$) vẫn giữ điểm số cao ổn định ($0.689815$).
  - Toàn bộ 200 mẫu buffer được phân định ranh giới nghiêm ngặt: chỉ dùng cho chẩn đoán và thích nghi, không đưa vào tập đánh giá hiệu năng chính thức.

---

### 3.7. Phase 7.14, 7.15, 7.16 & 7.17 — Đánh Giá Hiệu Năng Hậu Thích Nghi (Post-Adaptation)

Phạm vi đánh giá: Toàn bộ các mẫu xuất hiện **sau khi bộ đệm thích nghi kết thúc** cho đến cuối dòng dữ liệu:
- **Sudden Post-adaptation:** $t \in [1384, 1999]$ ($N = 616$ mẫu).
- **Gradual Post-adaptation:** $t \in [1448, 1999]$ ($N = 552$ mẫu).

#### Phân phối điểm số trung bình (Cell 7.14):
- Sudden Drift: Mean Static Score $= 0.462804 \to$ Mean Evolving Score $= 0.325958$.
- Gradual Drift: Mean Static Score $= 0.464662 \to$ Mean Evolving Score $= 0.315719$.

#### Phân phối nhãn thực tế (Cell 7.16):
- Sudden Post-adaptation ($N = 616$): **$601$ mẫu Normal** ($97.56\%$) và **$15$ mẫu Failure** ($2.44\%$).
- Gradual Post-adaptation ($N = 552$): **$538$ mẫu Normal** ($97.46\%$) và **$14$ mẫu Failure** ($2.54\%$).

#### Bảng Tổng Hợp Chỉ Số Hậu Thích Nghi (Cell 7.15 & 7.17, Ngưỡng $\tau = 0.67$):

| Chỉ số Thực nghiệm | Sudden — Static | Sudden — Evolving | Biến thiên (Sudden) | Gradual — Static | Gradual — Evolving | Biến thiên (Gradual) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Mẫu đánh giá** | 616 | 616 | — | 552 | 552 | — |
| **True Positives (TP)** | 11 | 8 | **−3** | 10 | 6 | **−4** |
| **True Negatives (TN)** | 537 | 595 | **+58** | 483 | 535 | **+52** |
| **False Positives (FP)** | 64 | 6 | **−58 (−90.6%)** | 55 | 3 | **−52 (−94.5%)** |
| **False Negatives (FN)** | 4 | 7 | **+3** | 4 | 8 | **+4** |
| **Precision** | 14.67% | **57.14%** | **+42.47 pp** | 15.38% | **66.67%** | **+51.29 pp** |
| **Recall (TPR)** | **73.33%** | 53.33% | **−20.00 pp** | **71.43%** | 42.86% | **−28.57 pp** |
| **F1-Score** | 0.2444 | **0.5517** | **+0.3073** | 0.2532 | **0.5217** | **+0.2685** |
| **False Positive Rate (FPR)** | 10.65% | **1.00%** | **−9.65 pp** | 10.22% | **0.56%** | **−9.66 pp** |
| **False Negative Rate (FNR)** | 26.67% | 46.67% | **+20.00 pp** | 28.57% | 57.14% | **+28.57 pp** |
| **Specificity (TNR)** | 89.35% | **99.00%** | **+9.65 pp** | 89.78% | **99.44%** | **+9.66 pp** |
| **Balanced Accuracy** | **81.34%** | 76.17% | **−5.17 pp** | **80.60%** | 71.15% | **−9.45 pp** |

---

### 3.8. Phase 7.18 & 7.19 — Đánh Giá Toàn Dòng Luồng Thời Gian Thực (Overall Streaming Performance)

Để loại bỏ hoàn toàn thiên kiến chọn mẫu (selection bias) khi chỉ đánh giá đoạn hậu thích nghi, **Cell 7.18** ghép nối toàn diện chuỗi suy luận 2,000 mẫu theo chuẩn **Prequential Test-Then-Adapt**:
- **Static Pipeline:** Toàn bộ $2,000$ mẫu từ $0 \to 1999$ được chấm điểm bởi Static Mamdani FIS.
- **Evolving Pipeline:**
  - $0 \le t \le t_{\text{adapt\_end}}$ ($1384$ mẫu ở Sudden, $1448$ mẫu ở Gradual): Chấm điểm bằng Static FIS Knowledge.
  - $t > t_{\text{adapt\_end}}$ ($616$ mẫu ở Sudden, $552$ mẫu ở Gradual): Chấm điểm bằng Evolving FIS Knowledge.

#### Bảng Ma Trận Nhầm Lẫn Toàn Luồng (Overall Confusion Matrix — $N = 2000$):

```text
[SUDDEN DRIFT STREAM — 2,000 MẪU]
Static FIS   : TP = 18 | TN = 1847 | FP = 114 | FN = 21  (Tổng = 2,000)
Evolving FIS : TP = 15 | TN = 1905 | FP =  56 | FN = 24  (Tổng = 2,000)
-----------------------------------------------------------------------
Chênh lệch   : ΔTP = -3| ΔTN = +58 | ΔFP = -58| ΔFN = +3  (Tổng Δ = 0)

[GRADUAL DRIFT STREAM — 2,000 MẪU]
Static FIS   : TP = 18 | TN = 1848 | FP = 113 | FN = 21  (Tổng = 2,000)
Evolving FIS : TP = 14 | TN = 1900 | FP =  61 | FN = 25  (Tổng = 2,000)
-----------------------------------------------------------------------
Chênh lệch   : ΔTP = -4| ΔTN = +52 | ΔFP = -52| ΔFN = +4  (Tổng Δ = 0)
```

#### Bảng So Sánh Chỉ Số Toàn Luồng và Delta Thực Nghiệm (Cell 7.18 & 7.19):

| Chỉ số Toàn Luồng ($N=2000$) | Sudden — Static | Sudden — Evolving | **Sudden Delta** | Gradual — Static | Gradual — Evolving | **Gradual Delta** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Precision** | 13.64% | **21.13%** | **+7.49 pp** | 13.74% | **18.67%** | **+4.93 pp** |
| **Recall** | **46.15%** | 38.46% | **−7.69 pp** | **46.15%** | 35.90% | **−10.26 pp** |
| **F1-Score** | 0.2105 | **0.2727** | **+0.0622** | 0.2118 | **0.2456** | **+0.0338** |
| **False Positive Rate (FPR)** | 5.81% | **2.86%** | **−2.96 pp** | 5.76% | **3.11%** | **−2.65 pp** |
| **Relative FPR Reduction** | — | — | **50.88%** | — | — | **46.02%** |
| **False Negative Rate (FNR)** | 53.85% | 61.54% | **+7.69 pp** | 53.85% | 64.10% | **+10.26 pp** |
| **Specificity** | 94.19% | **97.14%** | **+2.96 pp** | 94.24% | **96.89%** | **+2.65 pp** |
| **Balanced Accuracy** | **70.17%** | 67.80% | **−2.37 pp** | **70.20%** | 66.39% | **−3.80 pp** |

---

## 4. Phân Tích Khoa Học Đa Chiều & Trade-Off

### 4.1. Hiệu Ứng Triệt Tiêu Cảnh Báo Giả (False Alarm Suppression)
1. **Ý nghĩa vận hành thực tế:** 
   - Trong bài toán Bảo trì Dự đoán (Predictive Maintenance), chi phí gián đoạn sản xuất do cảnh báo sai (False Alarms) là một trong những rủi ro lớn nhất. Static FIS dưới tác động của drift liên tục kích hoạt cảnh báo sai do phân phối RPM bị kéo lệch về vùng giá trị thấp (kích hoạt các luật nguy cơ quá tải).
   - Evolving FIS đã thành công rực rỡ khi **cắt giảm hơn 50% số ca báo động sai toàn luồng** ($114 \to 56$ ở Sudden và $113 \to 61$ ở Gradual), và cắt giảm trên $90\%$ ở đoạn hậu thích nghi.
2. **Cải thiện độ chuẩn xác (Precision):**
   - Precision toàn luồng tăng từ $13.6\%$ lên $21.1\%$ (Sudden) và $13.7\%$ lên $18.7\%$ (Gradual). Ở đoạn hậu thích nghi, Precision đạt tới $57.1\%$ và $66.7\%$.

### 4.2. Bản Chất Đánh Đổi Vật Lý với Recall & Phân Tích Căn Nguyên
1. **Sự sụt giảm Recall:**
   - Trên toàn luồng, Recall của Evolving giảm $-7.69$ pp ở Sudden ($18 \to 15$ TP) và $-10.26$ pp ở Gradual ($18 \to 14$ TP).
   - Ở đoạn hậu thích nghi, Recall giảm từ $73.3\% \to 53.3\%$ (Sudden, mất 3 ca) và $71.4\% \to 42.9\%$ (Gradual, mất 4 ca).
2. **Cơ chế phát sinh (Plausible Mechanism):**
   - Việc tịnh tiến hàm thuộc tính RPM sang trái ($-156\text{ rpm}$) và Torque sang phải ($+7.3\text{ Nm}$) đã đưa tâm phân phối dữ liệu vận hành mới về đúng vùng ngôn ngữ `MEDIUM`. Hệ quả là điểm bất thường trung bình của toàn dòng stream giảm mạnh ($0.46 \to 0.32$).
   - Tuy nhiên, ngưỡng phân loại được **đóng băng cố định tại $\tau = 0.67$**. Khi mặt bằng điểm mờ tổng thể hạ thấp, một số sự cố máy thực tế (True Failures) có biểu hiện sai lệch cảm biến tinh vi (boundary anomalies) chỉ kích hoạt điểm số ở mức mấp mé ($\approx 0.68 - 0.70$ ở Static model) nay bị kéo tụt xuống dưới ngưỡng $0.67$ (ví dụ về vùng $0.55 - 0.65$), dẫn đến việc bị phân loại nhầm thành Normal (tăng False Negatives).
3. **Hiện tượng F1 tăng nhưng Balanced Accuracy giảm:**
   - $F_1 = \frac{2 \cdot P \cdot R}{P + R}$ là trung bình điều hòa chịu ảnh hưởng áp đảo bởi sự gia tăng mạnh mẽ của Precision (tăng gấp 4 lần ở post-adaptation).
   - $\text{Balanced Accuracy} = \frac{\text{Recall} + \text{Specificity}}{2}$ là trung bình cộng công bằng giữa hai lớp. Mặc dù Specificity tăng gần tiệm cận $100\%$, nhưng sự sụt giảm của Recall ở lớp thiểu số ($N=15$) đã kéo chỉ số Balanced Accuracy giảm nhẹ $\approx 2 - 4$ percentage points.

---

### 4.3. Giới Hạn Nghiên Cứu và Nhận Thức Phương Pháp Luận
> [!NOTE]
> **Phân định giữa Covariate Shift và Concept Drift thực sự:**
> - Trong khuôn khổ đề tài, kịch bản trôi dạt được tạo ra bằng cách tiêm độ lệch nhân tạo lên các kênh cảm biến vật lý $X$ (`Rotational speed` và `Torque`), trong khi nhãn ground truth $Y$ (`Machine failure`) được giữ nguyên vẹn 100%.
> - Do đó, về mặt lý thuyết xác suất thống kê, hiện tượng này cấu thành một dạng **Controlled Input Covariate Shift ($P(X)$ thay đổi)** lan truyền sang không gian điểm số mờ $P(A(t))$, chứ chưa thể khẳng định triệt để là $P(Y|X)$ thay đổi.
> - Việc gọi tên "Evolving Fuzzy System under Concept Drift" được đặt trong ngữ cảnh kỹ thuật: hệ thống tự động thích ứng để duy trì độ tin cậy của bộ giám sát mờ khi môi trường cảm biến vật lý thay đổi trạng thái làm việc.

---

## 5. Kết Luận Phase 7 và Định Hướng Tích Hợp

### 5.1. Kết Luận Đóng Gói Phase 7
Phase 7 đã hoàn thành xuất sắc toàn bộ các mục tiêu nghiên cứu đề ra:
1. Xây dựng thành công quy trình thích nghi mờ trực tuyến tự động không dùng nhãn (unsupervised, buffer-only), hoàn toàn loại bỏ rò rỉ ranh giới trôi dạt.
2. Chứng minh thực nghiệm bằng số liệu định lượng: Thích nghi mờ tịnh tiến giúp triệt tiêu $50.88\%$ cảnh báo giả toàn luồng ở Sudden Drift và $46.02\%$ ở Gradual Drift, đưa FPR hậu thích nghi về dưới $1\%$.
3. Ghi nhận trung thực, minh bạch sự đánh đổi với Recall và Balanced Accuracy khi duy trì ngưỡng quyết định cố định.

### 5.2. Định Hướng Pha Tiếp Theo (Phase 8)
- Tổng hợp toàn diện chuỗi kết quả từ Phase 1 đến Phase 7 phục vụ báo cáo luận văn / công trình nghiên cứu.
- Trực quan hóa so sánh đa chiều: biểu đồ luồng điểm số bất thường theo thời gian ($A_{\text{static}}(t)$ vs $A_{\text{evolving}}(t)$), ma trận nhầm lẫn đối chiếu, và biểu đồ radar các chỉ số hiệu năng.
