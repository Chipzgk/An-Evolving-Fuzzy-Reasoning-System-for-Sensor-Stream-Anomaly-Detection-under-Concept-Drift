# Phase 2.1 — Xác định Mục tiêu Suy luận Mờ (Fuzzy Reasoning Target)

## 1. Mục tiêu

Phase 2.1 đóng vai trò là cột mốc kiến trúc nền tảng của hệ suy luận mờ tĩnh (Static Fuzzy Inference System - FIS). Mục tiêu của phase này là:
1. **Xác định bản chất đầu ra (Output Target)** của hệ mờ: Không ép hệ mờ phân loại nhị phân cứng (*Normal / Anomaly*), mà thiết kế để sinh ra một chỉ số bất thường liên tục (**Anomaly Score** $A(x) \in [0, 1]$).
2. **Lựa chọn mô hình suy luận mờ**: Lựa chọn hệ suy luận mờ **Mamdani (Mamdani FIS)** vì tính trực quan, cấu trúc luật ngôn ngữ $IF-THEN$ minh bạch và khả năng diễn giải chuyên sâu (explainability).
3. **Phân định ranh giới toán học**: Làm rõ sự khác biệt bản chất giữa *Anomaly Score* (mức độ thỏa mãn tri thức mờ) và *Xác suất* (Probability), bảo đảm tính chuẩn xác khi báo cáo học thuật.
4. **Chuẩn hóa quy trình phân tách dữ liệu & lựa chọn ngưỡng ($\tau$)**: Thiết lập quy tắc chọn ngưỡng $\tau$ độc quyền trên tập Validation, đóng băng trước khi kiểm thử trên tập Test, kiên quyết chống rò rỉ dữ liệu (data leakage).

---

## 2. Xác nhận tính tương thích với đề tài nghiên cứu

Thiết kế kiến trúc luồng:
$$\mathbf{x} = [x_1, x_2, x_3, x_4, x_5]^T \xrightarrow{\quad\text{Mamdani FIS}\quad} A(\mathbf{x}) \in [0, 1] \xrightarrow{\quad\text{Ngưỡng }\tau\quad} \hat{y} \in \{0, 1\}$$

hoàn toàn tương thích và là sự lựa chọn tối ưu cho đề tài **"An Evolving Fuzzy Reasoning System for Sensor Stream Anomaly Detection under Concept Drift"** vì các lý do cốt lõi sau:

1. **Phù hợp với đặc thù dữ liệu cảm biến công nghiệp:**
   Dữ liệu cảm biến vật lý (nhiệt độ, tốc độ, mô-men, độ mòn) biến thiên liên tục trong không gian thực. Các trạng thái thoái hóa máy móc (degradation) không diễn ra tức thời từ "tốt" sang "hỏng" mà là quá trình tiệm tiến. Một chỉ số liên tục $A(x) \in [0, 1]$ phản ánh chính xác quá trình suy hao này.
2. **Khả năng giải thích (Interpretability & Explainability) vượt trội:**
   Hệ Mamdani sử dụng các tập mờ ngôn ngữ ở cả phần tiền đề (antecedent) lẫn phần hệ quả (consequent). Khi phát hiện bất thường, hệ thống có thể xuất ra chính xác tập luật nào đang kích hoạt (firing strength $\alpha_k$) và đóng góp bao nhiêu vào chỉ số bất thường, đáp ứng trọn vẹn tiêu chí của một "Hệ thống thông minh" (Intelligent System).
3. **Bản lề vững chắc cho Evolving & Concept Drift (Phase 3, 4, 5):**
   Trong môi trường dữ liệu luồng (stream), sự dịch chuyển phân bố (drift) thường biểu hiện trước tiên qua sự biến động của phân bố Anomaly Score trước khi lỗi thực sự xảy ra. Việc sở hữu giá trị Anomaly Score liên tục cho phép áp dụng các thuật toán dò tìm drift (như ADWIN, Page-Hinkley, CUSUM) lên luồng điểm số hoặc luồng lỗi dự đoán một cách hiệu quả.

---

## 3. Bản chất toán học của Anomaly Score $A(x)$

### 3.1. Định nghĩa hình thức

Cho vector đầu vào gồm 5 tín hiệu cảm biến tại một thời điểm:
$$\mathbf{x} = [x_{\text{air}}, x_{\text{proc}}, x_{\text{rpm}}, x_{\text{torque}}, x_{\text{wear}}]^T \in \mathbb{R}^5$$

Hệ suy luận mờ đóng vai trò là một ánh xạ phi tuyến:
$$f_{\text{FIS}}: \mathbb{R}^5 \to [0, 1]$$
$$A(\mathbf{x}) = f_{\text{FIS}}(\mathbf{x})$$

Trong đó:
- $A(\mathbf{x}) \to 0$: Trạng thái cảm biến hoàn toàn bình thường, phù hợp với các mẫu vận hành lý tưởng.
- $A(\mathbf{x}) \to 1$: Trạng thái cảm biến có mức độ bất thường cực đại, kích hoạt các luật cảnh báo hỏng hóc hoặc vận hành khắc nghiệt.

Phân loại nhị phân cuối cùng được xác định thông qua hàm bước nhảy theo ngưỡng $\tau \in [0, 1]$:
$$\hat{y} = \mathbb{I}(A(\mathbf{x}) \ge \tau) = \begin{cases} 1 & \text{nếu } A(\mathbf{x}) \ge \tau \quad (\text{Bất thường / Anomaly}) \\ 0 & \text{nếu } A(\mathbf{x}) < \tau \quad (\text{Bình thường / Normal}) \end{cases}$$

---

### 3.2. Phân biệt triệt để giữa Anomaly Score và Xác suất (Probability)

> [!IMPORTANT]
> **Tuyệt đối không đồng nhất Anomaly Score với xác suất máy hỏng ($P(\text{Machine failure} = 1 \mid \mathbf{x})$).**

| Tiêu chí | Anomaly Score $A(\mathbf{x})$ (Fuzzy Degree of Anomaly) | Xác suất $P(\text{Failure} \mid \mathbf{x})$ (Probability) |
| :--- | :--- | :--- |
| **Nền tảng lý thuyết** | Lý thuyết Tập mờ (Fuzzy Set Theory - Lotfi Zadeh, 1965). | Tiên đề Xác suất (Kolmogorov Axioms, 1933). |
| **Ý nghĩa bản chất** | Đo lường **mức độ tương đồng / mức độ thỏa mãn** của trạng thái cảm biến hiện tại đối với khái niệm "bất thường" được định nghĩa trong cơ sở tri thức mờ. | Đo lường **tần suất xuất hiện khả dĩ** của sự kiện hỏng hóc trong vô hạn phép thử lặp lại. |
| **Tính cộng tính** | Không bắt buộc tuân theo quy tắc cộng tính: $A(\text{Normal}) + A(\text{Anomaly}) \neq 1$. | Bắt buộc tuân theo tiên đề cộng tính: $P(\text{Normal}) + P(\text{Failure}) = 1$. |
| **Ví dụ diễn giải** | $A(\mathbf{x}) = 0.82 \implies$ Trạng thái vận hành hiện tại mang tính chất bất thường ở mức độ 0,82 dựa trên các luật mờ được thiết kế. | $P = 0.82 \implies$ Có 82% cơ hội máy sẽ gặp sự cố hỏng hóc thực sự. |

**Ý nghĩa học thuật:**
Một máy móc có thể vận hành trong vùng rủi ro rất cao (Torque quá lớn, Tool Wear mòn nặng $\to A(\mathbf{x}) = 0.90$), nhưng tại đúng mẫu quan sát đó máy chưa sụp đổ hoàn toàn (`Machine failure = 0`). Việc ghi nhận $A(\mathbf{x}) = 0.90$ là hoàn toàn chính xác về mặt kỹ thuật cảnh báo sớm, không thể coi là mô hình đoán sai xác suất.

---

## 4. Vì sao Anomaly Score liên tục vượt trội hơn đầu ra nhị phân cứng?

1. **Bảo tồn thông tin cảnh báo đa mức (Multi-level Warning):**
   - Mẫu $A$: $\text{Torque} = \text{HIGH}, \text{ToolWear} = \text{HIGH} \implies A(\mathbf{x}) = 0.68$ (Mức cảnh báo chú ý - Warning).
   - Mẫu $B$: $\text{Torque} = \text{VERY HIGH}, \text{ToolWear} = \text{VERY HIGH}, \text{Temp} = \text{HIGH} \implies A(\mathbf{x}) = 0.94$ (Mức nguy cấp - Critical Emergency).
   Nếu hệ mờ trả thẳng 0 hoặc 1, cả hai trường hợp đều chỉ là `1 (Anomaly)`, đánh mất toàn bộ thông tin về mức độ nghiêm trọng.
2. **Hỗ trợ giao diện giám sát công nghiệp (SCADA / Dashboard Demo):**
   - Hiển thị trực quan thanh trạng thái (Gauge/Progress bar) từ xanh lá ($0.0 - 0.3$) sang vàng ($0.3 - 0.7$) và đỏ ($0.7 - 1.0$).
3. **Phục vụ giải thích chi tiết (Explainable AI - XAI):**
   - Cho phép phân rã:
     $$\text{Air Temp} = \text{HIGH} \quad (\mu = 0.82)$$
     $$\text{Torque} = \text{VERY HIGH} \quad (\mu = 0.75)$$
     $$\implies \text{Kích hoạt Luật } R_5 \text{ với trọng số } \alpha_5 = 0.75 \implies \text{Đóng góp chính vào } A(\mathbf{x}) = 0.85$$

---

## 5. Cấu trúc 5 Tín hiệu Cảm biến đầu vào (Inputs)

Theo kết quả khảo sát từ Phase 1 và quy tắc chống rò rỉ dữ liệu (Anti-Leakage), 5 biến đầu vào được chốt chính thức như sau:

| STT | Tên biến cảm biến | Ký hiệu kỹ thuật | Đơn vị | Ý nghĩa vật lý trong giám sát |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `Air temperature [K]` | $T_{\text{air}}$ | Kelvin (K) | Nhiệt độ môi trường xung quanh máy |
| 2 | `Process temperature [K]` | $T_{\text{proc}}$ | Kelvin (K) | Nhiệt độ sản sinh trong quá trình gia công |
| 3 | `Rotational speed [rpm]` | $\omega$ | Vòng/phút | Tốc độ quay của trục chính (spindle speed) |
| 4 | `Torque [Nm]` | $M$ | Newton-mét (Nm) | Mô-men xoắn cản trở trục máy |
| 5 | `Tool wear [min]` | $t_{\text{wear}}$ | Phút (min) | Thời gian dao cắt đã làm việc mòn tích lũy |

### Danh sách các trường TUYỆT ĐỐI KHÔNG làm đầu vào:
- **`Machine failure`**: Nhãn mục tiêu (Ground truth), chỉ dùng cho giai đoạn đánh giá (Evaluation).
- **`TWF` (Tool Wear Failure)**: Chế độ hỏng hóc do mòn dao.
- **`HDF` (Heat Dissipation Failure)**: Chế độ hỏng hóc do tản nhiệt kém.
- **`PWF` (Power Failure)**: Chế độ hỏng hóc do mất cân bằng công suất.
- **`OSF` (Overstrain Failure)**: Chế độ hỏng hóc do quá tải cơ học.
- **`RNF` (Random Failure)**: Chế độ hỏng hóc ngẫu nhiên.
- **`UDI`, `Product ID`, `Type`**: Các trường định danh và phân loại tĩnh, không phải chuỗi thời gian cảm biến vật lý trực tiếp.

---

## 6. Kiến trúc Mamdani Fuzzy Inference System (Static FIS)

Sơ đồ khối tổng thể của hệ mờ tĩnh trong Phase 2:

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                         5 TÍN HIỆU CẢM BIẾN ĐẦU VÀO                         │
 │     T_air [K]     T_proc [K]      RPM [rpm]      Torque [Nm]     Wear [min] │
 └─────────┬──────────────┬──────────────┬──────────────┬───────────────┬──────┘
           │              │              │              │               │
 ┌─────────▼──────────────▼──────────────▼──────────────▼───────────────▼──────┐
 │ 1. MỜ HÓA (FUZZIFICATION)                                                   │
 │    Ánh xạ giá trị số thực x_i sang độ thuộc μ_A(x_i) qua Membership Funcs   │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
 ┌──────────────────────────────────────▼──────────────────────────────────────┐
 │ 2. CƠ SỞ TRI THỨC VÀ SUY LUẬN (FUZZY RULE BASE & INFERENCE)                 │
 │    - Tập luật: IF <Tiền đề cảm biến> THEN Anomaly is <LOW / MED / HIGH>     │
 │    - T-norm (AND): Min operator: α_k = min(μ_1, μ_2, ...)                   │
 │    - Suy luận hệ quả (Implication): Mamdani Min: μ_k(y) = min(α_k, μ_out(y))│
 │    - Tích lũy luật (Aggregation): Max operator: μ_agg(y) = max_k(μ_k(y))    │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
 ┌──────────────────────────────────────▼──────────────────────────────────────┐
 │ 3. KHỬ MỜ (DEFUZZIFICATION)                                                 │
 │    Tính trọng tâm (Centroid / Center of Gravity - COG):                      │
 │    A(x) = ∫ y · μ_agg(y) dy / ∫ μ_agg(y) dy                                 │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
                                        ▼
                        ANOMALY SCORE: A(x) ∈ [0.0, 1.0]
                                        │
                                ┌───────┴───────┐
                                │   Ngưỡng τ    │ (Tinh chỉnh trên Validation)
                                └───────┬───────┘
                                        │
                                ┌───────┴───────┐
                                ▼               ▼
                             Normal          Anomaly
                           (y_hat = 0)     (y_hat = 1)
```

### Chi tiết các thành phần toán học:
1. **Biến ngôn ngữ đầu ra `Anomaly`:**
   - Miền vũ luận (Universe of Discourse): $U = [0, 1]$.
   - Các giá trị ngôn ngữ (Linguistic Terms):
     - `LOW` (Thấp): Đại diện cho trạng thái an toàn, bình thường (tiệm cận 0.0).
     - `MEDIUM` (Trung bình): Đại diện cho trạng thái chớm bất thường, cảnh báo (vùng quanh 0.5).
     - `HIGH` (Cao): Đại diện cho trạng thái nguy cấp, hỏng hóc cao (tiệm cận 1.0).
2. **Cơ chế suy luận Mamdani:**
   - **T-norm (Intersection / AND):** Chuẩn tối thiểu (Zadeh Min):
     $$\alpha_k = \min_{j} \left(\mu_{A_{kj}}(x_j)\right)$$
   - **Implication (Cắt ngọn hệ quả):** Mamdani Min operator:
     $$\mu_{C_k'}(y) = \min\left(\alpha_k, \, \mu_{C_k}(y)\right)$$
   - **Aggregation (Hợp các luật):** Max operator:
     $$\mu_{\text{agg}}(y) = \max_{k=1}^K \left(\mu_{C_k'}(y)\right)$$
3. **Khử mờ (Defuzzification):**
   - Sử dụng phương pháp **Trọng tâm (Centroid / Center of Gravity - COG)**:
     $$A(\mathbf{x}) = \frac{\int_0^1 y \cdot \mu_{\text{agg}}(y) \, dy}{\int_0^1 \mu_{\text{agg}}(y) \, dy}$$
   - *Lý do chọn COG:* Đảm bảo tính liên tục, trơn và phản ứng nhạy với sự thay đổi nhỏ của tín hiệu cảm biến (tránh hiện tượng nhảy bậc đột ngột như phương pháp cực đại Mean of Maxima - MOM).

---

## 7. Quy trình Phân tách Dữ liệu & Cơ chế Chọn Ngưỡng $\tau$

### 7.1. Nguyên tắc: Không chọn trước $\tau = 0.5$ tại Phase 2.1
Việc gán cứng $\tau = 0.5$ tại thời điểm này là hoàn toàn thiếu cơ sở khoa học, bởi vì:
1. **Lệch lớp nghiêm trọng (Severe Class Imbalance):**
   Tỷ lệ nhãn `Machine failure = 1` trong dataset chỉ chiếm **3,39%** (toàn bộ) và **4,25%** (tập Train). Một ngưỡng cố định 0.5 thường sẽ dẫn đến hoặc bỏ sót rất nhiều bất thường (Recall thấp) hoặc báo động giả quá mức nếu hàm thuộc chưa cân đối.
2. **Chi phí sai số không đối xứng trong công nghiệp:**
   Trong bảo trì dự đoán, việc bỏ sót một máy sắp hỏng (False Negative - máy dừng đột ngột gây thiệt hại dây chuyền) có chi phí tổn thất đắt hơn gấp hàng chục lần so với việc kiểm tra nhầm một máy bình thường (False Positive).

---

### 7.2. Giao thức tương tác giữa 3 phân vùng (Train / Validation / Test)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. TẬP TRAIN (6,000 mẫu đầu: UDI 1 -> 6,000)                                │
│    - Khảo sát phân bố thống kê (Min, Max, Mean, Std, Phân vị).              │
│    - Thiết kế hình dáng và thông số các hàm thuộc tính (MFs).               │
│    - Xây dựng cơ sở tri thức tập luật mờ (Fuzzy Rule Base).                 │
│    => Hoàn tất đóng gói STATIC FUZZY SYSTEM.                                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. TẬP VALIDATION (2,000 mẫu tiếp theo: UDI 6,001 -> 8,000)                 │
│    - Đưa dữ liệu qua Static FIS để sinh chuỗi Anomaly Scores A(x).          │
│    - Quét ngưỡng ứng viên τ ∈ [0.01, 0.99].                                 │
│    - Đánh giá Precision, Recall, F1-score, PR-AUC.                          │
│    - Lựa chọn ngưỡng tối ưu τ* (ví dụ tối đa hóa F1 hoặc F2-score).         │
│    => ĐÓNG BĂNG NGƯỠNG TỐI ƯU τ*.                                           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. TẬP TEST (2,000 mẫu cuối: UDI 8,001 -> 10,000)                           │
│    - Tập dữ liệu hoàn toàn chưa từng biết (Unseen Test Stream).              │
│    - Áp dụng Static FIS + Ngưỡng đóng băng τ*.                              │
│    - Đánh giá song song trên 3 kịch bản: No Drift, Sudden Drift, Gradual.   │
│    - Benchmark công bằng đối đầu với Evolving Fuzzy System.                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

> [!NOTE]
> Giao thức này bảo đảm tính khách quan tuyệt đối (zero data-snooping), bảo vệ nghiên cứu trước mọi nghi ngại về rò rỉ dữ liệu kiểm thử.

---

## 8. Lợi ích mở rộng đối với Cơ chế Evolving và Concept Drift (Phases 3, 4, 5)

Việc xuất ra chỉ số liên tục $A(\mathbf{x}) \in [0, 1]$ thay vì nhãn rời rạc $0/1$ tạo ra tiền đề sống còn cho bài toán Concept Drift:

1. **Giám sát trôi dạt phân bố điểm số (Anomaly Score Distribution Shift):**
   Khi có Concept Drift (ví dụ mòn dao nhanh hơn do thay đổi vật liệu phôi, hoặc nhiệt độ môi trường tăng vọt theo mùa), phân bố của $A(\mathbf{x})$ trên cửa sổ trượt (sliding window) sẽ có sự dịch chuyển kỳ vọng $E[A(\mathbf{x})]$. Nhờ đó, bộ dò trôi dạt (ADWIN / CUSUM) có thể kích hoạt tín hiệu drift sớm.
2. **Cơ chế tự thích nghi mờ (Evolving Fuzzy Rules Adaptation):**
   - Nếu $A(\mathbf{x})$ liên tục cao trên một cụm dữ liệu mới nhưng không gây hỏng hóc máy (Virtual Drift do tải vận hành mới), hệ Evolving sẽ nhận diện nhu cầu điều chỉnh lại trọng tâm (center) hoặc độ rộng (width) của các hàm thuộc tính.
   - Nếu xuất hiện một dạng bất thường hoàn toàn mới ngoài tầm bao phủ của các luật mờ ban đầu, hệ thống có thể bổ sung luật mờ mới (Rule Generation).

---

## 9. Tóm tắt Checkpoint Phase 2.1

| Hạng mục | Quyết định kỹ thuật |
| :--- | :--- |
| **Đầu vào (Inputs)** | 5 biến cảm biến: $T_{\text{air}}$, $T_{\text{proc}}$, $\text{RPM}$, $\text{Torque}$, $\text{Tool wear}$. |
| **Loại hệ mờ** | **Mamdani Fuzzy Inference System** (trực quan, dễ giải thích, minh bạch luật). |
| **Đầu ra mờ (Fuzzy Output)** | Biến ngôn ngữ `Anomaly` với các mức `LOW`, `MEDIUM`, `HIGH`. |
| **Chỉ số bất thường** | $A(\mathbf{x}) \in [0, 1]$ thu được qua khử mờ trọng tâm (Centroid Defuzzification). |
| **Bản chất toán học** | Mức độ thỏa mãn khái niệm bất thường trong không gian mờ (Degree of Anomaly), **không phải xác suất**. |
| **Ngưỡng quyết định ($\tau$)** | Chưa chọn ở Phase 2.1; sẽ được tinh chỉnh tối ưu trên tập **Validation** và đóng băng cho tập **Test**. |
| **Phân tách Ground truth** | Nhãn `Machine failure` và 5 nhãn chế độ lỗi tuyệt đối không dùng làm đầu vào, chỉ dùng để đánh giá. |

---

## 10. Kế hoạch chuyển tiếp sang Phase 2.2

Sau khi thống nhất trọn vẹn kiến trúc mục tiêu tại Phase 2.1, bước tiếp theo sẽ là **Phase 2.2 — Thiết kế không gian mờ hóa và hàm thuộc tính (Fuzzification & Membership Functions)**:
1. Trích xuất thống kê mô tả (Min, Max, Med, Q1, Q3, $3\sigma$) trên 6.000 mẫu tập Train.
2. Xác định số lượng tập mờ cho từng biến đầu vào (ví dụ: `LOW`, `NORMAL`, `HIGH` hoặc `LOW`, `MEDIUM`, `HIGH`).
3. Lựa chọn dạng hình học của hàm thuộc tính (Tam giác - Triangular, Hình thang - Trapezoidal, hoặc Gaussian) để bảo đảm vừa phản ánh đúng vật lý, vừa tối ưu tốc độ tính toán cho môi trường stream.
