# Phase 8 — Đánh Giá Hiệu Năng Toàn Diện và Trực Quan Hóa Hệ Suy Luận Mờ Tĩnh và Tự Thích Ứng Dưới Controlled Sensor Distribution Shift

---

## 1. Tóm Tắt Khoa Học (Executive Summary)

### 1.1. Bối Cảnh và Mục Tiêu Tổng Kết
Phase 8 là giai đoạn tổng kết thực nghiệm và đóng băng khoa học của toàn bộ đề tài nghiên cứu: *"Xây dựng hệ suy luận mờ tự tiến hóa phát hiện bất thường trên dòng dữ liệu cảm biến dưới tác động của trôi dạt dữ liệu"*. 

Mục tiêu trung tâm của Phase 8 là:
1. **Tái tạo độc lập và khép kín (Self-contained End-to-end Reconstruction):** Tái tạo toàn bộ chuỗi thực nghiệm từ nạp dữ liệu gốc (`ai4i2020.csv`), thiết lập dòng dữ liệu tuần tự ($N = 2,000$ mẫu), tiêm trôi dạt cảm biến có kiểm soát, suy luận mờ Mamdani tĩnh, giám sát trôi dạt bằng thuật toán ADWIN, thích ứng hàm thuộc tính cục bộ dựa trên cửa sổ đệm, đến đánh giá hiệu năng phân loại theo giao thức Prequential chuẩn xác mà không phụ thuộc vào trạng thái bộ nhớ của các notebook trước.
2. **Kiểm định tính toàn vẹn và ngăn chặn rò rỉ dữ liệu (Integrity & Leakage Verification):** Thiết lập các kiểm định tính toàn vẹn kỹ thuật (Cell 8.10) và các cờ kiểm soát diễn giải khoa học (Cell 8.16) nhằm bảo đảm không có hiện tượng rò rỉ thông tin tương lai (*zero data leakage*), bảo toàn tri thức chuyên gia không bị trôi dạt, và cố định tuyệt đối ngưỡng quyết định $\tau = 0.67$ được lựa chọn trên tập Validation theo tiêu chí $F_1$ định trước.
3. **Lượng hóa trung thực và khách quan hiệu năng:** Đánh giá hành vi của mô hình Static Fuzzy và Evolving Fuzzy trên 3 dòng dữ liệu (Control, Sudden Drift, Gradual Drift), phân tích bản chất đánh đổi thực nghiệm giữa kiểm soát cảnh báo giả (*false-positive control*) và khả năng bao phủ bất thường (*anomaly recall*), kiên quyết loại trừ các nhận định phóng đại (*overclaims*).

---

### 1.2. Tóm Tắt Phát Hiện Thực Nghiệm Chính
Dưới hai kịch bản dịch chuyển phân phối cảm biến có kiểm soát (*controlled sensor distribution shift*), các bằng chứng thực nghiệm thu được từ chuỗi kiểm tra độc lập ghi nhận:

1. **Giảm mức điểm bất thường nền sau thích ứng:**
   - Dưới tác động của controlled sensor distribution shift trên RPM và Torque (injected shift: $\Delta\text{RPM} = -150\text{ rpm}$, $\Delta\text{Torque} = +8\text{ Nm}$), mô hình Static Fuzzy xuất hiện sự gia tăng mức anomaly score nền, đẩy điểm số bất thường trung bình toàn luồng từ $0.315161$ (Control) lên $0.381982$ (Sudden) và $0.382425$ (Gradual).
   - Mô hình Evolving Fuzzy — thông qua cơ chế tịnh tiến hàm thuộc tính cục bộ của RPM và Torque dựa trên độ lệch kỳ vọng trong cửa sổ đệm $W = 200$ mẫu sau cảnh báo ADWIN (độ dịch chuyển ước lượng từ buffer: $\Delta\text{RPM} = -156.214228$, $\Delta\text{Torque} = +7.301500$ ở Sudden; $\Delta\text{RPM} = -161.959228$, $\Delta\text{Torque} = +8.053000$ ở Gradual) — đã làm giảm mức anomaly score nền sau adaptation xuống $0.325958$ ở Sudden và $0.315719$ ở Gradual, gần với mức trung bình của Control ($0.315161$).

2. **Kiểm soát mạnh mẽ tỷ lệ báo động giả (FPR Reduction):**
   - Sự dịch chuyển hàm thuộc tính giúp tỷ lệ các mẫu vận hành bình thường bị kích hoạt nhầm luật cảnh báo bất thường giảm đáng kể.
   - Trên quy mô toàn bộ dòng dữ liệu kiểm tra 2,000 mẫu theo giao thức Prequential, số lượng mẫu cảnh báo giả ($\text{FP}$) giảm đáng kể: từ $114 \to 56$ mẫu ở Sudden Drift (giảm $50.88\%$) và từ $113 \to 61$ mẫu ở Gradual Drift (giảm $46.02\%$).
   - Tỷ lệ báo động giả ($\text{FPR}$) giảm tương ứng từ $0.0581 \to 0.0286$ (Sudden) và từ $0.0576 \to 0.0311$ (Gradual), nâng độ đặc hiệu ($\text{Specificity}$) từ $\approx 94.2\%$ lên trên $96.8\% - 97.1\%$.

3. **Cải thiện độ chuẩn xác và chỉ số $F_1$ tổng thể:**
   - Do số lượng cảnh báo giả giảm mạnh trong khi nhãn lỗi thực tế trong tập kiểm tra rất hiếm ($39 / 2000$ mẫu, chiếm $1.95\%$), độ chính xác ($\text{Precision}$) của mô hình Evolving tăng đáng kể: từ $0.1364 \to 0.2113$ ở Sudden Drift và từ $0.1374 \to 0.1867$ ở Gradual Drift.
   - Nhờ đó, chỉ số tổng hợp $F_1\text{-score}$ ghi nhận mức tăng từ $0.2105 \to 0.2727$ ($+0.0622$) trong kịch bản Sudden Drift và từ $0.2118 \to 0.2456$ ($+0.0338$) trong kịch bản Gradual Drift.

---

### 1.3. Bản Chất Đánh Đổi Hiệu Năng Quan Sát Được (Observed Performance Trade-off)
Thực nghiệm không hỗ trợ kết luận rằng mô hình Evolving Fuzzy *"vượt trội toàn diện"* so với Static Fuzzy. Dữ liệu thực tế cho thấy một sự đánh đổi thực nghiệm rõ nét (*observed performance trade-off*) giữa việc kiểm soát cảnh báo giả và độ nhạy phát hiện sự cố khi ngưỡng quyết định $\tau = 0.67$ được lựa chọn trên tập Validation theo tiêu chí $F_1$ định trước và sau đó được đóng băng:

1. **Gia tăng số ca bỏ sót lỗi ($\text{FN}$) và suy giảm Recall:**
   - Khi mặt bằng phân phối điểm bất thường được hạ thấp để đưa các mẫu bình thường về dưới ngưỡng $\tau = 0.67$, một số mẫu sự cố thực tế có biểu hiện bất thường ở mức biên (*marginal anomalies*) cũng bị kéo điểm số xuống dưới ngưỡng.
   - Trên toàn luồng dữ liệu, số ca phát hiện đúng ($\text{TP}$) của Evolving Fuzzy giảm so với Static Fuzzy: từ $18 \to 15$ ca ở Sudden Drift (bỏ sót thêm $3$ lỗi) và từ $18 \to 14$ ca ở Gradual Drift (bỏ sót thêm $4$ lỗi).
   - Hệ quả là chỉ số bao phủ bất thường ($\text{Recall}$) giảm từ $0.4615 \to 0.3846$ (Sudden Drift) và từ $0.4615 \to 0.3590$ (Gradual Drift); tỷ lệ bỏ sót sự cố ($\text{FNR}$) tăng tương ứng từ $0.5385 \to 0.6154$ (Sudden) và $0.5385 \to 0.6410$ (Gradual).

2. **Suy giảm độ chính xác cân bằng (Balanced Accuracy):**
   - Do Balanced Accuracy là trung bình của Recall và Specificity, mức giảm của Recall ($-7.69$ percentage points ở Sudden; $-10.26$ percentage points ở Gradual) lớn hơn mức tăng của Specificity ($+2.96$ percentage points ở Sudden; $+2.65$ percentage points ở Gradual), dẫn đến Balanced Accuracy giảm trong mô hình Evolving Fuzzy trên cả hai kịch bản: $0.6780$ so với $0.7017$ (Sudden Drift) và $0.6639$ so với $0.7020$ (Gradual Drift).

---

### 1.4. Tuyên Bố Đóng Băng Thực Nghiệm & Ranh Giới Khoa Học
1. **Trạng thái đóng băng (Frozen Status):** Toàn bộ các cell thuộc Phase 8 trong notebook [`notebooks/08_final_evaluation.ipynb`](../notebooks/08_final_evaluation.ipynb) đã được thực thi hoàn tất và khóa cứng. Không có thêm bất kỳ tế bào tính toán, tinh chỉnh tham số hay can thiệp hồi tố nào được thực hiện trên mã nguồn hay kết quả thực nghiệm.
2. **Ranh giới diễn giải khoa học (Scientific Guardrails):**
   - Hiện tượng trôi dạt trong nghiên cứu được định nghĩa chính xác là **dịch chuyển phân phối dữ liệu cảm biến có kiểm soát** (*controlled sensor distribution shift*), không mở rộng thành khái niệm trôi dạt khái niệm thực chất $P(Y|X)$ (*concept drift*) do bản chất nhãn của bộ dữ liệu AI4I 2020 không thay đổi theo thời gian.
   - Cơ chế thích ứng được định danh đúng bản chất là **thích ứng tịnh tiến hàm thuộc tính dựa trên độ lệch thống kê cửa sổ đệm** (*buffer-based centroid heuristic adaptation*), không tuyên bố là cơ chế học máy tự trị hoàn toàn (*fully autonomous online learning*).
   - Ngưỡng phân loại $\tau = 0.67$ được duy trì cố định, phản ánh trung thực bài toán vận hành công nghiệp khi hệ thống giám sát chưa được trang bị cơ chế tự động thích ứng ngưỡng quyết định.

---

## 2. Phương Pháp Luận & Giao Thức Đánh Giá (Methodology & Evaluation Protocol)

### 2.1. Phân Chia Dữ Liệu Tuần Tự & Nguyên Tắc Đóng Băng Tham Số
Quy trình thực nghiệm tuân thủ nghiêm ngặt giao thức phân chia dữ liệu theo trình tự thời gian (*Chronological Split*), bảo đảm cấu trúc chuỗi thời gian của cảm biến công nghiệp không bị xáo trộn:

- **Tập Huấn luyện (Train Partition):** Chỉ số $0 \to 5,999$ (tương ứng $\text{UDI } 1 \to 6,000$, gồm $6,000$ mẫu). Được sử dụng độc quyền ở Phase 2 để trích xuất phân phối thống kê ban đầu và thiết kế các hàm thuộc tính tĩnh của hệ mờ Mamdani.
- **Tập Kiểm định (Validation Partition):** Chỉ số $6,000 \to 7,999$ (tương ứng $\text{UDI } 6,001 \to 8,000$, gồm $2,000$ mẫu). Được sử dụng độc quyền ở Phase 3 nhằm quét và xác định ngưỡng quyết định tối ưu theo tiêu chí $F_1$ định trước, thu được ngưỡng cố định $\tau = 0.67$.
- **Dòng Kiểm tra Thời gian thực (Streaming Test Partition):** Chỉ số $8,000 \to 9,999$ (tương ứng $\text{UDI } 8,001 \to 10,000$, gồm $2,000$ mẫu). Đóng vai trò là dòng dữ liệu cảm biến thời gian thực chưa từng được quan sát trong pha thiết kế mô hình.

> [!NOTE]
> **Đính chính:** phiên bản trước của mục này ghi nhầm Train = 5.000 mẫu, Validation = 3.000 mẫu. Mã nguồn thực tế (`notebooks/03_static_fuzzy_evaluation.ipynb`: `df.iloc[:6000]`, `df.iloc[6000:8000]`, `df.iloc[8000:]`) và Protocol Phase 1.5 dùng **6.000 / 2.000 / 2.000**. Đã sửa cho khớp mã nguồn.

> [!IMPORTANT]
> **Nguyên tắc đóng băng tham số (Frozen Parameter Invariance):**
> Ngưỡng phân loại $\tau = 0.67$ được lựa chọn duy nhất từ tập Validation và bị đóng băng tuyệt đối trên toàn bộ các kịch bản của Test Stream. Trong suốt quá trình đánh giá ở Phase 8, không có bất kỳ bước tinh chỉnh ngưỡng (threshold retuning) nào dựa trên nhãn của tập Test, bảo đảm tính khách quan và ngăn chặn hoàn toàn rò rỉ thông tin tối ưu hóa.

---

### 2.2. Kiến Trúc Hệ Suy Luận Mờ Mamdani Tĩnh (Static Mamdani FIS Engine)
Hệ suy luận mờ cơ sở được thiết kế dựa trên cấu trúc chuyên gia Mamdani chuẩn, bao gồm 5 biến cảm biến đo lường vật lý:

1. **Không gian biến đầu vào (Input Variables):**
   - $x_1$: `Air temperature [K]` (Nhiệt độ không khí)
   - $x_2$: `Process temperature [K]` (Nhiệt độ quy trình)
   - $x_3$: `Rotational speed [rpm]` (Tốc độ quay trục chính)
   - $x_4$: `Torque [Nm]` (Mô-men xoắn)
   - $x_5$: `Tool wear [min]` (Thời gian mòn dao cụ)

2. **Cấu trúc hàm thuộc tính (Membership Functions - MFs):**
   - Mỗi biến được mô hình hóa bởi 3 tập mờ: `Low` (Thấp), `Medium` (Trung bình), `High` (Cao).
   - Tổng cộng 15 hàm thuộc tính hình học: Các tập `Medium` sử dụng dạng tam giác đối xứng (`trimf`); các tập biên `Low` và `High` sử dụng dạng hình thang (`trapmf`) với vùng bão hòa mở rộng ra vô cực để đảm bảo tính bao phủ toàn miền giá trị vật lý.

3. **Cơ sở 12 luật Mamdani chuyên gia (Fuzzy Rule Base):**
   - Tập luật được đúc kết từ tri thức chẩn đoán hư hỏng cơ khí công nghiệp (đặc biệt các dạng lỗi quá tải công suất - PWF, mòn dụng cụ - TWF, và tiêu tán nhiệt - HDF).
   - *Luật R1 đặc thù:* Kiểm soát trạng thái công suất tải cao bất thường với điều kiện tiền đề gồm 3 biến đồng thời:
     $$\text{IF } (\text{RPM is Low}) \text{ AND } (\text{Torque is High}) \text{ AND } (\text{Air Temperature is High}) \text{ THEN } (\text{Anomaly is High})$$
   - 11 luật còn lại bao phủ các tương quan áp lực mô-men xoắn, tốc độ tới hạn và suy thoái do mòn dao.

4. **Cơ chế suy luận và giải mờ liên tục (Defuzzification Engine):**
   - **Phép hợp suy luận (Fuzzy Implication):** Sử dụng toán tử cực tiểu Mamdani: $\mu_{\text{rule}_k}(y) = \min(\alpha_k, \mu_{\text{consequent}_k}(y))$, trong đó $\alpha_k$ là mức độ kích hoạt (firing strength) tính theo phép giao $\min$ của các điều kiện tiền đề.
   - **Phép tích lũy mờ (Aggregation):** Sử dụng toán tử cực đại $\max$ trên tất cả các luật kích hoạt: $\mu_{\text{agg}}(y) = \max_{k} \mu_{\text{rule}_k}(y)$.
   - **Giải mờ trọng tâm liên tục (Centroid Defuzzification):** Điểm bất thường liên tục $A(t) \in [0, 1]$ được tính toán chính xác bằng phương pháp tích phân trọng tâm thông qua phép xấp xỉ hình thang trên 1,000 điểm rời rạc trong đoạn $[0, 1]$:
     $$A(t) = \frac{\int_{0}^{1} y \cdot \mu_{\text{agg}}(y) \, dy}{\int_{0}^{1} \mu_{\text{agg}}(y) \, dy} \approx \frac{\sum_{j=1}^{1000} y_j \cdot \mu_{\text{agg}}(y_j)}{\sum_{j=1}^{1000} \mu_{\text{agg}}(y_j)}$$
     *(Hiện thực chuẩn xác bằng hàm `numpy.trapezoid`, đảm bảo tính ổn định và triệt tiêu sai số làm tròn số học).*

---

### 2.3. Cơ Chế Giám Sát Trôi Dạt ADWIN Trên Dòng Anomaly Score
Để phát hiện sự biến đổi phân phối cảm biến mà không cần nhãn giám sát, thuật toán ADWIN (*Adaptive Windowing*) được áp dụng trực tiếp trên chuỗi điểm bất thường $A(t) \in [0, 1]$ do Static FIS sinh ra:

1. **Nguyên lý ADWIN:** ADWIN tự động duy trì một cửa sổ trượt có kích thước biến thiên của các điểm số gần nhất. Mỗi khi hai nửa cửa sổ con xuất hiện sự khác biệt có ý nghĩa thống kê về giá trị trung bình vượt quá ngưỡng Hoeffding bound:
   $$|\bar{\mu}_{W_0} - \bar{\mu}_{W_1}| > \epsilon_{\text{cut}}$$
   thuật toán sẽ phát tín hiệu cảnh báo trôi dạt và cắt ngắn cửa sổ để loại bỏ dữ liệu cũ.
2. **Tham số độ tin cậy:** Cố định tham số $\delta = 0.002$ xuyên suốt mọi kịch bản.
3. **Mốc phát hiện thực tế:**
   - Trong kịch bản *Sudden Drift* (bắt đầu tiêm tại $t = 1000$), ADWIN phát hiện trôi dạt tại mẫu **$t_{\text{detect}} = 1183$** (độ trễ phát hiện là $183$ mẫu).
   - Trong kịch bản *Gradual Drift* (chuyển tiếp $t = 800 \to 1199$, đạt mức trôi dạt tối đa từ $t = 1200$), ADWIN phát hiện trôi dạt tại mẫu **$t_{\text{detect}} = 1247$** (độ trễ là $47$ mẫu kể từ khi trôi dạt đạt cực đại).
   - Trong kịch bản *Control Stream*, ADWIN không phát bất kỳ cảnh báo nào trong suốt 2,000 mẫu, bảo đảm không có phát hiện giả mạo khi dòng dữ liệu ổn định.

---

### 2.4. Cơ Chế Thích Ứng Cục Bộ Dựa Trên Cửa Sổ Đệm Thống Kê (Buffer-based Centroid Heuristic Adaptation)
Sau khi ADWIN phát tín hiệu trôi dạt tại $t_{\text{detect}}$, quy trình thích ứng mờ được khởi động với các nguyên tắc nghiêm ngặt:

1. **Cửa sổ đệm tích lũy mẫu ($W = 200$ mẫu):**
   - Dữ liệu cảm biến được tích lũy tuần tự vào bộ đệm không giám sát trong đoạn thời gian $t \in [t_{\text{detect}} + 1, t_{\text{detect}} + W]$:
     - Kịch bản Sudden Drift: Bộ đệm gồm 200 mẫu từ $t = 1184 \to 1383$.
     - Kịch bản Gradual Drift: Bộ đệm gồm 200 mẫu từ $t = 1248 \to 1447$.
2. **Ước lượng độ lệch tâm hàm thuộc tính:**
   - Tính toán giá trị trung bình mẫu của từng cảm biến trong bộ đệm: $\bar{x}_{\text{buffer}, v} = \frac{1}{W} \sum_{i=1}^{W} x_{i, v}$.
   - Xác định độ dịch chuyển của biến $v$ so với tâm hàm thuộc tính mức trung bình ban đầu:
     $$\Delta_v = \bar{x}_{\text{buffer}, v} - C_{\text{MEDIUM}, v}$$
   - Giá trị dịch chuyển thực nghiệm ước lượng từ buffer đạt được:
     - *Sudden Drift:* $\Delta\text{RPM} = -156.214228\text{ rpm}$, $\Delta\text{Torque} = +7.301500\text{ Nm}$.
     - *Gradual Drift:* $\Delta\text{RPM} = -161.959228\text{ rpm}$, $\Delta\text{Torque} = +8.053000\text{ Nm}$.
3. **Tịnh tiến hàm thuộc tính cục bộ (Localized MF Translation):**
   - Chỉ tịnh tiến tọa độ các điểm mốc của 6 hàm thuộc tính thuộc 2 biến chịu tác động trôi dạt:
     $$C_{\text{new}} = C_{\text{old}} + \Delta_v \quad (v \in \{\text{rpm, torque}\})$$
4. **Cơ chế bảo toàn tri thức chuyên gia (Protected Expert Knowledge):**
   - Toàn bộ 9 hàm thuộc tính của các biến nhiệt độ (`Air temperature`, `Process temperature`) và độ mòn dao (`Tool wear`) được giữ nguyên vẹn 100% (độ dịch chuyển bằng $0.0$).
   - Tập 12 luật Mamdani và ngữ nghĩa ngôn ngữ chuyên gia được bảo toàn hoàn toàn.

---

### 2.5. Giao Thức Đánh Giá Trực Tuyến Prequential (Test-Then-Adapt) & Loại Trừ Rò Rỉ Dữ Liệu
Để phản ánh trung thực quá trình vận hành thời gian thực của hệ thống giám sát và bảo đảm tính toàn vẹn của kết quả, giao thức đánh giá Prequential (*Test-Then-Adapt*) được triển khai theo quy trình phân đoạn thời gian chặt chẽ:

```text
Stream Timeline (t = 0 -> 1999)
├────────────────────────────────┬───────────────────────────┬──────────────────────────────┤
│ 1. Pre-adaptation (Static FIS) │ 2. Adaptation Buffer (W)  │ 3. Post-adaptation (Evolving)│
│    Chấm điểm bằng Static FIS   │    Test bằng Static FIS   │    Chấm điểm bằng Evolving   │
│    t: 0 -> t_detect            │    và đưa mẫu vào Buffer  │    t: t_detect + W + 1 -> 1999│
│                                │    t: t_detect+1 -> +W    │                              │
└────────────────────────────────┴───────────────────────────┴──────────────────────────────┘
```

1. **Pha tiền thích ứng ($t \le t_{\text{detect}} + W$):**
   - Toàn bộ các mẫu từ đầu luồng đến hết cửa sổ đệm thích ứng ($t = 0 \to 1383$ ở Sudden; $t = 0 \to 1447$ ở Gradual) được chấm điểm và dự báo độc quyền bằng mô hình **Static Fuzzy**.
   - Điều này bảo đảm điểm số của Evolving Fuzzy trước khi hoàn tất thích ứng trùng khớp $100\%$ với Static Fuzzy (`Pre-adaptation equality: PASS`), loại bỏ hoàn toàn khả năng mô hình "biết trước" thông tin trôi dạt (*zero oracle boundary leakage*).
2. **Pha tích lũy đệm ($t \in [t_{\text{detect}} + 1, t_{\text{detect}} + W]$):**
   - Tuân thủ nguyên tắc *Test-Then-Adapt*: Mỗi mẫu $x_t$ khi xuất hiện trước hết được dùng để kiểm tra dự báo bằng tri thức hiện tại (Static FIS), sau đó mới được đưa vào bộ đệm thống kê. 
   - Quá trình thích ứng hoàn toàn không sử dụng nhãn lỗi $Y$ (*unsupervised adaptation*).
3. **Pha hậu thích ứng ($t > t_{\text{detect}} + W$):**
   - Sau khi cửa sổ đệm $W = 200$ mẫu kết thúc, các hàm thuộc tính mới được cập nhật. Từ thời điểm này ($t = 1384 \to 1999$ ở Sudden gồm 616 mẫu; $t = 1448 \to 1999$ ở Gradual gồm 552 mẫu), các mẫu mới đến được chấm điểm và phân loại bằng mô hình **Evolving Fuzzy**.
4. **Đánh giá hiệu năng tích hợp toàn luồng (Overall Stream Evaluation):**
   - Quỹ đạo điểm số tích hợp của mô hình Evolving Fuzzy được ghép nối tuần tự:
     $$A_{\text{evolving}}(t) = \begin{cases} 
     A_{\text{static}}(t), & \text{với } t \le t_{\text{detect}} + W \\ 
     A_{\text{adapted}}(t), & \text{với } t > t_{\text{detect}} + W 
     \end{cases}$$
   - Ma trận nhầm lẫn và các chỉ số hiệu năng toàn luồng ($N = 2,000$ mẫu) được tính toán trên toàn bộ chuỗi $A_{\text{evolving}}(t)$ tại ngưỡng cố định $\tau = 0.67$.

---

## 3. Kết Quả Thực Nghiệm Chi Tiết (Detailed Experimental Results)

### 3.1. Bảng Tổng Hợp Chỉ Số Cuối Cùng — Tái Tạo Độc Lập (Cell 8.9)

Bảng dưới đây là kết quả **tái tạo lại từ đầu** (không tái sử dụng biến số của notebook Phase 7) trên toàn bộ $N = 2{,}000$ mẫu của từng luồng, tại ngưỡng đóng băng $\tau = 0.67$:

| Scenario | Model | TP | TN | FP | FN | Precision | Recall | F1 | FPR | FNR | Specificity | Balanced Accuracy |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Control | Static | 13 | 1927 | 34 | 26 | 0.2766 | 0.3333 | 0.3023 | 0.0173 | 0.6667 | 0.9827 | 0.6580 |
| Sudden Drift | Static | 18 | 1847 | 114 | 21 | 0.1364 | 0.4615 | 0.2105 | 0.0581 | 0.5385 | 0.9419 | 0.7017 |
| Sudden Drift | Evolving | 15 | 1905 | 56 | 24 | 0.2113 | 0.3846 | 0.2727 | 0.0286 | 0.6154 | 0.9714 | 0.6780 |
| Gradual Drift | Static | 18 | 1848 | 113 | 21 | 0.1374 | 0.4615 | 0.2118 | 0.0576 | 0.5385 | 0.9424 | 0.7020 |
| Gradual Drift | Evolving | 14 | 1900 | 61 | 25 | 0.1867 | 0.3590 | 0.2456 | 0.0311 | 0.6410 | 0.9689 | 0.6639 |

> [!NOTE]
> **Đối chiếu chéo với Phase 7 (Cell 8.9 — Phase 7 Reconciliation):** Toàn bộ 5 dòng kết quả trên được tính lại độc lập bằng một pipeline dựng riêng trong Phase 8 (nạp lại dữ liệu gốc, dựng lại luồng, dựng lại hệ suy diễn Mamdani, không import biến từ notebook Phase 7). Sai số tuyệt đối lớn nhất giữa kết quả tái tạo và kết quả gốc của Phase 7 là **$4.615 \times 10^{-7}$** — nằm trong sai số làm tròn dấu phẩy động, không phải sai lệch phương pháp luận. Đây là bằng chứng thực nghiệm cho thấy kết quả Phase 7 không phải ngẫu nhiên hay lỗi cài đặt một lần, mà tái lập được bằng một pipeline độc lập thứ hai.

**Quan sát định lượng (không suy rộng vượt quá số liệu):**
- Ở cả hai kịch bản drift, chuyển từ Static sang Evolving đều **giảm FP** (Sudden: $114 \to 56$; Gradual: $113 \to 61$) đồng thời **tăng FN** (Sudden: $21 \to 24$; Gradual: $21 \to 25$). Đây là một sự đánh đổi (trade-off) quan sát được trên đúng 2 kịch bản đã thử nghiệm, chưa có cơ sở để khẳng định đây là quy luật tổng quát cho mọi cường độ/loại drift khác.
- Ở kịch bản Control, chỉ có kết quả Static. **Chưa có số liệu Evolving trên Control** (xem mục 4.2).

### 3.2. Trực Quan Hóa Đã Thực Thi (Cells 8.11 → 8.15)

Năm nhóm biểu đồ đã được dựng và chạy không lỗi trong notebook, mỗi biểu đồ đều đi kèm assertion kiểm tra miền giá trị $[0,1]$ trước khi vẽ:

1. **Cell 8.11 — Score Trajectories & Drift Detection:** 3 biểu đồ đường (Control / Sudden / Gradual) vẽ $A(t)$ theo thời gian, có đường ngang đánh dấu ngưỡng đóng băng $\tau = 0.67$, và ở hai kịch bản drift có thêm 2 đường dọc đánh dấu thời điểm ADWIN phát hiện ($t=1183$ Sudden, $t=1247$ Gradual) và thời điểm kết thúc cửa sổ thích ứng ($t=1383$ Sudden, $t=1447$ Gradual).
2. **Cell 8.12 — Static vs Evolving Score Trajectories:** chồng lớp quỹ đạo điểm số Static và Evolving trên cùng một trục thời gian cho từng kịch bản drift, xác nhận bằng assertion `Pre-adaptation equality: PASS` — tức đoạn trước khi thích ứng hoàn tất, hai đường trùng khít tuyệt đối (đúng như thiết kế test-then-adapt, không có gì đáng "wow" ở đoạn này, nó chỉ xác nhận không có leak).
3. **Cell 8.13 — Membership Functions Before/After:** so sánh hình dạng 6 hàm thuộc tính của RPM/Torque trước và sau tịnh tiến, cùng xác nhận 9 hàm thuộc tính còn lại (Air/Process/Tool wear) không đổi.
4. **Cell 8.14 — Final Metrics Visualization:** biểu đồ cột các chỉ số (Precision/Recall/F1/FPR...) theo Scenario × Model.
5. **Cell 8.15 — Final Summary Figure:** biểu đồ cột tổng hợp F1/FPR/Recall của Static và Evolving trên 2 kịch bản drift.

> [!WARNING]
> **Lưu ý khi dùng Cell 8.15 cho slide báo cáo:** biểu đồ này dùng kỹ thuật *stacked bar* (`bottom=f1_static` khi vẽ `f1_evolving`), nghĩa là cột Evolving được vẽ **chồng lên trên** cột Static thay vì đặt cạnh nhau. Về mặt kỹ thuật số liệu vẫn đúng (đã có assertion `np.allclose` khớp với bảng ở mục 3.1), nhưng cách trình bày này dễ khiến người xem hiểu nhầm rằng giá trị Evolving = Static + phần chồng thêm (cộng dồn), trong khi thực chất đây là 2 giá trị độc lập cần so sánh cạnh nhau. **Khuyến nghị:** khi đưa vào slide bảo vệ, nên vẽ lại dạng *grouped bar* (2 cột đặt cạnh nhau cho mỗi scenario) để tránh gây hiểu lầm cho hội đồng — đây là lỗi trình bày, không phải lỗi số liệu.

### 3.3. Kiểm Toán Toàn Vẹn (Cells 8.10 & 8.16)

**Cell 8.10 — Final Experiment Integrity Audit:** 11/11 hạng mục PASS, bao gồm dataset integrity, sequential stream integrity, controlled drift integrity, drift/adaptation boundary integrity, protected/adaptive knowledge integrity, no-leakage protocol integrity, và **feature leakage check** (xác nhận lại lần cuối rằng 5 cột chế độ lỗi TWF/HDF/PWF/OSF/RNF không được dùng làm input, nhất quán với quyết định Phase 1).

**Cell 8.16 — Final Scientific Audit:** đây là cell quan trọng nhất về mặt liêm chính khoa học của toàn dự án, được giữ nguyên văn bên dưới vì nó chính là "rào chắn chống overclaim" mà dự án tự đặt ra cho mình:

```text
=== SCIENTIFIC INTERPRETATION FLAGS ===
1. Controlled sensor distribution shift:
   PASS — demonstrated by construction.
2. Concept drift P(Y|X):
   NOT DIRECTLY ESTABLISHED — do not overclaim.
3. Autonomous adaptation:
   NOT FULLY ESTABLISHED — adaptation uses a buffer-based heuristic.
4. Threshold:
   FROZEN — validation-selected τ=0.67; no Test retuning.
5. Evolving evaluation:
   PREQUENTIAL — Static before adaptation, Evolving after adaptation.
6. Main observed trade-off:
   FPR decreases while Recall/FNR changes after adaptation.
```

Ba dòng đầu tiên là ba giới hạn diễn giải **bắt buộc phải giữ nguyên trong báo cáo bảo vệ**, không được lược bỏ khi viết tóm tắt hay làm slide:
- Cái đã chứng minh: dịch chuyển phân phối cảm biến có kiểm soát (covariate shift do chính tay tiêm vào), lan truyền được vào điểm số mờ, và bị phát hiện bởi ADWIN.
- Cái **chưa** chứng minh: rằng đây là "concept drift" theo đúng nghĩa lý thuyết ($P(Y|X)$ thay đổi) — nhãn gốc không hề bị đổi, chỉ có input bị dịch. Nếu trong báo cáo/slide dùng cụm "concept drift" thì phải chú thích rõ đây là cách dùng theo nghĩa kỹ thuật vận hành, không phải khẳng định thống kê chặt.
- Cái **chưa** chứng minh: rằng cơ chế thích ứng là "học máy tự trị" — nó là một heuristic dịch chuyển tâm cụm dựa trên trung bình cộng của buffer, không phải một thuật toán học online (online learning) theo nghĩa tối ưu hóa hàm mất mát.

---

## 4. Thảo Luận, Giới Hạn Còn Tồn Đọng và Khuyến Nghị (Tránh Overclaim)

### 4.1. Ma trận thực nghiệm chưa đầy đủ — thiếu E2 (Control × Evolving Fuzzy)

Theo đúng định hướng đề ra ở cuối Phase 7 ("So sánh Static Baseline vs. Evolving Fuzzy... trên cả 3 kịch bản stream"), ma trận thực nghiệm đầy đủ cần **3 kịch bản × 2 mô hình = 6 tổ hợp**. Bảng ở mục 3.1 hiện chỉ có **5/6 tổ hợp** — thiếu **Control + Evolving Fuzzy**.

Đây không phải chi tiết phụ: mục tiêu khoa học cốt lõi mà chính đề tài đặt ra ngay từ đầu là chứng minh *"khi không có drift, Static và Evolving có performance tương đương"* (đối chứng bắt buộc để loại trừ khả năng cơ chế thích ứng gây hại một cách âm thầm khi môi trường thực ra không đổi). Thiếu tổ hợp này, báo cáo **chưa có quyền phát biểu** câu đó — dù trực giác kỹ thuật cho thấy nhiều khả năng nó đúng (vì ADWIN không kích hoạt trên Control nên Evolving sẽ trùng Static suốt 2.000 mẫu), **đây vẫn là một khẳng định cần số liệu, không phải suy diễn**.

**Khuyến nghị:** chạy pipeline Evolving Fuzzy trên `control_stream` (kỳ vọng hợp lý: vì ADWIN không phát hiện drift nào trên Control ở Phase 5, hệ Evolving sẽ không kích hoạt thích ứng và cho kết quả **trùng tuyệt đối** với Static Control) — nhưng đây vẫn cần được chạy và ghi lại bằng số, không được viết vào báo cáo như một điều "hiển nhiên".

### 4.2. Metrics độ phức tạp (complexity metrics) chưa được đo

Roadmap gốc của đề tài liệt kê "Number of fuzzy rules" và "Inference latency" là các metric bắt buộc (Phase 9 trong lộ trình ban đầu). Notebook 8 xác nhận số luật không đổi (12 luật, cố định — thể hiện ở Cell 8.10: `Rules: 12`), nhưng **chưa có phép đo thời gian suy luận (latency) thực tế** bằng đồng hồ (ví dụ `time.perf_counter()` trên N lần lặp). Nếu báo cáo muốn khẳng định hệ thống "phù hợp vận hành thời gian thực", cần ít nhất một con số latency đo được, hiện tại claim này chưa có bằng chứng định lượng đi kèm.

### 4.3. Reproducibility — khoảng trống giữa `requirements.txt` và môi trường thực tế đã dùng

`requirements.txt` hiện chỉ liệt kê `pandas, numpy, matplotlib, seaborn, jupyter, scikit-fuzzy`. Theo doc Phase 5, ADWIN được chạy trong một **conda env riêng** (`drift_env`, Python 3.11, có thêm `river==0.26.1`) do xung đột với chính sách bảo mật Windows trên môi trường gốc. Notebook 8 (`08_final_evaluation.ipynb`) tự dựng lại toàn bộ pipeline bao gồm cả phần liên quan ADWIN — nếu nó chạy được trong cùng một kernel duy nhất mà không cần `drift_env`, cần cập nhật `requirements.txt` cho khớp (thêm `river` nếu vẫn dùng, hoặc ghi rõ trong docs nếu Phase 8 đã thay ADWIN bằng cài đặt khác). Nếu không cập nhật, một người khác `pip install -r requirements.txt` rồi chạy `08_final_evaluation.ipynb` có khả năng gặp lỗi thiếu thư viện — ảnh hưởng tới tiêu chí "khả tái lập" mà chính dự án đề cao.

### 4.4. Trạng thái Git — Phase 8 chưa được đóng băng bằng commit

Các Phase 1–7 mỗi phase đều có một commit `feat(...)` riêng trên nhánh `main`. Tại thời điểm viết mục này, `08_final_evaluation.ipynb` và tài liệu Phase 8 vẫn là untracked file.

> [!NOTE]
> **Đính chính:** bản trước của mục này nói "nhiều file cũ đang ở trạng thái modified". Kiểm tra lại cho thấy đó chỉ là khác biệt line-ending (CRLF trên Windows so với LF) khi đọc repo từ một môi trường Git không bật `core.autocrlf`. Với `git -c core.autocrlf=true status` và `git diff --ignore-cr-at-eol`, **không có thay đổi nội dung nào** ở các file Phase 1–7. Không cần commit các file đó.

**Khuyến nghị (đã thực hiện):** commit Phase 8 thành một commit riêng theo đúng convention của các phase trước.

### 4.5. Không có Dashboard / Explainability (đúng như đã xếp vào Should-have/Bonus)

Notebook 8 dừng ở việc tổng hợp số liệu và biểu đồ tĩnh (matplotlib), chưa có: (a) màn hình explainability hiển thị rule nào được kích hoạt cho một mẫu cụ thể, (b) dashboard tương tác. Theo đúng phân loại Must/Should/Bonus mà đề tài tự đặt ra, đây là các hạng mục **Should-have/Bonus**, không chặn việc coi Phase 8 (must-have) là hoàn thành về mặt thực nghiệm cốt lõi.

---

## 5. Kết Luận Phase 8 — Đánh Giá Mức Độ "Đóng"

**Đánh giá tổng thể: Phase 8 đã hoàn thành phần thực thi kỹ thuật (41 cell, 8.0 → 8.16, không lỗi runtime, mọi integrity check đều PASS), nhưng CHƯA đủ điều kiện để coi là "đóng băng" hoàn chỉnh** theo đúng tiêu chuẩn nghiêm ngặt mà chính dự án đặt ra ở các phase trước, vì còn 4 việc chưa xong:

1. Thiếu tổ hợp thực nghiệm E2 (Control + Evolving) — **quan trọng nhất, cần làm trước khi viết bất kỳ câu kết luận so sánh nào vào báo cáo cuối**.
2. Thiếu số đo latency/độ phức tạp định lượng.
3. `requirements.txt` chưa khớp với môi trường thực tế đã dùng để chạy ADWIN.
4. Chưa có commit git chính thức đóng gói Phase 8 (và các phase trước còn diff line-ending chưa dọn).

Phần lõi khoa học — pipeline tái tạo độc lập, đối chiếu sai số với Phase 7 ($<5\times10^{-7}$), và đặc biệt là cơ chế tự-audit chống overclaim (Cell 8.16) — được thực hiện ở mức nghiêm túc hiếm thấy ở một đồ án cấp thạc sĩ, và **không cần sửa gì thêm**. Việc còn lại là các khoảng trống có thể lấp trong thời gian ngắn (ước lượng: E2 + latency + commit ≈ dưới 1 buổi làm việc), không phải làm lại từ đầu.

Sau khi hoàn tất 4 mục trên, Phase 8 mới nên được tuyên bố "đóng băng" và làm nền để viết chương Kết quả của báo cáo luận văn cuối cùng.
