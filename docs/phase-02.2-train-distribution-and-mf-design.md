# Phase 2.2 — Phân tích phân phối Train và Thiết kế mốc Membership Functions

## 1. Mục tiêu

Phase 2.2 là bước triển khai thực nghiệm và định lượng tri thức đầu tiên của hệ mờ tĩnh (**Static Fuzzy Baseline**), tiếp nối sau khi đã hoàn thành kiến trúc mục tiêu ở [Phase 2.1](file:///docs/phase-02.1-fuzzy-reasoning-target.md). 

Mục tiêu cốt lõi của Phase 2.2:
1. **Phân tích thực nghiệm phân phối 5 biến cảm biến đầu vào** trên toàn bộ 6.000 mẫu của tập Train ($UDI: 1 \to 6.000$).
2. **Khảo sát độ xiên (skewness), độ nhọn (kurtosis), độ dài đuôi và mật độ dữ liệu** nhằm tránh việc phân chia cứng nhắc hoặc đặt ngưỡng cảm tính (heuristic/arbitrary).
3. **Chuẩn hóa ranh giới học thuật**: Phân biệt rạch ròi giữa *"vùng giá trị cao/thấp hiếm gặp"* (rare operating states) với *"trạng thái bất thường"* (anomalies) trong giai đoạn phân tích phân phối thống kê.
4. **Xác định hình dạng hình học và đề xuất các mốc định lượng (Candidate MF Parameters)** cho các tập mờ $LOW$, $MEDIUM$, $HIGH$ của từng biến cảm biến, bảo đảm tính giao thoa (overlap) và nguyên lý vật lý vận hành của thiết bị cơ khí.

---

## 2. Tài nguyên và Môi trường thực hiện

- **Tệp dữ liệu**: `data/ai4i2020.csv` (sử dụng 6.000 dòng đầu tiên $UDI: 1 \to 6.000$, chỉ số index $0 \to 5.999$).
- **Notebook thực hiện**: [`notebooks/02_static_fuzzy_baseline.ipynb`](file:///notebooks/02_static_fuzzy_baseline.ipynb) (Notebook độc lập cho Phase 2 nhằm bảo toàn nguyên vẹn notebook khảo sát Phase 1).
- **Thư viện**: Python 3.11.15, NumPy 2.1.3, Pandas 2.2.3, Matplotlib 3.11.0, `scikit-fuzzy` 0.5.0 (đã cập nhật vào `requirements.txt`).

---

## 3. Nguyên tắc phương pháp luận & Chống rò rỉ dữ liệu (Anti-Leakage)

> [!IMPORTANT]
> **Toàn bộ tri thức và tham số của Static FIS được thiết kế độc quyền từ 6.000 mẫu tập Train.**
> - Tuyệt đối **không sử dụng nhãn `Machine failure`** để dò tìm hay tối ưu hóa các mốc hàm thuộc tính trong giai đoạn này.
> - Tuyệt đối **không tham chiếu đến dữ liệu Validation hay Test**. Mọi tham số hàm thuộc tính ở Phase 2.2 là các thông số ứng viên ban đầu (Candidate MF Parameters); tính tối ưu và năng lực tổng quát hóa của chúng sẽ chỉ được đánh giá khách quan trên tập Validation ở các bước sau.

---

## 4. Kết quả thống kê mô tả 5 biến cảm biến (Cell 2.2.1)

Mã nguồn thực thi tại Cell 2.2.1:
```python
# Phase 2.2.1 — Prepare training data
train_df = df.iloc[:6000].copy()
print("Train shape:", train_df.shape)
print("UDI range:", train_df["UDI"].min(), "→", train_df["UDI"].max())
display(train_df[sensor_cols].describe().T)
```

Kết quả in ra:
- **Kích thước Train:** $(6000, 14)$
- **Phạm vi UDI:** $1 \to 6000$

### Bảng thống kê mô tả (`train_df[sensor_cols].describe().T`):

| Biến cảm biến | count | mean | std | min | 25% (Q1) | 50% (Median) | 75% (Q3) | max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Air temperature [K]** | 6000.0 | 300.3216 | 2.2835 | 295.3 | 298.300 | 300.4 | 302.3 | 304.5 |
| **Process temperature [K]** | 6000.0 | 309.9220 | 1.6650 | 305.7 | 308.600 | 309.7 | 311.1 | 313.8 |
| **Rotational speed [rpm]** | 6000.0 | 1539.9997 | 182.9094 | 1168.0 | 1422.000 | 1504.0 | 1612.0 | 2886.0 |
| **Torque [Nm]** | 6000.0 | 39.9550 | 9.9770 | 3.8 | 33.275 | 40.0 | 46.8 | 76.2 |
| **Tool wear [min]** | 6000.0 | 108.9600 | 63.9765 | 0.0 | 54.000 | 109.0 | 164.0 | 253.0 |

---

## 5. Phân tích phân phối chi tiết qua các phân vị (Cell 2.2.2)

Để quan sát sâu vào độ dài phần đuôi và các vùng biên mật độ thấp, tập Train được khảo sát qua 9 mốc phân vị (Quantiles):
$$\{0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99\}$$

### Bảng giá trị phân vị chi tiết (`distribution_stats`):

| Biến cảm biến | 1% | 5% | 10% | 25% (Q1) | 50% (Median) | 75% (Q3) | 90% | 95% | 99% |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Air temperature [K]** | 295.600 | 296.800 | 297.400 | 298.300 | 300.400 | 302.300 | 303.400 | 303.700 | 304.200 |
| **Process temperature [K]** | 306.200 | 307.500 | 307.800 | 308.600 | 309.700 | 311.100 | 312.300 | 312.800 | 313.400 |
| **Rotational speed [rpm]** | 1278.000 | 1331.000 | 1363.900 | 1422.000 | 1504.000 | 1612.000 | 1748.000 | 1877.000 | 2206.050 |
| **Torque [Nm]** | 16.499 | 23.300 | 27.190 | 33.275 | 40.000 | 46.800 | 52.500 | 55.800 | 62.800 |
| **Tool wear [min]** | 0.000 | 10.000 | 20.000 | 54.000 | 109.000 | 164.000 | 197.000 | 208.000 | 225.000 |

### Đánh giá định lượng từ bảng phân vị:
1. **Air Temperature & Process Temperature:** 
   - Độ trải từ $1\%$ đến $99\%$ rất hẹp: Air Temp trong khoảng $[295.6\text{ K}, 304.2\text{ K}]$, Process Temp trong khoảng $[306.2\text{ K}, 313.4\text{ K}]$.
   - Tính đối xứng thể hiện rõ khi Median ($300.4$ và $309.7$) nằm chính xác ở vị trí trung tâm của khoảng tứ phân vị $IQR = Q3 - Q1$.
2. **Rotational speed:**
   - $IQR$ chỉ vỏn vẹn $190\text{ rpm}$ ($[1422, 1612]$).
   - Tuy nhiên, từ $Q3$ ($1612$) lên phân vị $90\%$ ($1748$), $95\%$ ($1877$), $99\%$ ($2206$) và giá trị Max ($2886$) tạo thành một dải dữ liệu trải dài hơn $1200\text{ rpm}$. Nếu chia đều một cách máy móc theo khoảng giá trị $[1168, 2886]$, tập mờ sẽ bị biến dạng nghiêm trọng.
3. **Torque:**
   - Phân bố tập trung chủ yếu quanh $40.0\text{ Nm}$ với độ mở rộng cân đối ở cả hai phía: vùng thấp dưới $23.3\text{ Nm}$ ($5\%$) và vùng cao trên $55.8\text{ Nm}$ ($95\%$).
4. **Tool wear:**
   - Giá trị phân vị tăng gần như tuyến tính: $25\% \approx 54\text{ min}$, $50\% \approx 109\text{ min}$, $75\% \approx 164\text{ min}$. Khoảng cách giữa các phần tư đều xấp xỉ $55\text{ min}$.

---

## 6. Khảo sát hình dạng phân phối thực tế (Cell 2.2.3)

Cell 2.2.3 trực quan hóa biểu đồ tần suất (Histogram) 40 bins cho cả 5 biến cảm biến:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ Distribution Characteristics Analysis:                                │
│ 1. Vùng tập trung (Central concentration)                              │
│ 2. Độ xiên (Skewness - Lệch trái hay lệch phải)                        │
│ 3. Độ dài phần đuôi (Tail length & Kurtosis)                           │
│ 4. Tính liên tục và phân cụm (Multimodality / Gaps)                    │
└────────────────────────────────────────────────────────────────────────┘
```

| Cảm biến | Dải giá trị $[Min, Max]$ | Đỉnh tập trung cao nhất | Độ xiên (Skewness) | Độ nhọn (Kurtosis) | Đặc tính hình dạng quan sát được |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Air temperature** | $[295.3, 304.5]$ | $[302.2, 302.4]$ | $-0.099$ | $-1.176$ | Đơn cụm, dạng chuông bẹt (platykurtic), không có khoảng trống. |
| **Process temperature** | $[305.7, 313.8]$ | $[309.1, 309.4]$ | $+0.142$ | $-0.676$ | Đơn cụm, đối xứng cao, dịch chuyển cao hơn Air Temp $\approx 9.5\text{ K}$. |
| **Rotational speed** | $[1168.0, 2886.0]$ | $[1425.7, 1468.7]$ | **$+2.113$** | **$+8.262$** | **Lệch phải rất mạnh (heavy right tail)**; vùng $>2500\text{ rpm}$ rất thưa thớt. |
| **Torque** | $[3.8, 76.2]$ | $[41.8, 43.6]$ | $-0.034$ | $+0.038$ | Dạng chuẩn Gauss đối xứng hoàn hảo, mật độ ở 2 biên đủ dày để tạo MF. |
| **Tool wear** | $[0.0, 253.0]$ | $[0.0, 6.3]$ | $+0.023$ | $-1.158$ | **Gần phân phối đều (Uniform-like)** từ $0 \to 200\text{ min}$, giảm nhẹ về cuối. |

---

## 7. Chuẩn hóa thuật ngữ học thuật (Academic Terminology Standardization)

> [!IMPORTANT]
> **Phân định rõ ràng giữa "Vùng giá trị cao/thấp hiếm gặp" và "Trạng thái bất thường" (Anomaly):**
> 
> Trong quá trình phân tích phân phối thống kê:
> - Các mẫu có $\text{Rotational speed} > 2200\text{ rpm}$, $\text{Torque} > 55\text{ Nm}$ hoặc $\text{Tool wear} > 200\text{ min}$ **chỉ được gọi là các vùng vận hành giá trị cao hiếm gặp (rare high-value operational regions)**.
> - Các mẫu này **chưa thể khẳng định là bất thường (anomalies)**. Một giá trị cảm biến đơn lẻ nằm ở biên chưa đồng nghĩa với việc máy móc gặp lỗi hoặc hỏng hóc.
> - Giá trị chỉ chính thức trở thành "bất thường" theo định nghĩa của bài toán **sau khi toàn bộ hệ suy luận mờ (Mamdani FIS) được xây dựng, tổng hợp luật liên kết đa biến và sinh ra chỉ số $A(\mathbf{x}) \ge \tau$ được đánh giá thực nghiệm**.

---

## 8. Thiết kế hình học của các Membership Functions (MF Shape)

### 8.1. Lựa chọn dạng hình học: Trapezoidal kết hợp Triangular

Để phục vụ bài toán giám sát luồng cảm biến theo hướng **AI có thể giải thích được (Explainable AI - XAI)**, dạng hình học của hàm thuộc tính cho mỗi biến đầu vào được lựa chọn:
- **Tập $LOW$:** Sử dụng hàm **Hình thang (Trapezoidal MF)** có vai trái bão hòa bằng 1 ($\mu_{LOW}(x) = 1$ khi $x \le a$). Điều này bảo đảm mọi giá trị cực thấp đều được gán mức độ thỏa mãn tối đa của tập $LOW$.
- **Tập $MEDIUM$:** Sử dụng hàm **Tam giác (Triangular MF)** có đỉnh nhọn tại trung tâm/trung vị của phân bố dữ liệu ($\mu_{MEDIUM}(m) = 1$). Đây là vùng vận hành danh định (nominal/normal state) dễ giải thích nhất.
- **Tập $HIGH$:** Sử dụng hàm **Hình thang (Trapezoidal MF)** có vai phải bão hòa bằng 1 ($\mu_{HIGH}(x) = 1$ khi $x \ge d$). Bảo đảm mọi giá trị vượt ngưỡng cực cao đều kích hoạt trọn vẹn tập $HIGH$.

### 8.2. Mô hình trực quan hình học:
```text
  Membership
   μ(x)
   1.0 ──────┐                                     ┌──────
             │\                                   /│
             │ \     LOW         MEDIUM     HIGH / │
             │  \                 /\            /  │
             │   \               /  \          /   │
             │    \             /    \        /    │
   0.0 ──────┴─────\───────────/──────\──────/─────┴────── x (Input)
                   a     b     c      d     e      f
                     (Overlap 1)        (Overlap 2)
```

### 8.3. Rationale (Lý do kỹ thuật và khoa học):
1. **Phù hợp ranh giới vật lý:** Ở các vùng biên ($LOW$ và $HIGH$), trạng thái máy móc cần sự khẳng định dứt khoát ($\mu = 1.0$), hình thang đáp ứng trọn vẹn hơn tam giác.
2. **Tiết kiệm tham số:** Dạng hình thang + tam giác phân đoạn tuyến tính (piecewise linear) đòi hỏi ít tham số tính toán hơn đáng kể so với Gaussian hoặc Bell-shaped MF, giúp suy luận nhanh trong môi trường stream.
3. **Tính trực quan và minh bạch:** Tránh việc đưa hàm phi tuyến (Gaussian) vào khi chưa có bằng chứng thực nghiệm cho thấy sự vượt trội, tuân thủ nguyên lý *Occam's razor*.

---

## 9. Đề xuất các mốc hàm thuộc tính ban đầu (Candidate MF Parameters)

Dựa trên thống kê phân vị và phân bố thực tế tại các bước trên, bảng mốc ứng viên ban đầu cho 5 biến cảm biến được thiết lập như sau:

| Biến cảm biến | Miền khảo sát Train $[x_{\min}, x_{\max}]$ | Tập mờ $LOW$ (Trapezoidal) | Tập mờ $MEDIUM$ (Triangular) | Tập mờ $HIGH$ (Trapezoidal) | Cơ sở thực nghiệm & Vật lý |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Air temp [K]** | $[295.3, 304.5]$ | $[295.3, 295.3, 298.0, 300.4]$ | $[298.0, 300.4, 302.5]$ | $[300.4, 302.5, 304.5, 304.5]$ | Đối xứng hẹp quanh Median $300.4\text{ K}$; $Q1=298.3$, $Q3=302.3$. |
| **Process temp [K]** | $[305.7, 313.8]$ | $[305.7, 305.7, 308.0, 309.7]$ | $[308.0, 309.7, 311.5]$ | $[309.7, 311.5, 313.8, 313.8]$ | Đối xứng quanh Median $309.7\text{ K}$; $Q1=308.6$, $Q3=311.1$. |
| **Rotational speed [rpm]** | $[1168, 2886]$ | $[1168, 1168, 1420, 1504]$ | $[1420, 1504, 1750]$ | $[1612, 1880, 2886, 2886]$ | Vùng đuôi phải trải dài: đỉnh $LOW$ chặn tại $1504$, $HIGH$ mở rộng qua $95\%$ ($1877$). |
| **Torque [Nm]** | $[3.8, 76.2]$ | $[3.8, 3.8, 33.0, 40.0]$ | $[33.0, 40.0, 47.0]$ | $[40.0, 47.0, 76.2, 76.2]$ | Đối xứng cân bằng quanh $40.0\text{ Nm}$; vùng chuyển tiếp $IQR$ $[33.3, 46.8]$. |
| **Tool wear [min]** | $[0, 253]$ | $[0, 0, 54, 109]$ | $[54, 109, 164]$ | $[109, 164, 253, 253]$ | Phân bố đều: 3 mốc tương ứng hoàn hảo với $Q1=54$, $\text{Med}=109$, $Q3=164$. |

> [!NOTE]
> Bảng tham số trên mang tính chất **Candidate Parameters**. Trong các bước tiếp theo của Phase 2 và Phase 3, các mốc này sẽ được kiểm nghiệm tính hợp lý qua phản hồi của hệ suy luận trên tập Validation.

---

## 10. Môi trường triển khai thư viện (`scikit-fuzzy`)

Tại Cell 2.3.1, thư viện chuyên dụng cho suy luận mờ đã được cấu hình và kiểm tra thành công:
- Tên gói: `scikit-fuzzy`
- Phiên bản xác nhận: **`0.5.0`**
- File phụ thuộc [`requirements.txt`](file:///requirements.txt) đã được cập nhật đồng bộ.

---

## 11. Tóm tắt Checkpoint Phase 2.2 và Kế hoạch Phase 2.3

| Hạng mục | Tình trạng | Kết luận / Quyết định |
| :--- | :---: | :--- |
| **Tập dữ liệu phân tích** | Hoàn thành | 6.000 mẫu Train ($UDI: 1 \to 6.000$). |
| **Phân tích phân phối** | Hoàn thành | Đã tính toán đầy đủ Describe, 9 Phân vị Quantiles, và vẽ 5 biểu đồ Histogram. |
| **Bảo toàn file cũ** | Đảm bảo 100% | Tạo notebook mới `notebooks/02_static_fuzzy_baseline.ipynb`, giữ nguyên các file Phase 1. |
| **Chuẩn hóa học thuật** | Hoàn thành | Quy ước gọi "vùng giá trị cao/thấp hiếm gặp", chưa coi là "anomaly" khi chưa suy luận FIS. |
| **Kiến trúc hàm thuộc tính** | Thống nhất | Dạng Trapezoidal ($LOW$) — Triangular ($MEDIUM$) — Trapezoidal ($HIGH$) với vùng chồng lấn (overlap). |
| **Thư viện nền tảng** | Đã sẵn sàng | Cài đặt và kiểm tra thành công `scikit-fuzzy` 0.5.0. |

### Hướng tiếp theo (Phase 2.3):
1. Khai báo các đối tượng `fuzz.trapmf` và `fuzz.trimf` độc lập cho từng biến trong Python.
2. Thiết kế hàm thuộc tính cho biến đầu ra: `Anomaly` $\in [0, 1]$ với 3 tập mờ: $LOW$, $MEDIUM$, $HIGH$.
3. Vẽ đồ thị trực quan hóa hình dạng của toàn bộ 5 biến cảm biến đầu vào và 1 biến đầu ra để nghiệm thu trước khi bước vào xây dựng Rule Base (Phase 2.4).
