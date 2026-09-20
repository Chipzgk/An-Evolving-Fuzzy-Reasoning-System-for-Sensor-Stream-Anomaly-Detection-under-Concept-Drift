# Phase 6 — Phân tích Tác động Trôi dạt và Xác lập Giao thức Thích nghi cho Hệ Mờ (Concept Drift Analysis & Adaptation Protocol)

## 1. Mục tiêu và Tóm tắt Khoa học

### 1.1. Mục tiêu Cốt lõi
Phase 6 là giai đoạn cầu nối mang tính quyết định phương pháp luận giữa tầng **Phát hiện Trôi dạt (Drift Detection - Phase 5)** và tầng **Thực thi Thích nghi Hệ Mờ Tự tiến hóa (Evolving Fuzzy Adaptation - Phase 7)**.

Mục tiêu nghiên cứu trọng tâm của Phase 6:
1. **Định lượng tác động của trôi dạt cảm biến lên không gian suy luận mờ:** Khảo sát chi tiết sự biến thiên phân phối của chuỗi điểm bất thường $A(t) \in [0, 1]$ trước, trong và sau các mốc tiêm trôi dạt (cả Sudden Drift và Gradual Drift).
2. **Xác nhận tính độc lập và thứ tự thời gian của tín hiệu kích hoạt thích nghi (Adaptation Trigger):** Đối chiếu các điểm phát hiện trực tuyến từ thuật toán ADWIN ($t = 1183$ trên Sudden Drift, $t = 1247$ trên Gradual Drift) với ranh giới trôi dạt vật lý để bảo đảm nguyên tắc khoa học: *Hệ thống chỉ được phép thích nghi sau khi đã có tín hiệu cảnh báo trôi dạt tự động.*
3. **Xác lập ranh giới dữ liệu khả dụng (Data Boundary):** Tính toán chính xác số lượng mẫu cảm biến thời gian thực còn lại trong luồng để phục vụ quá trình thích nghi và hậu kiểm.
4. **Chuẩn hóa Giao thức Đánh giá Trực tuyến Prequential (Test-Then-Adapt):** Bác bỏ phương pháp chia cắt tĩnh (batch split) làm mất tính chất luồng; thiết lập quy trình đánh giá nghiêm ngặt nhằm triệt tiêu hoàn toàn hiện tượng rò rỉ dữ liệu (data leakage).
5. **Khoanh vùng tri thức mờ được phép tiến hóa (Fuzzy Knowledge Candidates):** Phân định rạch ròi giữa các tham số hàm thuộc tính (MF) cần cập nhật và các tri thức mờ bất biến cần được bảo vệ.

> [!IMPORTANT]
> **Nguyên tắc phương pháp luận bảo toàn:**
> - Toàn bộ tài nguyên, mã nguồn, mô hình và tài liệu từ Phase 1 đến Phase 5 (`notebooks/01_...` đến `05_...`, `docs/phase-01...` đến `phase-05...`) được niêm phong, giữ nguyên vẹn 100%.
> - Phase 6 được triển khai độc lập trong notebook mới [`notebooks/06_concept_drift.ipynb`](file:///notebooks/06_concept_drift.ipynb).
> - Mọi thử nghiệm trong Phase 6 đều là khảo sát và tiền đề phương pháp luận; tuyệt đối chưa can thiệp hay thay đổi tham số hàm thuộc tính/luật mờ trước khi bước vào Phase 7.

---

### 1.2. Tuyên bố Tổng kết Khoa học (Executive Scientific Summary)

> *"Thực nghiệm định lượng trên Phase 6 chứng minh rằng sự dịch chuyển phân phối của hai kênh cảm biến cơ học (Rotational speed $-150\text{ rpm}$ và Torque $+8\text{ Nm}$) đã tạo ra bước nhảy phân phối mang tính hệ thống trên chuỗi điểm bất thường của hệ mờ tĩnh Mamdani. Trên kịch bản Sudden Drift, điểm trung bình tăng từ $0.3159$ lên $0.4480$ ($\Delta\text{mean} = +0.1321$) và trung vị nhảy vọt từ $0.2249$ lên $0.5000$ ($\Delta\text{median} = +0.2751$). Trên kịch bản Gradual Drift, sự gia tăng diễn ra tiệm tiến qua giai đoạn chuyển tiếp ($0.3200 \to 0.3650 \to 0.4535$), đạt mức tăng chung cuộc $\Delta\text{mean} = +0.1335$ và $\Delta\text{median} = +0.2749$ tương đồng chặt chẽ với Sudden Drift.*
> 
> *Sự thay đổi này phản ánh tác động lan truyền từ không gian đầu vào $P(X)$ sang hành vi điểm số của hệ mờ $P(A(t))$, cung cấp cơ sở định lượng để khẳng định sự suy giảm tính tương thích của hệ mờ tĩnh. Các điểm phát hiện ADWIN ($t = 1183$ cho Sudden và $t = 1247$ cho Gradual) được xác nhận nằm hoàn toàn sau vùng trôi dạt, bảo đảm điều kiện kích hoạt thích nghi hợp lệ với $816$ mẫu (Sudden) và $752$ mẫu (Gradual) khả dụng.*
> 
> *Để bảo tồn bản chất luồng thời gian thực và ngăn chặn rò rỉ dữ liệu, dự án chuẩn hóa giao thức **Prequential (Test-Then-Adapt)**: mỗi mẫu mới luôn được chấm điểm và ghi nhận hiệu năng trước khi được đưa vào bộ nhớ thích nghi. Đồng thời, không gian thích nghi được giới hạn cục bộ ở các hàm thuộc tính của hai biến bị trôi dạt (`Rotational speed` và `Torque`), bảo vệ nguyên vẹn 12 luật mờ và ngưỡng quyết định $\tau = 0.67$ nhằm duy trì khả năng diễn giải và độ ổn định của hệ suy luận."*

---

## 2. Kiến trúc Luồng Thực nghiệm và Phương pháp luận Phase 6

### 2.1. Sơ đồ Pipeline Phân tích và Ranh giới Thích nghi

```text
       ┌────────────────────────────────────────────────────────┐
       │     SENSOR DATA STREAM (Test partition: 2,000 mẫu)     │
       │     - Sudden Drift tiêm tại t = 1000                   │
       │     - Gradual Drift chuyển tiếp t = 800 -> 1200        │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │             STATIC MAMDANI FUZZY SYSTEM                │
       │     - Freeze 5 biến đầu vào, 12 compact rules          │
       │     - Continuous Min-Max Centroid Defuzzification      │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │         ANOMALY SCORE STREAM & DRIFT DETECTION         │
       │     - ADWIN kích hoạt:                                 │
       │         * Sudden Drift:  t = 1183 (delay: 183 mẫu)     │
       │         * Gradual Drift: t = 1247 (delay: 47 mẫu)      │
       └───────────────────────────┬────────────────────────────┘
                                   │
         ══════════════════════════╪══════════════════════════
                 RANH GIỚI BẢO VỆ (NO ADAPTATION TRƯỚC DETECT)
         ══════════════════════════╪══════════════════════════
                                   │ (t > detection_index)
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │       ONLINE PREQUENTIAL ADAPTATION / EVALUATION       │
       │  1. Mẫu x_t đến: Đánh giá điểm số bằng FIS hiện tại     │
       │  2. Ghi nhận dự báo phục vụ Evaluation                 │
       │  3. x_t được nạp vào bộ đệm thích nghi (Adaptation)    │
       │  4. Chỉ điều chỉnh MFs của RPM & Torque               │
       │  5. Bảo vệ Air/Process/Wear MFs, 12 rules, tau=0.67    │
       └────────────────────────────────────────────────────────┘
```

### 2.2. Các Rào cản Phương pháp luận và Quyết định Thiết kế

#### Quyết định 1: Phân biệt giữa Input Shift và Concept Drift $P(Y|X)$
Trong lý thuyết học luồng dữ liệu, sự dịch chuyển phân phối đầu vào $P(X)$ (covariate shift) không nhất thiết đồng nghĩa với việc mối quan hệ điều kiện $P(Y|X)$ thay đổi. Trong Phase 6:
- Chúng ta chứng minh được sự thay đổi trong hành vi của điểm mờ $A(t)$ là hệ quả trực tiếp từ $P(X)$.
- Không vội vàng kết luận chủ quan đây là concept drift hoàn toàn cho đến khi quan sát được sự tương tác của nó với nhãn thực tế $Y$ trong quá trình đánh giá phân loại.

#### Quyết định 2: Loại bỏ Batch Retraining, Áp dụng Triệt để Prequential Protocol
Nếu phân chia 800 mẫu còn lại thành một tập huấn luyện tĩnh (train set) và một tập kiểm thử tĩnh (test set):
- Sẽ phá vỡ tính liên tục và nhân quả của luồng dữ liệu thời gian thực.
- Dẫn đến nguy cơ rò rỉ dữ liệu hoặc che giấu độ trễ thích nghi của hệ thống.
Do đó, phương pháp **Prequential (Test-Then-Train / Test-Then-Adapt)** được chọn làm chuẩn mực khoa học duy nhất.

#### Quyết định 3: Thích nghi Cục bộ (Targeted MF Adaptation) thay vì Thay đổi Toàn bộ
Thay vì cho phép hệ mờ tự sinh luật mới không kiểm soát hoặc dịch chuyển toàn bộ 5 biến cảm biến:
- Chỉ thích nghi hai biến vật lý thực sự bị tác động (`Rotational speed` và `Torque`).
- Đóng băng 3 biến không bị trôi dạt (`Air temperature`, `Process temperature`, `Tool wear`), đóng băng cấu trúc 12 luật chuyên gia và giữ nguyên ngưỡng phân loại $\tau = 0.67$.
- Thiết kế này ngăn ngừa hiện tượng **quên thảm khốc (catastrophic forgetting)** và giữ vững tính minh bạch, diễn giải được của hệ mờ.

---

## 3. Chi tiết Triển khai và Kết quả Thực nghiệm Định lượng

Toàn bộ các thử nghiệm được thực thi tuần tự, kiểm soát chặt chẽ từng cell trong notebook [`notebooks/06_concept_drift.ipynb`](file:///notebooks/06_concept_drift.ipynb):

### 3.1. Phase 6.1 — Khảo sát Điểm số Bất thường Xung quanh Vùng Trôi dạt (Cell 6.1)

#### 3.1.1. Mã nguồn Thực thi
```python
import numpy as np

def summarize_score_region(scores, start, end, name):
    region = np.asarray(scores[start:end])

    print(f"\n{name}")
    print(f"Range: {start} -> {end - 1}")
    print(f"Count: {len(region)}")
    print(f"Mean: {region.mean():.4f}")
    print(f"Median: {np.median(region):.4f}")
    print(f"Std: {region.std():.4f}")
    print(f"Min: {region.min():.4f}")
    print(f"Max: {region.max():.4f}")
```

#### 3.1.2. Kết quả Thực nghiệm
```text
=== SUDDEN DRIFT ===

Before Drift
Range: 0 -> 999
Count: 1000
Mean: 0.3159
Median: 0.2249
Std: 0.1476
Min: 0.1944
Max: 0.6898

After Drift
Range: 1000 -> 1999
Count: 1000
Mean: 0.4480
Median: 0.5000
Std: 0.1739
Min: 0.1944
Max: 0.6898

=== GRADUAL DRIFT ===

Before Transition
Range: 0 -> 799
Count: 800
Mean: 0.3200
Median: 0.2251
Std: 0.1509
Min: 0.1944
Max: 0.6898

Transition
Range: 800 -> 1199
Count: 400
Mean: 0.3650
Median: 0.3191
Std: 0.1629
Min: 0.1944
Max: 0.6898

After Transition
Range: 1200 -> 1999
Count: 800
Mean: 0.4535
Median: 0.5000
Std: 0.1743
Min: 0.1944
Max: 0.6898
```

#### 3.1.3. Phân tích Hiện tượng
1. **Trước trôi dạt (Nominal Region):** Cả hai kịch bản đều có giá trị trung bình $\approx 0.316 - 0.320$ và trung vị $\approx 0.225$. Đây là mức kích hoạt của trạng thái vận hành bình thường (Low Anomaly).
2. **Giai đoạn chuyển tiếp Gradual ($800 \to 1199$):** Điểm số trung bình tăng dần lên $0.3650$, trung vị dịch chuyển lên $0.3191$, phản ánh sự lan truyền tiệm tiến theo hệ số pha trộn $\alpha(t)$.
3. **Sau trôi dạt (Post-Drift Region):** Trung vị của cả hai kịch bản nhảy vọt lên đúng mức **$0.5000$** (tâm của tập mờ *MEDIUM*), kéo giá trị trung bình lên $\approx 0.448 - 0.453$. Biên độ dao động tối đa vẫn giữ ở mức $0.6898$, khẳng định không có hiện tượng nổ giá trị hay bão hòa biên giải mờ.

---

### 3.2. Phase 6.2 — Định lượng Mức Dịch chuyển Điểm số (Cell 6.2)

#### 3.2.1. Mã nguồn Thực thi
```python
import numpy as np

def compare_score_regions(scores, start_a, end_a, start_b, end_b, name_a, name_b):
    region_a = np.asarray(scores[start_a:end_a])
    region_b = np.asarray(scores[start_b:end_b])

    mean_a = region_a.mean()
    mean_b = region_b.mean()

    median_a = np.median(region_a)
    median_b = np.median(region_b)

    print(f"\n{name_a} vs {name_b}")
    print(f"Mean:   {mean_a:.4f} -> {mean_b:.4f}")
    print(f"Delta:  {mean_b - mean_a:+.4f}")
    print(f"Median: {median_a:.4f} -> {median_b:.4f}")
    print(f"Delta:  {median_b - median_a:+.4f}")
```

#### 3.2.2. Kết quả Thực nghiệm
```text
=== PHASE 6.2 — SCORE SHIFT SUMMARY ===

Before Drift vs After Drift
Mean:   0.3159 -> 0.4480
Delta:  +0.1321
Median: 0.2249 -> 0.5000
Delta:  +0.2751

Before Transition vs After Transition
Mean:   0.3200 -> 0.4535
Delta:  +0.1335
Median: 0.2251 -> 0.5000
Delta:  +0.2749
```

#### 3.2.3. Bảng Tổng hợp So sánh Định lượng

| Kịch bản Thực nghiệm | Vùng So sánh Đối chứng | $\text{Mean}_{\text{trước}}$ | $\text{Mean}_{\text{sau}}$ | $\Delta \text{Mean}$ | $\text{Median}_{\text{trước}}$ | $\text{Median}_{\text{sau}}$ | $\Delta \text{Median}$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Sudden Drift** | $0 \to 999$ vs $1000 \to 1999$ | $0.3159$ | $0.4480$ | **$+0.1321$** | $0.2249$ | $0.5000$ | **$+0.2751$** |
| **Gradual Drift** | $0 \to 799$ vs $1200 \to 1999$ | $0.3200$ | $0.4535$ | **$+0.1335$** | $0.2251$ | $0.5000$ | **$+0.2749$** |

> [!NOTE]
> **Nhận xét Khoa học cốt lõi:**
> Mức chênh lệch ($\Delta\text{Mean} \approx +0.133$ và $\Delta\text{Median} \approx +0.275$) giữa hai kịch bản gần như trùng khớp hoàn toàn. Điều này kiểm chứng tính chuẩn xác trong thiết kế của Phase 4: cả Sudden và Gradual Drift đều dẫn đến cùng một trạng thái phân phối cảm biến cuối cùng, chỉ khác biệt ở động học chuyển tiếp.

---

### 3.3. Phase 6.3 — Kiểm định Điểm Kích hoạt Thích nghi (Cell 6.3)

#### 3.3.1. Mục tiêu và Mã nguồn
Kiểm tra mối tương quan thời gian giữa điểm kích hoạt cảnh báo trôi dạt của ADWIN (Phase 5) và các mốc ground truth tiêm trôi dạt.

```python
sudden_drift_start = 1000
gradual_transition_start = 800
gradual_transition_end = 1200

sudden_detections = [1183]
gradual_detections = [1247]
```

#### 3.3.2. Kết quả Thực nghiệm
```text
=== PHASE 6.3 — ADAPTATION TRIGGER CHECK ===

Sudden Drift
Injected drift starts at index: 1000
ADWIN detections: [1183]
Detection 1183: AFTER drift start

Gradual Drift
Transition: 800 -> 1199
ADWIN detections: [1247]
Detection 1247: AFTER transition end
```

- **Sudden Drift:** ADWIN kích hoạt tại $t = 1183$ ($> 1000$). Điểm kích hoạt nằm sau điểm tiêm trôi dạt $183$ mẫu.
- **Gradual Drift:** ADWIN kích hoạt tại $t = 1247$ ($> 1200$). Điểm kích hoạt nằm sau khi quá trình chuyển tiếp kết thúc $47$ mẫu.
- **Kết luận:** Cả hai điểm kích hoạt đều đáp ứng tính hợp lệ nhân quả tuyệt đối: **Hệ thống không phát tín hiệu thích nghi giả trước khi drift xuất hiện.**

---

### 3.4. Phase 6.4 — Ranh giới Dữ liệu Khả dụng cho Thích nghi (Cell 6.4)

#### 3.4.1. Kết quả Thực nghiệm
```text
=== PHASE 6.4 — ADAPTATION DATA BOUNDARY ===

Sudden Drift
Drift detection index: 1183
Adaptation can start from: 1184
Remaining stream samples: 816

Gradual Drift
Drift detection index: 1247
Adaptation can start from: 1248
Remaining stream samples: 752

Rule
Adaptation must NOT use samples before ADWIN detection.
Samples used for adaptation must be separated from samples used for evaluation.
```

#### 3.4.2. Ý nghĩa Thực nghiệm
- **Sudden Drift:** Sau mốc phát hiện $1183$, hệ thống còn **816 mẫu** ($1184 \to 1999$) để tiến hành thích nghi và đánh giá hồi phục hiệu năng trực tuyến.
- **Gradual Drift:** Sau mốc phát hiện $1247$, hệ thống còn **752 mẫu** ($1248 \to 1999$) trong miền phân phối mới đã ổn định.

---

### 3.5. Phase 6.5 — Chuẩn hóa Giao thức Trực tuyến Prequential (Cell 6.5)

#### 3.5.1. Định nghĩa Chu trình Prequential (Test-Then-Adapt)
Giao thức đánh giá được thiết lập chặt chẽ theo 6 bước không thể đảo ngược cho mỗi mẫu cảm biến $x_t$:

$$\begin{aligned}
\text{Bước 1:} & \quad \text{Nhận mẫu cảm biến mới } x_t \\
\text{Bước 2:} & \quad \text{Tính toán điểm bất thường: } A(t) = \text{FIS}_{t-1}(x_t) \quad \text{(Dùng tri thức hiện tại)} \\
\text{Bước 3:} & \quad \text{Ghi nhận } A(t) \text{ và dự báo nhãn phục vụ đánh giá (Evaluation Metric)} \\
\text{Bước 4:} & \quad \text{Cập nhật bộ phát hiện trôi dạt: } \text{ADWIN.update}(A(t)) \\
\text{Bước 5:} & \quad \text{Nếu cờ trôi dạt đã bật, cho phép } x_t \text{ tham gia vào bộ thích nghi: } \text{FIS}_t = \text{Adapt}(\text{FIS}_{t-1}, x_t) \\
\text{Bước 6:} & \quad \text{Tuyệt đối không cập nhật } \text{FIS}_t \text{ trước khi } x_t \text{ được chấm điểm.}
\end{aligned}$$

#### 3.5.2. Kết quả Output Xác nhận
```text
=== PHASE 6.5 — ONLINE ADAPTATION / EVALUATION PROTOCOL ===

Protocol:
1. Receive sample x_t
2. Compute anomaly score using current fuzzy knowledge
3. Record prediction / score for evaluation
4. Update drift detector
5. If drift has been detected, x_t may become available for future adaptation
6. Never adapt before evaluating the sample

Sudden Drift
Detection index: 1183
First post-detection sample: 1184
Samples available for post-detection adaptation/evaluation: 816

Gradual Drift
Detection index: 1247
First post-detection sample: 1248
Samples available for post-detection adaptation/evaluation: 752

Leakage Check
Evaluation happens BEFORE adaptation for each sample.
No future sample is used to evaluate the current sample.
```

---

### 3.6. Phase 6.6 — Phân định Không gian Tri thức Mờ Cần Thích nghi (Cell 6.6)

#### 3.6.1. Nguyên tắc Phân định Tri thức
Không tiến hành thích nghi mù quáng (blind adaptation) trên toàn bộ hệ mờ. Việc khoanh vùng dựa trên nguyên lý vật lý:

```text
=== PHASE 6.6 — FUZZY KNOWLEDGE CANDIDATES ===

Static Fuzzy Knowledge
Inputs:
- Air temperature
- Process temperature
- RPM
- Torque
- Tool wear

Controlled Drift Variables:
- RPM
- Torque

Non-Drift Variables:
- Air temperature
- Process temperature
- Tool wear

Candidate Adaptation Targets:
1. RPM membership functions
2. Torque membership functions

Protected Knowledge:
Air temperature membership functions
Process temperature membership functions
Tool wear membership functions
Static rule structure
Static validation threshold
```

#### 3.6.2. Bảng Phân định Trách nhiệm Tri thức Mờ cho Phase 7

| Thành phần Hệ Mờ | Trạng thái trong Phase 7 | Cơ sở Lý luận Khoa học |
| :--- | :---: | :--- |
| **RPM Membership Functions** | **EVOLVE / ADAPT** | Biến chịu trôi dạt trực tiếp ($-150\text{ rpm}$); cần định vị lại tâm/biên tập mờ |
| **Torque Membership Functions** | **EVOLVE / ADAPT** | Biến chịu trôi dạt trực tiếp ($+8\text{ Nm}$); cần định vị lại tâm/biên tập mờ |
| **Air Temperature MFs** | **BẢO VỆ (PROTECTED)** | Không chịu trôi dạt; giữ nguyên phân phối từ tập huấn luyện ban đầu |
| **Process Temperature MFs** | **BẢO VỆ (PROTECTED)** | Không chịu trôi dạt; bảo toàn tri thức nhiệt động học |
| **Tool Wear MFs** | **BẢO VỆ (PROTECTED)** | Không chịu trôi dạt; bảo toàn mô hình hao mòn dao cắt |
| **Cấu trúc 12 Luật Mờ Mamdani** | **BẢO VỆ (PROTECTED)** | Quan hệ nhân quả ngữ nghĩa giữa các biến là bất biến; chỉ ngữ nghĩa mức độ (MF) thay đổi |
| **Ngưỡng Phân loại $\tau = 0.67$** | **BẢO VỆ (PROTECTED)** | Giữ nguyên điểm tham chiếu đánh giá từ Phase 3 để so sánh đối đầu công bằng |

---

## 4. Thảo luận Khoa học và Nhận xét Phương pháp luận

### 4.1. Cơ chế Bảo toàn Ý nghĩa Ngữ nghĩa (Semantic Interpretability)
Một trong những nguy cơ lớn nhất của các hệ mờ tự tiến hóa (Evolving Fuzzy Systems) là **suy thoái ngữ nghĩa (semantic loss)**: khi các luật mờ được tự do thêm/bớt hoặc các hàm thuộc tính bị méo mó, con người không còn khả năng giải thích vì sao hệ thống đưa ra cảnh báo. 

Bằng cách bảo vệ cấu trúc 12 luật mờ chuyên gia và chỉ dịch chuyển thông số hàm thuộc tính của hai biến bị drift, hệ thống đảm bảo tính diễn giải trong suốt:
- Luật: *"NẾU RPM LOW VÀ TORQUE HIGH THÌ NGUY CƠ CAO"* vẫn giữ nguyên giá trị logic.
- Khái niệm thế nào là *"RPM LOW"* hoặc *"TORQUE HIGH"* được tinh chỉnh lại cho phù hợp với môi trường vận hành mới của động cơ sau trôi dạt.

### 4.2. Tính Khách quan trong Đánh giá Thực nghiệm
Nhờ việc chốt chặt giao thức **Prequential (Test-Then-Adapt)**:
- Không một mẫu nào ở phân đoạn sau trôi dạt được hệ mờ "học trước" khi bị chấm điểm.
- Mọi cải thiện về chỉ số $F_1$, Precision hay Recall ở Phase 7 sẽ phản ánh năng lực thích nghi thực sự của thuật toán trực tuyến, chứ không phải ảo ảnh do overfitting hay data leakage.

---

## 5. Kết luận và Kế hoạch Chuyển tiếp sang Phase 7

### 5.1. Tổng kết Đóng Phase 6
- Toàn bộ 6 cell thực nghiệm (`6.1` $\to$ `6.6`) đã hoàn thành chính xác, nhất quán 100% trong notebook độc lập [`notebooks/06_concept_drift.ipynb`](file:///notebooks/06_concept_drift.ipynb).
- Tất cả các tệp dữ liệu, notebook và tài liệu từ Phase 1 đến Phase 5 được giữ nguyên vẹn tuyệt đối.
- Bằng chứng định lượng về sự dịch chuyển điểm bất thường của hệ mờ tĩnh đã được xác lập vững chắc.
- Ranh giới thích nghi, giao thức prequential và phạm vi tham số được phép tiến hóa đã được phê duyệt và niêm phong phương pháp luận.

### 5.2. Kế hoạch Triển khai Chi tiết Phase 7 (Evolving Fuzzy Reasoning System)
Khi bước sang Phase 7, các nhiệm vụ kỹ thuật cụ thể bao gồm:
1. **Thiết kế Động cơ Thích nghi Hàm Thuộc tính (Online MF Adaptation Mechanism):**
   - Triển khai cơ chế cập nhật trực tuyến các thông số hình thang/tam giác của `Rotational speed` và `Torque` (dịch chuyển tâm và độ rộng dựa trên cửa sổ thống kê trượt hoặc cập nhật đệ quy).
2. **Thực thi Vòng lặp Prequential Streaming:**
   - Chạy luồng trên 816 mẫu của Sudden Drift ($t = 1184 \to 1999$).
   - Chạy luồng trên 752 mẫu của Gradual Drift ($t = 1248 \to 1999$).
3. **So sánh Đối chuẩn Hiệu năng (Static Baseline vs. Evolving Fuzzy):**
   - Đánh giá sự phục hồi của Anomaly Score về phân phối danh định.
   - So sánh định lượng ma trận nhầm lẫn (Confusion Matrix), Precision, Recall và $F_1$-score tại ngưỡng $\tau = 0.67$ giữa hệ mờ tĩnh bị suy thoái và hệ mờ tự tiến hóa.
