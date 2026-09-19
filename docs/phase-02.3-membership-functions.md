# Phase 2.3 — Xây dựng Membership Functions (5 Inputs + 1 Output)

## 1. Mục tiêu

Phase 2.3 là bước triển khai cụ thể hóa các quyết định kiến trúc hàm thuộc tính (Membership Functions - MF) đã được xác lập về hình học và mốc tham số tại Phase 2.2. Mục tiêu của Phase 2.3:

1. **Khởi tạo miền giá trị (Universe of Discourse)** cho 5 biến cảm biến đầu vào và 1 biến đầu ra `Anomaly`.
2. **Khai báo và xác thực từng bộ MF** theo tuần tự, kiểm tra tính bao phủ (coverage) và chất lượng vùng chồng lấn (overlap) trước khi chốt.
3. **Trực quan hóa tổng hợp** toàn bộ 5 biến tại checkpoint cuối Phase 2.3, phát hiện lỗi hình học hoặc tham số trước khi bước vào thiết kế Rule Base.

> [!IMPORTANT]
> Tất cả tham số MF được thiết kế độc quyền từ thống kê phân phối tập Train (6.000 mẫu đầu). Tuyệt đối không sử dụng nhãn `Machine failure`, dữ liệu Validation hoặc Test ở bước này.

---

## 2. Tài nguyên và Môi trường

- **Notebook thực hiện:** [`notebooks/02_static_fuzzy_baseline.ipynb`](file:///notebooks/02_static_fuzzy_baseline.ipynb)
- **Thư viện chính:** `scikit-fuzzy` 0.5.0, NumPy 2.1.3, Matplotlib 3.11.0
- **Kiến trúc hình học đã thống nhất ở Phase 2.2:**
  - Tập $LOW$: Hàm hình thang (Trapezoidal MF), bão hòa $\mu = 1$ phía biên trái.
  - Tập $MEDIUM$: Hàm tam giác (Triangular MF), đỉnh tại giá trị trung tâm/trung vị.
  - Tập $HIGH$: Hàm hình thang (Trapezoidal MF), bão hòa $\mu = 1$ phía biên phải.

---

## 3. Miền giá trị Universe of Discourse (Cell 2.3.2)

Trước khi khai báo bất kỳ MF nào, miền giá trị rời rạc hóa với **1.000 điểm** được khởi tạo cho mỗi biến:

```python
# Phase 2.3.2 — Define fuzzy universes
universes = {
    "air_temp":     np.linspace(295.3, 304.5, 1000),
    "process_temp": np.linspace(305.7, 313.8, 1000),
    "rpm":          np.linspace(1168,  2886,  1000),
    "torque":       np.linspace(3.8,   76.2,  1000),
    "tool_wear":    np.linspace(0,     253,   1000),
    "anomaly":      np.linspace(0,     1,     1000),
}
```

| Biến | Min | Max | Số điểm |
| :--- | :---: | :---: | :---: |
| `air_temp` | 295.30 | 304.50 | 1000 |
| `process_temp` | 305.70 | 313.80 | 1000 |
| `rpm` | 1168.00 | 2886.00 | 1000 |
| `torque` | 3.80 | 76.20 | 1000 |
| `tool_wear` | 0.00 | 253.00 | 1000 |
| `anomaly` | 0.00 | 1.00 | 1000 |

> [!NOTE]
> 1.000 điểm này không phải dữ liệu cảm biến thực tế, mà là lưới số (grid) dùng để biểu diễn hàm thuộc tính và thực hiện inference/defuzzification trong `scikit-fuzzy`.

---

## 4. Kiểm tra thư viện scikit-fuzzy (Cell 2.3.1)

```python
import skfuzzy as fuzz
print("scikit-fuzzy:", fuzz.__version__)
```

Kết quả: **`scikit-fuzzy: 0.5.0`**

---

## 5. Air Temperature [K] (Cells 2.3.3 – 2.3.4)

### 5.1. Tham số MF

```python
air_low    = fuzz.trapmf(air_temp, [295.3, 295.3, 298.0, 300.4])
air_medium = fuzz.trimf( air_temp, [298.0, 300.4, 302.5])
air_high   = fuzz.trapmf(air_temp, [300.4, 302.5, 304.5, 304.5])
```

### 5.2. Kết quả kiểm tra phân hoạch trên toàn bộ universe (Cell 2.3.4)

```text
Minimum sum of memberships: 1.0
Maximum sum of memberships: 1.0
All points approximately equal to 1: True
Maximum deviation from 1: 0.0
```

Các MF tạo thành một partition đầy đủ và liên tục trên universe; tại các vùng chuyển tiếp, tổng membership được duy trì xấp xỉ 1, giúp tránh khoảng trống trong biểu diễn fuzzy.

### 5.3. Cơ sở thực nghiệm

| MF | Tham số | Cơ sở phân phối Train |
| :--- | :--- | :--- |
| $LOW$ | $[295.3, 295.3, 298.0, 300.4]$ | Bão hòa phía biên trái; dốc xuống qua vùng $[Q1 = 298.3, \text{Med} = 300.4]$ |
| $MEDIUM$ | $[298.0, 300.4, 302.5]$ | Đỉnh tại Median $300.4\text{ K}$; bao phủ vùng hoạt động phổ biến $IQR = [298.3, 302.3]$ |
| $HIGH$ | $[300.4, 302.5, 304.5, 304.5]$ | Bão hòa phía biên phải từ $302.5\text{ K}$ trở đi; bao phủ $P90 = 303.4\text{ K}$ |

**Chốt:** ✅ Air Temperature MF

---

## 6. Process Temperature [K] (Cell 2.3.5)

### 6.1. Tham số MF

```python
process_low    = fuzz.trapmf(process_temp, [305.7, 305.7, 308.0, 309.7])
process_medium = fuzz.trimf( process_temp, [308.0, 309.7, 311.5])
process_high   = fuzz.trapmf(process_temp, [309.7, 311.5, 313.8, 313.8])
```

### 6.2. Kết quả kiểm tra phân hoạch

```text
Minimum sum of memberships: 1.0
Maximum sum of memberships: 1.0
All points approximately equal to 1: True
Maximum deviation from 1: 0.0
```

Các MF tạo thành một partition đầy đủ và liên tục trên universe; tổng membership được duy trì xấp xỉ 1 trên toàn bộ 1.000 điểm.

### 6.3. Cơ sở thực nghiệm

| MF | Tham số | Cơ sở phân phối Train |
| :--- | :--- | :--- |
| $LOW$ | $[305.7, 305.7, 308.0, 309.7]$ | Bao phủ $P05 = 307.5\text{ K}$; dốc qua $[Q1 = 308.6, \text{Med} = 309.7]$ |
| $MEDIUM$ | $[308.0, 309.7, 311.5]$ | Đỉnh tại Median $309.7\text{ K}$ |
| $HIGH$ | $[309.7, 311.5, 313.8, 313.8]$ | Bao phủ $P90 = 312.3\text{ K}$ và $P95 = 312.8\text{ K}$ |

**Chốt:** ✅ Process Temperature MF

---

## 7. Rotational Speed [rpm] (Cells 2.3.6 – 2.3.7)

### 7.1. Phân tích phân phối theo vùng (Cell 2.3.6)

Trước khi thiết kế MF, mật độ dữ liệu của RPM được khảo sát theo từng khoảng vận hành:

| Vùng $[x_1, x_2)\text{ rpm}$ | Count | % |
| :---: | :---: | :---: |
| $[1168, 1300)$ | 126 | 2.10% |
| $[1300, 1400)$ | 978 | 16.30% |
| $[1400, 1500)$ | **1827** | **30.45%** |
| $[1500, 1600)$ | **1422** | **23.70%** |
| $[1600, 1700)$ | 842 | 14.03% |
| $[1700, 1800)$ | 355 | 5.92% |
| $[1800, 2000)$ | 310 | 5.17% |
| $[2000, 2200)$ | 78 | 1.30% |
| $[2200, 2500)$ | 38 | 0.63% |
| $[2500, 3000)$ | 24 | 0.40% |

Phân phối RPM lệch phải mạnh (Skewness $= +2.113$, Kurtosis $= +8.262$): hơn $54\%$ dữ liệu tập trung trong $[1400, 1600)\text{ rpm}$, trong khi đuôi phải trải dài từ $1612$ đến $2886\text{ rpm}$ (chiếm $\approx 7.5\%$).

> [!NOTE]
> Các mẫu RPM ở vùng tốc độ cao ít phổ biến trong tập Train (trên $2000\text{ rpm}$) được mô tả là **vùng tốc độ cao ít phổ biến (rare high-value operational regions)**, chưa phải "bất thường" theo nghĩa của bài toán trước khi FIS được đánh giá.

### 7.2. Tham số MF (Thiết kế bất đối xứng — Revised)

Phiên bản ban đầu sử dụng `MEDIUM = [1400, 1504, 1750]` dẫn đến vùng chuyển tiếp $MEDIUM$–$HIGH$ có coverage xuống $0.536$. Sau khi tinh chỉnh, `MEDIUM` được mở rộng:

```python
rpm_low    = fuzz.trapmf(rpm, [1168, 1168, 1350, 1500])
rpm_medium = fuzz.trimf( rpm, [1350, 1504, 1800])   # Revised từ [1400, 1504, 1750]
rpm_high   = fuzz.trapmf(rpm, [1600, 1880, 2886, 2886])
```

### 7.3. Kết quả kiểm tra phân hoạch (Revised)

```text
Minimum sum of memberships: 0.676
Maximum sum of memberships: 1.0
All points approximately equal to 1: False
Maximum deviation from 1: 0.324
Min sum occurs at RPM ≈ 1601 rpm
```

MF được thiết kế bất đối xứng để phù hợp với phân phối lệch phải của RPM. Kết quả kiểm tra cho thấy vùng chuyển tiếp $MEDIUM$–$HIGH$ có tổng membership thấp nhất khoảng $0.676$. Điều này không phải lỗi thiết kế — đây không phải bắt buộc là một Ruspini partition. Quan trọng hơn, tại mọi điểm trên universe đều có ít nhất một tập mờ kích hoạt với mức thuộc $\mu \geq 0.676 > 0$.

### 7.4. Cơ sở thực nghiệm

| MF | Tham số | Cơ sở phân phối Train |
| :--- | :--- | :--- |
| $LOW$ | $[1168, 1168, 1350, 1500]$ | Bão hòa từ Min đến $1350$; chuyển tiếp dần sang $\text{Med} = 1504$ |
| $MEDIUM$ | $[1350, 1504, 1800]$ | Đỉnh tại Median $1504\text{ rpm}$; mở rộng sang $P90 = 1748$ để tạo overlap tốt hơn |
| $HIGH$ | $[1600, 1880, 2886, 2886]$ | Bão hòa từ $1880\text{ rpm}$ (sát $P95 = 1877$); bao phủ toàn bộ đuôi đến Max $= 2886$ |

**Chốt:** ✅ Rotational Speed MF *(thiết kế bất đối xứng có chủ đích)*

---

## 8. Torque [Nm] (Cells 2.3.8 – 2.3.9)

### 8.1. Phân tích phân phối theo vùng (Cell 2.3.8)

Torque có đặc điểm gần đối xứng (Skewness $= -0.034$, Kurtosis $= +0.038$), đỉnh tập trung tại $[35, 45)\text{ Nm}$ chiếm gần $38\%$. Hai đuôi cân đối:
- Đuôi trái ($< 25\text{ Nm}$): $\approx 5.07\%$
- Đuôi phải ($> 55\text{ Nm}$): $\approx 5.97\%$

### 8.2. Tham số MF

```python
torque_low    = fuzz.trapmf(torque, [3.8, 3.8, 25.0, 40.0])
torque_medium = fuzz.trimf( torque, [25.0, 40.0, 55.0])
torque_high   = fuzz.trapmf(torque, [40.0, 55.0, 76.2, 76.2])
```

### 8.3. Kết quả kiểm tra phân hoạch

```text
Minimum sum of memberships: 1.0
Maximum sum of memberships: 1.0
Maximum deviation from 1: 0.0
```

### 8.4. Cơ sở thực nghiệm

| MF | Tham số | Cơ sở phân phối Train |
| :--- | :--- | :--- |
| $LOW$ | $[3.8, 3.8, 25.0, 40.0]$ | Bão hòa từ Min đến $25\text{ Nm}$ (bao $P05 = 23.3$); dốc về Median |
| $MEDIUM$ | $[25.0, 40.0, 55.0]$ | Đỉnh tại Median $40.0\text{ Nm}$; bao phủ $IQR = [33.3, 46.8]$ |
| $HIGH$ | $[40.0, 55.0, 76.2, 76.2]$ | Bão hòa từ $55\text{ Nm}$ (sát $P95 = 55.8$); bao phủ đến Max $= 76.2$ |

Các mốc $25\text{ Nm}$ và $55\text{ Nm}$ phù hợp với đặc điểm gần đối xứng của phân phối quan sát được: dưới $25\text{ Nm}$ và trên $55\text{ Nm}$ mỗi bên chiếm khoảng $5 - 6\%$ mẫu.

**Chốt:** ✅ Torque MF

---

## 9. Tool Wear [min] (Cells 2.3.10 – 2.3.11)

### 9.1. Phân tích phân phối theo vùng (Cell 2.3.10)

Tool Wear có đặc điểm phân bố đáng chú ý nhất trong 5 biến (Skewness $= +0.023$, Kurtosis $= -1.159$):

| Vùng $[x_1, x_2)\text{ min}$ | Count | % | Ghi chú |
| :---: | :---: | :---: | :--- |
| $[0, 20)$ đến $[180, 200)$ | $534 - 569$ mỗi khoảng | $8.9 - 9.5\%$ | **Gần như đều nhau** — đặc điểm gần uniform |
| $[200, 220)$ | 413 | 6.88% | Bắt đầu giảm mật độ |
| $[220, 240)$ | 95 | 1.58% | Mật độ giảm mạnh |
| $[240, 260)$ | 10 | 0.17% | Vùng cực trị đuôi |

10 khoảng liên tiếp từ $[0, 200)\text{ min}$ mỗi khoảng đều xấp xỉ $8.9 - 9.5\%$ — phân phối gần đều (uniform-like). Không có vùng trung tâm tự nhiên rõ rệt, nên các mốc MF được đặt theo $Q1 = 54$, $\text{Med} = 109$, $Q3 = 164$ thay vì tìm đỉnh tần suất.

### 9.2. Tham số MF

```python
tool_wear_low    = fuzz.trapmf(tool_wear, [0,   0,   54,  109])
tool_wear_medium = fuzz.trimf( tool_wear, [54,  109, 164])
tool_wear_high   = fuzz.trapmf(tool_wear, [109, 164, 253, 253])
```

### 9.3. Kết quả kiểm tra phân hoạch

```text
Minimum sum of memberships: 1.0
Maximum sum of memberships: 1.0
Maximum deviation from 1: 0.0
```

### 9.4. Cơ sở thực nghiệm

| MF | Tham số | Cơ sở phân phối Train |
| :--- | :--- | :--- |
| $LOW$ | $[0, 0, 54, 109]$ | Bão hòa từ $0$ đến $Q1 = 54\text{ min}$; chuyển tiếp qua Median $109$ |
| $MEDIUM$ | $[54, 109, 164]$ | Đỉnh tại Median $109\text{ min}$; đối xứng qua $IQR = [54, 164]$ |
| $HIGH$ | $[109, 164, 253, 253]$ | Bão hòa từ $Q3 = 164\text{ min}$; bao phủ phần đuôi đến Max $= 253$ |

Bộ mốc $Q1/\text{Med}/Q3$ phù hợp với đặc điểm gần đều trong khoảng $0 - 200\text{ min}$, nơi không có một vùng trung tâm tự nhiên rõ rệt để đặt đỉnh MF một cách trực quan hơn.

**Chốt:** ✅ Tool Wear MF

---

## 10. Checkpoint Trực quan hóa Tổng hợp 5 Biến (Cell 2.3.12)

Tại bước cuối Phase 2.3, toàn bộ 5 bộ MF được vẽ và kiểm tra 4 tiêu chí trực quan:

| Tiêu chí kiểm tra | Air Temp | Process Temp | RPM | Torque | Tool Wear |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Không có khoảng trống** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Overlap hợp lý** | ✅ | ✅ | ✅* | ✅ | ✅ |
| **Phù hợp phân phối Train** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Không có lỗi code/tham số** | ✅ | ✅ | ✅ | ✅ | ✅ |

*RPM có vùng chuyển tiếp $MEDIUM$–$HIGH$ với $\min\sum\mu = 0.676$, là quyết định thiết kế có chủ đích phù hợp với phân phối lệch phải mạnh.

---

## 11. Tóm tắt bảng tham số MF đã chốt

| Sensor | Universe $[x_{\min}, x_{\max}]$ | $LOW$ (Trapezoidal) | $MEDIUM$ (Triangular) | $HIGH$ (Trapezoidal) |
| :--- | :---: | :--- | :--- | :--- |
| **Air Temp [K]** | $[295.3, 304.5]$ | $[295.3, 295.3, 298.0, 300.4]$ | $[298.0, 300.4, 302.5]$ | $[300.4, 302.5, 304.5, 304.5]$ |
| **Process Temp [K]** | $[305.7, 313.8]$ | $[305.7, 305.7, 308.0, 309.7]$ | $[308.0, 309.7, 311.5]$ | $[309.7, 311.5, 313.8, 313.8]$ |
| **RPM [rpm]** | $[1168, 2886]$ | $[1168, 1168, 1350, 1500]$ | $[1350, 1504, 1800]$ | $[1600, 1880, 2886, 2886]$ |
| **Torque [Nm]** | $[3.8, 76.2]$ | $[3.8, 3.8, 25.0, 40.0]$ | $[25.0, 40.0, 55.0]$ | $[40.0, 55.0, 76.2, 76.2]$ |
| **Tool Wear [min]** | $[0, 253]$ | $[0, 0, 54, 109]$ | $[54, 109, 164]$ | $[109, 164, 253, 253]$ |

---

## 12. Kế hoạch chuyển tiếp sang Phase 2.4

Sau khi hoàn tất 5 bộ MF đầu vào, bước tiếp theo sẽ là **Phase 2.4 — Thiết kế Fuzzy Rule Base** cho biến đầu ra `Anomaly $\in [0, 1]$`:
1. Thiết kế 3 tập mờ đầu ra: `Anomaly_LOW`, `Anomaly_MEDIUM`, `Anomaly_HIGH`.
2. Xây dựng tập luật $IF$–$THEN$ (~10–20 rules) kết hợp đa biến, sao cho các trạng thái vận hành bất thường (tải cao + nhiệt độ cao + mòn cao) sẽ kích hoạt `Anomaly_HIGH`.
3. Tuân thủ cấu hình Mamdani đã chốt: AND = min, Implication = min, Aggregation = max, Defuzzification = centroid.
