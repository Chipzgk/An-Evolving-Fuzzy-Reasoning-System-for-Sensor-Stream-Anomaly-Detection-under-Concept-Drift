# Phase 2.4 & 2.5 — Thiết kế Fuzzy Rule Base và Triển khai Động cơ Suy diễn Mờ Mamdani

## 1. Mục tiêu

Tài liệu này ghi nhận quá trình thực hiện và kết quả của hai giai đoạn cốt lõi trong việc xây dựng hệ cơ sở mờ tĩnh (**Static Fuzzy Baseline**):
1. **Phase 2.4 — Thiết kế Fuzzy Rule Base:** Khảo sát các mẫu hình (patterns) bất thường trong tập Train (6.000 mẫu đầu), phân tích mối liên hệ có điều kiện (conditional associations) theo từng biến đơn lẻ, cặp biến và bộ ba biến để xây dựng một tập luật mờ gồm 12 luật compact, có khả năng giải thích cao, thay vì sử dụng toàn bộ $3^5 = 243$ tổ hợp khả dĩ.
2. **Phase 2.5 — Triển khai Động cơ Suy diễn Mờ Mamdani (FIS Engine):** Xây dựng module tính toán mức thuộc liên tục theo giải tích (analytical continuous fuzzification), áp dụng cơ chế suy diễn Mamdani (AND = min, Implication = min, Aggregation = max, Defuzzification = centroid) và kiểm tra tính nhất quán của phép suy diễn trên các mẫu dữ liệu đại diện.

> [!IMPORTANT]
> **Nguyên tắc phương pháp luận:**
> - Toàn bộ việc thiết kế tập luật chỉ dựa trên tập dữ liệu huấn luyện (Train set: 6.000 mẫu đầu). Không sử dụng tập Validation hay Test trong quá trình xây dựng luật.
> - Tuyệt đối không sử dụng các nhãn chế độ lỗi cụ thể (TWF, HDF, PWF, OSF, RNF) làm thuộc tính đầu vào nhằm đảm bảo tính tổng quát và ngăn ngừa rò rỉ tri thức (Anti-Leakage).
> - Nhãn kết luận của các luật mờ được gán dựa trên mức độ mạnh yếu tương đối của mối liên hệ với failure trong tập Train (*"The rule consequents were assigned according to the relative strength of the observed failure associations in the training set"*), không phải khẳng định mối quan hệ nhân quả vật lý tuyệt đối.

---

## 2. Hàm thuộc tính của Biến đầu ra Anomaly Score

Biến đầu ra của hệ thống là `Anomaly Score` $y \in [0, 1]$, thể hiện mức độ nghi ngờ bất thường của trạng thái vận hành.

### 2.1. Cấu trúc hình học (Cell 2.4.1)

Miền giá trị rời rạc $y \in [0, 1]$ được tạo với 1.000 điểm lưới để phục vụ giải mờ (defuzzification):

```python
anomaly = universes["anomaly"]  # np.linspace(0, 1, 1000)

anomaly_low    = fuzz.trapmf(anomaly, [0.0, 0.0, 0.25, 0.50])
anomaly_medium = fuzz.trimf( anomaly, [0.25, 0.50, 0.75])
anomaly_high   = fuzz.trapmf(anomaly, [0.50, 0.75, 1.0, 1.0])
```

| Tập mờ | Dạng MF | Tham số hình học | Ngữ nghĩa |
| :--- | :---: | :---: | :--- |
| **LOW** | Hình thang (vai trái) | $[0.0, 0.0, 0.25, 0.50]$ | Vùng vận hành an toàn/danh định |
| **MEDIUM** | Tam giác | $[0.25, 0.50, 0.75]$ | Vùng cảnh báo, tín hiệu bất thường trung gian |
| **HIGH** | Hình thang (vai phải) | $[0.50, 0.75, 1.0, 1.0]$ | Vùng bất thường cao, nguy cơ hỏng hóc lớn |

### 2.2. Kiểm tra phân hoạch hình học

- $\min\sum\mu = 1.0$, $\max\sum\mu = 1.0$, độ lệch cực đại so với 1: $0.0$.
- Điểm chuyển tiếp (crossover points) tại $y = 0.375$ ($\mu_{LOW} = \mu_{MEDIUM} = 0.5$) và $y = 0.625$ ($\mu_{MEDIUM} = \mu_{HIGH} = 0.5$).
- Cấu trúc đối xứng và mượt mà trên toàn miền $[0, 1]$.

---

## 3. Quá trình Khám phá và Kiểm chứng Bằng chứng Dữ liệu (Train Set)

Tập huấn luyện Train gồm 6.000 mẫu, trong đó có **255 mẫu Failure** ($4.25\%$) và **5.745 mẫu Normal** ($95.75\%$). Tỷ lệ mất cân bằng giữa hai lớp xấp xỉ $1:22.5$.

### 3.1. Phân tích mối liên hệ có điều kiện theo từng Term đơn lẻ (Cell 2.4.4)

Khảo sát tỷ lệ failure khi từng term được kích hoạt ưu thế (dominant term):

| Cảm biến | Linguistic Term | Hỗ trợ (Support) | Số mẫu lỗi (Fail Count) | Failure Rate (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Torque [Nm]** | **HIGH** | **1378** | **183** | **13.28%** |
| Torque [Nm] | LOW | 1354 | 32 | 2.36% |
| Torque [Nm] | MEDIUM | 3268 | 40 | 1.22% |
| **Rotational speed [rpm]** | **LOW** | **1560** | **198** | **12.69%** |
| Rotational speed [rpm] | HIGH | 826 | 28 | 3.39% |
| Rotational speed [rpm] | MEDIUM | 3614 | 29 | 0.80% |
| **Air temperature [K]** | **HIGH** | **2439** | **171** | **7.01%** |
| Air temperature [K] | LOW | 2213 | 56 | 2.53% |
| Air temperature [K] | MEDIUM | 1348 | 28 | 2.08% |
| **Tool wear [min]** | **HIGH** | **2243** | **134** | **5.97%** |
| Tool wear [min] | MEDIUM | 1501 | 50 | 3.33% |
| Tool wear [min] | LOW | 2256 | 71 | 3.15% |
| **Process temperature [K]** | **HIGH** | **2227** | **119** | **5.34%** |
| Process temperature [K] | MEDIUM | 2011 | 86 | 4.28% |
| Process temperature [K] | LOW | 1762 | 50 | 2.84% |

**Nhận xét:**
- `Torque = HIGH` ($13.28\%$) và `RPM = LOW` ($12.69\%$) thể hiện mức tương phản tỷ lệ lỗi mạnh nhất so với term `MEDIUM` của chính chúng (gấp từ 10 đến 15 lần). Đây là hai điều kiện tiên quyết hàng đầu trong việc phát hiện bất thường.
- `Air Temp = HIGH` ($7.01\%$) và `Tool Wear = HIGH` ($5.97\%$) có tỷ lệ lỗi vượt mức nền ($4.25\%$), đóng vai trò là các biến khuếch đại hoặc bổ trợ quan trọng.

### 3.2. Phân tích tương quan cặp điều kiện (Cell 2.4.5)

Khảo sát khi hai điều kiện mạnh xuất hiện đồng thời:

| Điều kiện kết hợp (2 biến) | Support | Fail Count | Failure Rate (%) |
| :--- | :---: | :---: | :---: |
| `RPM=LOW` AND `Air Temp=HIGH` | 641 | 144 | **22.46%** |
| `Torque=HIGH` AND `Air Temp=HIGH` | 557 | 125 | **22.44%** |
| `Torque=HIGH` AND `Tool Wear=HIGH` | 526 | 93 | **17.68%** |
| `Torque=HIGH` AND `Process Temp=HIGH` | 496 | 86 | **17.34%** |
| `RPM=LOW` AND `Process Temp=HIGH` | 570 | 97 | **17.02%** |
| `RPM=LOW` AND `Tool Wear=HIGH` | 597 | 99 | **16.58%** |
| `RPM=LOW` AND `Torque=HIGH` | 1065 | 173 | **16.24%** |

**Nhận xét:**
- `Air Temp = HIGH` thể hiện vai trò khuếch đại rõ rệt: khi kết hợp cùng `RPM=LOW` hoặc `Torque=HIGH`, tỷ lệ lỗi tăng vọt lên xấp xỉ $22.5\%$.
- Cặp `RPM=LOW AND Torque=HIGH` có độ phủ rộng nhất ($1.065$ mẫu, tức $\approx 17.75\%$ tập Train) với tỷ lệ lỗi $16.24\%$, là ứng viên tiêu biểu cho mức cảnh báo trung gian (MEDIUM).

### 3.3. Phân tích tổ hợp ba biến (Cell 2.4.6)

Khi kết hợp 3 điều kiện đồng thời, tính chọn lọc phân biệt lỗi tăng mạnh:

| Điều kiện tổ hợp (3 biến) | Support | Support (%) | Fail Count | Failure Rate (%) | Lift (so với 4.25%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`RPM=LOW` AND `Torque=HIGH` AND `Air Temp=HIGH`** | **439** | **7.32%** | **121** | **27.56%** | **6.49×** |
| **`Torque=HIGH` AND `Air Temp=HIGH` AND `Tool Wear=HIGH`** | **205** | **3.42%** | **55** | **26.83%** | **6.31×** |
| **`RPM=LOW` AND `Torque=HIGH` AND `Process Temp=HIGH`** | **385** | **6.42%** | **81** | **21.04%** | **4.95×** |
| **`RPM=LOW` AND `Torque=HIGH` AND `Tool Wear=HIGH`** | **412** | **6.87%** | **86** | **20.87%** | **4.91×** |
| `Torque=HIGH` AND `Air Temp=HIGH` AND `Process Temp=HIGH` | 465 | 7.75% | 84 | 18.06% | 4.25× |

> [!NOTE]
> Tổ hợp `RPM=LOW AND Torque=HIGH AND Air Temp=HIGH` có 121 mẫu failure nằm trong vùng này (chiếm $47.5\%$ tổng số 255 mẫu failure của tập Train). Đây là độ bao phủ mẫu lỗi (coverage of failure samples) của pattern trong tập Train, chưa phải độ nhạy (Recall) của toàn bộ hệ FIS.

### 3.4. Khảo sát các vùng vận hành an toàn cho luật LOW Anomaly (Cell 2.4.7)

Để tránh hiện tượng hệ thống mặc định đẩy các trạng thái bình thường lên mức bất thường cao, cần các luật $LOW$ có cơ sở dữ liệu:

| Điều kiện kết hợp | Support | Support (%) | Fail Count | Failure Rate (%) | Lift (so với 4.25%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`RPM=MEDIUM` AND `Torque=MEDIUM`** | **2758** | **45.97%** | **15** | **0.54%** | **0.13×** |
| **`RPM=MEDIUM` AND `Torque=LOW`** | **543** | **9.05%** | **4** | **0.74%** | **0.17×** |
| **`RPM=HIGH` AND `Torque=LOW`** | **811** | **13.52%** | **28** | **3.45%** | **0.81×** |

- `RPM=MEDIUM AND Torque=MEDIUM` đại diện cho vùng vận hành danh định lớn nhất (chiếm gần $46\%$ tập Train) với tỷ lệ lỗi chỉ $0.54\%$ (thấp hơn baseline gần 8 lần).
- `RPM=HIGH AND Torque=LOW` thể hiện chế độ quay nhanh ở tải thấp, có tỷ lệ lỗi $3.45\%$, thấp hơn mức trung bình của tập dữ liệu.

---

## 4. Thiết kế Hệ Cơ sở Luật Mờ (12 Mamdani Rules)

Thay vì bùng nổ tổ hợp với $3^5 = 243$ luật, hệ thống sử dụng **12 luật mờ** được cấu trúc có chủ đích thành 3 tầng bằng chứng:

### 4.1. Nhóm 🔴 HIGH Anomaly (4 luật — Bằng chứng bất thường mạnh)
Các luật này bắt nguồn từ các tổ hợp 3 biến có Failure Rate từ $20.87\%$ đến $27.56\%$ và Lift từ $4.91\times$ đến $6.49\times$:
- **R1:** `IF RPM is LOW AND Torque is HIGH AND Air Temp is HIGH THEN Anomaly is HIGH`
- **R2:** `IF Torque is HIGH AND Air Temp is HIGH AND Tool Wear is HIGH THEN Anomaly is HIGH`
- **R3:** `IF RPM is LOW AND Torque is HIGH AND Process Temp is HIGH THEN Anomaly is HIGH`
- **R4:** `IF RPM is LOW AND Torque is HIGH AND Tool Wear is HIGH THEN Anomaly is HIGH`

### 4.2. Nhóm 🟡 MEDIUM Anomaly (5 luật — Bằng chứng bất thường trung gian)
Các luật bắt nguồn từ các cặp biến có tỷ lệ lỗi từ $16\%$ đến $22\%$, cung cấp tín hiệu cảnh báo sớm:
- **R5:** `IF RPM is LOW AND Torque is HIGH THEN Anomaly is MEDIUM`
- **R6:** `IF RPM is LOW AND Air Temp is HIGH THEN Anomaly is MEDIUM`
- **R7:** `IF Torque is HIGH AND Air Temp is HIGH THEN Anomaly is MEDIUM`
- **R8:** `IF Torque is HIGH AND Tool Wear is HIGH THEN Anomaly is MEDIUM`
- **R9:** `IF Torque is HIGH AND Process Temp is HIGH THEN Anomaly is MEDIUM`

### 4.3. Nhóm 🟢 LOW Anomaly (3 luật — Vùng vận hành danh định và ít lỗi)
Cung cấp lực kéo Anomaly Score về phía cận dưới khi máy vận hành trong các vùng bình thường:
- **R10:** `IF RPM is MEDIUM AND Torque is MEDIUM THEN Anomaly is LOW` *(vùng vận hành danh định chính)*
- **R11:** `IF RPM is MEDIUM AND Torque is LOW THEN Anomaly is LOW`
- **R12:** `IF RPM is HIGH AND Torque is LOW THEN Anomaly is LOW`

> [!TIP]
> **Cơ chế phân tầng bằng chứng (Evidence Hierarchy):**
> Ví dụ, nếu một mẫu có `RPM=LOW` và `Torque=HIGH`:
> - Luật `R5` sẽ kích hoạt kéo về `MEDIUM`.
> - Nếu mẫu này đồng thời có `Air Temp=HIGH`, luật `R1` sẽ kích hoạt kéo mạnh về `HIGH`.
> Phép hợp suy diễn Mamdani và giải mờ centroid sẽ tự động tổng hợp các mức thuộc này thành một điểm số liên tục, phản ánh sự tích lũy của các bằng chứng bất thường mà không gây ra xung đột logic.

---

## 5. Triển khai Động cơ Suy diễn Mờ Mamdani (FIS Engine)

Hệ thống được lập trình trực tiếp trong notebook [`notebooks/02_static_fuzzy_baseline.ipynb`](file:///notebooks/02_static_fuzzy_baseline.ipynb) (Cell 2.5.1).

### 5.1. Fuzzification liên tục giải tích (Analytical Piecewise Linear)

Để tránh sai số do lưới rời rạc, hàm thuộc tính $\mu(x)$ được tính trực tiếp từ giá trị số thực của cảm biến:

```python
def eval_mf(x, mf_type, params):
    x = float(x)
    if mf_type == "tri":
        a, b, c = params
        if a < b and a <= x <= b:
            return (x - a) / (b - a)
        elif b < c and b <= x <= c:
            return (c - x) / (c - b)
        elif x == b:
            return 1.0
        return 0.0
    elif mf_type == "trap":
        a, b, c, d = params
        if x < a:
            return 1.0 if a == b else 0.0
        elif a <= x < b:
            return (x - a) / (b - a) if b > a else 1.0
        elif b <= x <= c:
            return 1.0
        elif c < x <= d:
            return (d - x) / (d - c) if d > c else 1.0
        else:
            return 1.0 if c == d else 0.0
```

### 5.2. Thuật toán suy diễn Mamdani

Với một mẫu $x = (x_1, x_2, x_3, x_4, x_5)$:
1. **Độ kích hoạt tiền đề (Antecedent Firing Strength):**
   $$\alpha_k = \min_{(j, T) \in \text{Ant}_k} \mu_{j, T}(x_j)$$
2. **Kéo theo mờ (Fuzzy Implication):** Cắt đỉnh hàm thuộc kết luận:
   $$\mu_{R_k}(y) = \min(\alpha_k, \mu_{C_k}(y)), \quad \forall y \in [0, 1]$$
3. **Tổng hợp mờ (Aggregation):** Hợp các tập mờ kết luận:
   $$\mu_{agg}(y) = \max_{k=1..12} \mu_{R_k}(y), \quad \forall y \in [0, 1]$$
4. **Giải mờ trọng tâm (Centroid Defuzzification):**
   $$y^* = \frac{\int_0^1 y \cdot \mu_{agg}(y) \, dy}{\int_0^1 \mu_{agg}(y) \, dy}$$
   *(Nếu $\mu_{agg}(y) = 0$ trên toàn miền, gán mặc định $y^* = 0.0$)*.

---

## 6. Kiểm tra Tính Nhất quán của Phép Suy diễn trên các Mẫu Đại diện

Cell 2.5.2 đã thực hiện suy diễn thử nghiệm trên 5 mẫu có đặc tính vận hành khác nhau trong tập dữ liệu:

| UDI | Phân loại trạng thái | Nhãn thực tế | Giá trị cảm biến chính | Luật kích hoạt ($\alpha > 0$) | Anomaly Score ($y^*$) | Đánh giá hành vi suy diễn |
| :---: | :--- | :---: | :--- | :--- | :---: | :--- |
| **1** | Vận hành bình thường | **0** | RPM = 1551<br>Torque = 42.8<br>Tool Wear = 0 | `R10`: 0.8133 *(LOW)* | **0.2035** | Điểm rơi trọn vẹn trong vùng $LOW$ (trọng tâm hình thang $[0, 0, 0.25, 0.5]$ là $\approx 0.20$). |
| **2** | Chuyển tiếp (chớm tải cao) | **0** | RPM = 1408<br>Torque = 46.3<br>Tool Wear = 3 | `R5`: 0.4200 *(MEDIUM)*<br>`R10`: 0.3766 *(LOW)* | **0.3589** | Trọng tâm dịch chuyển mượt mà giữa $LOW$ và $MEDIUM$, không có sự nhảy bậc đột ngột. |
| **13** | Kích hoạt đơn thuần MEDIUM | **0** | RPM = 1339<br>Torque = 51.1<br>Tool Wear = 34 | `R5`: 0.7400 *(MEDIUM)* | **0.5000** | Khi chỉ có luật tam giác đối xứng `MEDIUM` kích hoạt, trọng tâm rơi chính xác tại đỉnh $0.5000$. |
| **70** | Hỏng hóc thực tế | **1** | RPM = 1410<br>Torque = 65.7<br>Tool Wear = 191 | `R4`: 0.6000 *(HIGH)*<br>`R5`: 0.6000 *(MEDIUM)*<br>`R8`: 1.0000 *(MEDIUM)* | **0.6468** | Tổ hợp luật $HIGH$ và $MEDIUM$ kéo điểm số vượt qua ngưỡng chuyển tiếp sang vùng $HIGH$. |
| **161** | Hỏng hóc nặng tải & mòn cao | **1** | RPM = 1282<br>Torque = 60.7<br>Tool Wear = 216 | `R4`: 1.0000 *(HIGH)*<br>`R5`: 1.0000 *(MEDIUM)*<br>`R8`: 1.0000 *(MEDIUM)* | **0.6898** | `R4` kích hoạt tối đa ($\alpha = 1.0$), diện tích $HIGH$ chi phối mạnh, điểm số đạt mức bất thường cao. |

> [!NOTE]
> Kết quả trên **đã kiểm tra tính nhất quán của phép suy diễn trên các mẫu đại diện**; chưa thể chứng minh toàn bộ hệ thống hoạt động tối ưu cho tới khi thực hiện chạy toàn bộ tập dữ liệu và đánh giá định lượng bằng các chỉ số kiểm thử.

---

## 7. Tổng kết và Kế hoạch Tiếp theo (Phase 2.6)

1. **Thành quả đạt được:**
   - Hoàn thành thiết kế hệ luật mờ 12 luật compact, minh bạch, dựa trên bằng chứng dữ liệu huấn luyện.
   - Hoàn thành động cơ suy diễn Mamdani liên tục với giải mờ centroid.
   - Xác nhận cơ chế suy diễn mờ chuyển tiếp trơn tru trên các mẫu thử nghiệm.
2. **Kế hoạch cho Phase 3:**
   - Thực thi suy diễn Mamdani trên toàn bộ tập dữ liệu (Train 6.000 mẫu, Validation 2.000 mẫu, Test 2.000 mẫu).
   - Khảo sát phân phối Anomaly Score của tập Train và tập Validation.
   - Tối ưu hóa ngưỡng phân loại $\tau \in [0, 1]$ trên tập **Validation** dựa trên các tiêu chí (F1-score, Precision-Recall AUC, PR curve).
   - Khóa chặt mô hình **Static Fuzzy Baseline** sẵn sàng cho việc so sánh ở các Phase thích nghi (Phase 3 & Phase 4).
