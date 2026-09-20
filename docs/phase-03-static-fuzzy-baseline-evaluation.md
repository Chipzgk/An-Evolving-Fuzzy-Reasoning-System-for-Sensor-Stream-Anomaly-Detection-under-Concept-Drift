# Phase 3 — Đánh giá Static Fuzzy Baseline và Khảo sát Dịch chuyển Phân phối Tự nhiên

## 1. Mục tiêu và Tóm tắt Khoa học

Phase 3 đánh dấu cột mốc hoàn thiện và đóng băng toàn diện hệ suy diễn mờ tĩnh (**Static Fuzzy Baseline**) trên quy trình dữ liệu tuần tự chuẩn hóa (Sequential Stream Split): Train (6.000 mẫu đầu), Validation (2.000 mẫu tiếp theo) và Test (2.000 mẫu cuối).

### 1.1. Tuyên bố Tổng kết Khoa học (Executive Scientific Summary)

> *"Hệ suy diễn mờ Mamdani với 5 cảm biến đầu vào và cơ sở tri thức gồm 12 luật mờ đã được đánh giá làm mốc đối chuẩn tĩnh (static baseline). Điểm bất thường (anomaly score) được chuyển đổi thành quyết định phân loại lỗi nhị phân thông qua ngưỡng quyết định được chọn độc quyền trên tập Validation theo tiêu chí cực đại hóa F1-score. Ngưỡng kết quả thu được là $\tau = 0.67$ và sau đó được đóng băng cố định cho quá trình đánh giá trên tập Test.*
> 
> *Trên tập Test, hệ cơ sở Static Fuzzy đạt Precision = 27,66%, Recall = 33,33%, và F1-score = 0,3023, với 13 trường hợp dương tính thật (TP), 34 trường hợp dương tính giả (FP), 26 trường hợp âm tính giả (FN) và 1.927 trường hợp âm tính thật (TN).*
> 
> *Phân tích sâu hơn về phân phối cho thấy các phân đoạn dữ liệu tuần tự của AI4I 2020 không đồng nhất về mặt phân phối. Cụ thể, chế độ lỗi HDF chỉ xuất hiện trong phân đoạn Train, trong khi phân đoạn Test thể hiện một phân phối nhiệt độ không khí khác biệt đáng kể. Do đó, phân đoạn Test tuần tự gốc không được coi là một mốc đối chuẩn không trôi dạt (no-drift benchmark) thuần túy. Những sai khác phân phối xuất hiện tự nhiên này được ghi nhận độc lập với các kịch bản trôi dạt có kiểm soát (controlled drift scenarios) sẽ được đưa vào ở các giai đoạn sau.*
> 
> *Vì vậy, hệ mờ Static Fuzzy cùng ngưỡng đóng băng của nó tạo thành mốc đối chuẩn cố định cho các thử nghiệm tiếp theo. Tuyệt đối không có tham số mô hình, luật mờ, hàm thuộc tính hay ngưỡng quyết định nào được tinh chỉnh lại dựa trên kết quả của tập Test."*

---

## 2. Tài nguyên Thực thi và Phân vùng Dữ liệu

- **Notebook độc lập:** [`notebooks/03_static_fuzzy_evaluation.ipynb`](file:///notebooks/03_static_fuzzy_evaluation.ipynb)
- **Tệp dữ liệu gốc:** `data/ai4i2020.csv` (10.000 mẫu, 14 thuộc tính).
- **Phân vùng tuần tự (Sequential Split theo Protocol Phase 1.5):**
  - **Train set:** 6.000 mẫu đầu (UDI 1 → 6000), tỷ lệ $60\%$.
  - **Validation set:** 2.000 mẫu tiếp theo (UDI 6001 → 8000), tỷ lệ $20\%$.
  - **Test set:** 2.000 mẫu cuối cùng (UDI 8001 → 10000), tỷ lệ $20\%$.

> [!IMPORTANT]
> Toàn bộ cấu hình của hệ mờ tĩnh (5 biến đầu vào, biến đầu ra Anomaly Score $[0, 1]$, hàm thuộc tính mờ liên tục và 12 luật Mamdani) được đóng băng nguyên vẹn từ Phase 2. Tuyệt đối không điều chỉnh luật hay tham số hình học trong Phase 3.

---

## 3. Khảo sát Phân phối Anomaly Score trên Tập Huấn luyện (Cell 3.1)

Hệ FIS được chạy suy diễn trên toàn bộ 6.000 mẫu của tập Train nhằm kiểm tra phân phối điểm số của hai lớp:

```text
Number of samples: 6000
Score range: 0.0000 → 0.6898

Mean score by actual class:
                 count      mean    median       min       max
Machine failure                                               
0                 5745  0.320477  0.225615  0.000000  0.689815
1                  255  0.558070  0.644626  0.194445  0.689815
```

### Nhận xét kiểm tra phân phối:
1. **Sự dịch chuyển điểm số mô tả (Descriptive score separation):** 
   - Lớp Failure có điểm số cao hơn rõ rệt về mặt thống kê mô tả: Median đạt $0.6446$ (so với $0.2256$ của lớp Normal) và Mean đạt $0.5581$ (so với $0.3205$).
   - Tuy nhiên, hai lớp vẫn có vùng chồng lấn (overlap) nhất định: lớp Normal có giá trị lớn nhất đạt $0.6898$, trong khi lớp Failure có giá trị nhỏ nhất là $0.1944$.
2. **Độ phủ của không gian suy diễn:**
   - Điểm số lớn nhất quan sát được trên tập Train là $0.6898$.
   - Trong toàn bộ 6.000 mẫu, chỉ có duy nhất 1 mẫu ($0.02\%$) nhận điểm $0.0$ (không kích hoạt luật nào). $99.98\%$ mẫu còn lại đều kích hoạt ít nhất một luật mờ, xác nhận không có hiện tượng "vùng chết" suy diễn.
3. **Nguyên tắc chống rò rỉ (Anti-Leakage):** Không thực hiện chọn ngưỡng $\tau$ từ tập Train.

---

## 4. Quét Ngưỡng Quyết định trên Tập Validation (Cells 3.2 – 3.4)

### 4.1. Phân phối điểm số trên Tập Validation (2.000 mẫu: UDI 6001 → 8000)

```text
Number of samples: 2000
Score range: 0.1944 → 0.6898

Mean score by actual class:
                 count      mean    median       min       max
Machine failure                                               
0                 1955  0.338487  0.233116  0.194445  0.689815
1                   45  0.525178  0.640925  0.194445  0.689815

Quantiles by actual class:
                     0.25      0.50      0.75      0.90      0.95
Machine failure                                                  
0                0.212559  0.233116  0.463213  0.620025  0.659937
1                0.227959  0.640925  0.679176  0.689815  0.689815
```

### 4.2. Khảo sát toàn diện vùng quyết định chính $\tau \in [0.50, 0.70]$ (Lưới bước quét 0.01)

| Ngưỡng $\tau$ | Precision (%) | Recall (%) | F1-Score | TP (trên 45) | FP (trên 1955) | FN | TN |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.50** | 6.87% | 71.11% | 0.1252 | 32 | 434 | 13 | 1521 |
| **0.52** | 7.51% | 71.11% | 0.1359 | 32 | 394 | 13 | 1561 |
| **0.54** | 7.87% | 68.89% | 0.1412 | 31 | 363 | 14 | 1592 |
| **0.56** | 8.52% | 66.67% | 0.1511 | 30 | 322 | 15 | 1633 |
| **0.58** | 8.86% | 62.22% | 0.1551 | 28 | 288 | 17 | 1667 |
| **0.60** | 10.11% | 60.00% | 0.1731 | 27 | 240 | 18 | 1715 |
| **0.62** | 11.31% | 55.56% | 0.1880 | 25 | 196 | 20 | 1759 |
| **0.63** | 12.37% | 53.33% | 0.2008 | 24 | 170 | 21 | 1785 |
| **0.64** | 13.87% | 53.33% | 0.2202 | 24 | 149 | 21 | 1806 |
| **0.65** | 13.33% | 44.44% | 0.2051 | 20 | 130 | 25 | 1825 |
| **0.66** | 14.04% | 35.56% | 0.2013 | 16 | 98 | 29 | 1857 |
| **0.67** | **16.85%** | **33.33%** | **0.2239** | **15** | **74** | **30** | **1881** |
| **0.68** | 17.74% | 24.44% | 0.2056 | 11 | 51 | 34 | 1904 |
| **0.69** | 0.00% | 0.00% | 0.0000 | 0 | 0 | 45 | 1955 |

---

## 5. Đóng băng Ngưỡng Quyết định Baseline (Cell 3.5)

### 5.1. Tiêu chuẩn lựa chọn và Kết quả Đóng băng
Tuân thủ tiêu chuẩn tiên quyết đã xác lập (predefined validation criterion): **Lựa chọn ngưỡng $\tau$ đạt F1-score cao nhất trên tập Validation theo lưới khảo sát bước 0.01**.

Ngưỡng được lựa chọn chính thức và đóng băng là:
$$\tau_{\text{STATIC}} = 0.67$$

```text
Frozen threshold for Static Fuzzy:
tau = 0.67

Validation performance at frozen threshold:
Precision: 0.1685 (16.85%)
Recall:    0.3333 (33.33%)
F1:        0.2239
TP: 15.0  |  FP: 74.0  |  FN: 30.0  |  TN: 1881.0
```

### 5.2. Chuẩn mực diễn giải học thuật
- Không khẳng định $\tau = 0.67$ là một ngưỡng "tối ưu phổ quát". Đây là kết quả thực nghiệm đạt $F_1$ cao nhất trên phân đoạn Validation theo đúng giao thức thử nghiệm.
- Tại $\tau = 0.64$, $F_1 = 0.2202$ bám rất sát ($0.2202$ so với $0.2239$, độ chênh $\Delta F_1 \approx 0.0037$), với Recall đạt $53.33\%$ (24/45 ca lỗi). Tuy nhiên, để bảo đảm tính nhất quán phương pháp luận, tiêu chuẩn cực đại $F_1$ được tuân thủ nghiêm ngặt mà không điều chỉnh chủ quan.
- Sau khi đóng băng $\tau_{\text{STATIC}} = 0.67$, giá trị này được giữ cố định tuyệt đối, không thay đổi.

---

## 6. Đánh giá Hiệu năng Static Fuzzy Baseline trên Tập Test (Cell 3.6)

Tập Test độc lập gồm 2.000 mẫu cuối cùng (UDI 8001 → 10000), chứa 39 mẫu Failure ($1.95\%$) và 1.961 mẫu Normal ($98.05\%$).

### 6.1. Ma trận nhầm lẫn và Chỉ số Đánh giá trên Test

```text
Static Fuzzy — Test Evaluation
--------------------------------
Test samples: 2000
Threshold:    0.67

Score range:  0.0000 → 0.6898

Confusion Matrix:
TP: 13
FP: 34
FN: 26
TN: 1927

Metrics:
Precision: 0.2766 (27.66%)
Recall:    0.3333 (33.33%)
F1:        0.3023
```

### 6.2. Đối sánh Định lượng giữa Validation và Test

| Chỉ số đánh giá | Validation Set (UDI 6001 → 8000) | Test Set (UDI 8001 → 10000) | Ghi chú so sánh |
| :--- | :---: | :---: | :--- |
| **Quy mô phân đoạn** | 2.000 mẫu | 2.000 mẫu | Thiết kế cân bằng 20% - 20% |
| **Số mẫu Failure thực tế** | 45 mẫu ($2.25\%$) | 39 mẫu ($1.95\%$) | Tỷ lệ lỗi giảm nhẹ |
| **Ngưỡng quyết định ($\tau$)** | **0.67** | **0.67** | Đóng băng cố định |
| **True Positives (TP)** | 15 | **13** | Bắt được 13/39 ca lỗi |
| **False Positives (FP)** | 74 | **34** | Giảm hơn 50% cảnh báo giả |
| **False Negatives (FN)** | 30 | **26** | Bỏ sót 26 ca lỗi |
| **True Negatives (TN)** | 1.881 | **1.927** | Nhận diện đúng mẫu bình thường |
| **Precision** | 16.85% | **27.66%** | Tăng do FP giảm |
| **Recall** | 33.33% | **33.33%** | Tỷ lệ phát hiện lỗi bằng nhau |
| **F1-Score** | 0.2239 | **0.3023** | Baseline chính thức cho bài toán |

### 6.3. Giới hạn diễn giải khoa học
- **Về Recall:** Việc Recall đạt đúng $33.33\%$ trên cả hai phân đoạn không phải bằng chứng chứng minh mô hình "hoạt động ổn định tổng quát". Nó chỉ phản ánh rằng tại ngưỡng $\tau = 0.67$, tỷ lệ phát hiện lỗi thực tế trên hai tập cụ thể này đều đạt $33.33\%$.
- **Về Precision và F1:** Không kết luận mô hình hoạt động trên Test "tốt hơn Validation". Kết quả thực nghiệm cho thấy trên tập Test, số lượng FP thấp hơn (34 so với 74), dẫn đến Precision và F1 cao hơn.

---

## 7. Khảo sát Chuyên sâu: Phân tích Phân phối Tự nhiên qua các Phân đoạn

Trước khi bước sang các kịch bản Concept Drift, một khảo sát thực nghiệm chi tiết đã được thực hiện để làm rõ: **Liệu phân đoạn Test ban đầu có đại diện cho một môi trường "No Drift" thuần túy hay không?**

### 7.1. Phân hóa chế độ lỗi thực tế (Failure Modes Breakdown)

| Chế độ lỗi cụ thể | Train (UDI 1 → 6000) | Validation (UDI 6001 → 8000) | Test (UDI 8001 → 10000) |
| :--- | :---: | :---: | :---: |
| **HDF (Heat Dissipation Failure)** | **115 mẫu** | **0 mẫu** | **0 mẫu** |
| **TWF (Tool Wear Failure)** | 26 mẫu | 10 mẫu | 10 mẫu |
| **PWF (Power Failure)** | 66 mẫu | 19 mẫu | 10 mẫu |
| **OSF (Overstrain Failure)** | 60 mẫu | 17 mẫu | 21 mẫu |
| **RNF (Random Failure)** | 14 mẫu | 5 mẫu | 0 mẫu |
| **Tổng số mẫu lỗi ($y=1$)** | **255 mẫu (4.25%)** | **45 mẫu (2.25%)** | **39 mẫu (1.95%)** |

> [!IMPORTANT]
> **Hiện tượng dịch chuyển phân bố nhãn (Label-Distribution Shift):**
> - Toàn bộ 115 ca lỗi HDF chỉ xuất hiện trong tập Train và hoàn toàn không xuất hiện ở tập Validation hay Test.
> - Sự sụt giảm tỷ lệ lỗi tổng thể (từ $4.25\%$ xuống $2.25\%$ và $1.95\%$) phản ánh một dạng **natural distribution shift / label-distribution shift** tồn tại sẵn trong dataset gốc theo thứ tự UDI.

### 7.2. Kiểm định phân phối cảm biến (Two-Sample Kolmogorov-Smirnov Tests)

| Biến cảm biến | Train Mean (Std) | Val Mean (Std) | Test Mean (Std) | KS-test Train vs Test ($D$, $p$-value) | Kết luận thống kê |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Rotational speed [rpm]** | 1540.0 (182.9) | 1539.4 (181.7) | 1534.5 (165.3) | $D = 0.0155, \; p = 0.8611$ | Không bác bỏ giả thuyết đồng phân phối |
| **Torque [Nm]** | 39.95 (9.98) | 40.04 (10.25) | 40.02 (9.66) | $D = 0.0162, \; p = 0.8249$ | Không bác bỏ giả thuyết đồng phân phối |
| **Tool wear [min]** | 108.96 (63.98) | 106.63 (63.18) | 106.25 (63.12) | $D = 0.0223, \; p = 0.4398$ | Không bác bỏ giả thuyết đồng phân phối |
| **Air temperature [K]** | 300.32 (2.28) | 300.66 (0.50) | **298.40 (0.90)** | $\mathbf{D = 0.4788, \; p < 10^{-5}}$ | **Bác bỏ giả thuyết đồng phân phối** |
| **Process temperature [K]** | 309.92 (1.67) | 310.87 (0.67) | **309.40 (1.05)** | $\mathbf{D = 0.2223, \; p < 10^{-5}}$ | **Bác bỏ giả thuyết đồng phân phối** |

### 7.3. Đánh giá học thuật chuẩn hóa
1. **Đối với các biến cơ học (RPM, Torque, Tool Wear):**
   Không phát hiện sự khác biệt có ý nghĩa thống kê về phân phối giữa tập Train và tập Test đối với RPM, Torque và Tool Wear theo các phép kiểm định Kolmogorov-Smirnov (KS) hai mẫu được áp dụng.
2. **Đối với các biến nhiệt độ (Air Temp, Process Temp):**
   Phân đoạn Test có phân phối nhiệt độ không khí trung bình thấp hơn đáng kể ($298.40\text{ K}$ so với $300.32\text{ K}$ ở Train và $300.66\text{ K}$ ở Validation).
3. **Mối liên hệ với sự suy giảm False Positives:**
   Phân phối nhiệt độ không khí thấp hơn ở phân đoạn Test nhất quán với sự sụt giảm số lượng cảnh báo giả (False Positives) quan sát được, do một số luật mờ cơ sở có chứa điều kiện tiền đề về nhiệt độ cao. Tuy nhiên, mức độ đóng góp mang tính nhân quả của sự dịch chuyển này đối với việc giảm FP chưa được tách biệt và chứng minh trực tiếp trong thử nghiệm này.

---

## 8. Kết luận và Định hướng Chuyển tiếp sang Phase 4

### 8.1. Đóng Phase 3 (Closed Baseline)
- Hệ suy diễn mờ tĩnh **Static Mamdani FIS** cùng ngưỡng cố định **$\tau_{\text{STATIC}} = 0.67$** chính thức được chốt làm mốc đối chuẩn cố định (**Fixed Baseline**).
- Điểm đối chuẩn chính thức trên tập Test:
  $$\text{Precision} = 27.66\%, \quad \text{Recall} = 33.33\%, \quad F_1 = 0.3023$$
- Tuyệt đối không tinh chỉnh lại bất kỳ tham số, tập luật hay hàm thuộc tính nào dựa trên kết quả Test.

### 8.2. Điều chỉnh phương pháp luận cho Phase 4
- **Không coi tập Test gốc là kịch bản "No Drift" thuần túy.** Các sai khác phân phối tự nhiên vốn có của bộ dữ liệu AI4I 2020 đã được ghi nhận độc lập và minh bạch.
- **Phạm vi của Phase 4:** Thiết kế giao thức dòng dữ liệu (Streaming Protocol) và chủ động tiêm (inject) các kịch bản Concept Drift có kiểm soát:
  - **Kịch bản 1 (Controlled No-Drift Stream):** Dòng dữ liệu được kiểm soát không có sự thay đổi phân phối nhân tạo.
  - **Kịch bản 2 (Sudden Drift):** Biến động đột ngột trên các kênh cảm biến cơ học (Torque / RPM).
  - **Kịch bản 3 (Gradual Drift):** Trôi dạt tiệm tiến theo thời gian mô phỏng sự suy thoái máy móc.
- Sau khi hoàn thiện khung kiểm thử của Phase 4, hệ thống mờ thích nghi (**Evolving Fuzzy System**) sẽ được triển khai và so sánh trực tiếp với Static Baseline tại Phase 5.
