# Phase 1.5 - Giao thức dữ liệu thử nghiệm (Experimental Data Protocol)

## 1. Mục tiêu

Phase 1.5 được thực hiện như một bước chuẩn hóa phương pháp luận thử nghiệm (experimental protocol) ngay sau khi hoàn thành khám phá dữ liệu (Phase 1) và trước khi bắt tay vào thiết kế hệ mờ (Phase 2).

Mục tiêu duy nhất của Phase 1.5:
1. Xác định quy ước thứ tự luồng dữ liệu (stream order).
2. Thiết lập cơ chế phân chia Train / Validation / Test theo thứ tự stream tuần tự (sequential split), kiên quyết **không sử dụng phân chia ngẫu nhiên (random split)**.
3. Phân định rõ ràng mục đích sử dụng của từng phân vùng để bảo đảm tính khách quan, chống rò rỉ dữ liệu (data leakage) và tạo tiền đề cho phép so sánh công bằng giữa **Static Fuzzy Baseline** và **Evolving Fuzzy System**.

> [!NOTE]
> Trong Phase 1.5, toàn bộ các thành phần như Fuzzy Logic, ADWIN, cơ chế phát hiện / thích ứng Concept Drift và thuật toán Evolving đều **chưa được cài đặt**, tuân thủ nguyên tắc triển khai theo từng pha độc lập và có kiểm soát.

---

## 2. Tài nguyên và nguồn kiểm tra

- **Tệp dữ liệu gốc**: `data/ai4i2020.csv` (10.000 dòng, 14 cột).
- **Notebook thực hiện**: `notebooks/01_exploration.ipynb` (Mục `## 10. Experimental Data Protocol`).
- **Môi trường**: Python 3.11.15, NumPy 2.1.3, Pandas 2.2.3.

---

## 3. Quy ước thứ tự Stream (Stream Order Convention)

### 3.1. Bản chất tập dữ liệu và tuyên bố khoa học
Tập dữ liệu AI4I 2020 Predictive Maintenance Dataset không chứa cột mốc thời gian thực tế (timestamp) và không phải là một benchmark concept drift tự nhiên có sẵn từ nhà máy. 

Do đó, để phục vụ bài toán xử lý luồng (data stream mining) một cách chặt chẽ và khoa học, dự án đưa ra quy ước:
- **Giữ nguyên thứ tự dòng của dataset theo chỉ số `UDI` (1 đến 10.000) và coi đây là thứ tự luồng thử nghiệm cơ sở (experimental stream order)**.
- **Không ngộ nhận hoặc gọi đây là "thời gian thực tế của máy" trong báo cáo**.

Trong các báo cáo khoa học và tài liệu kỹ thuật của dự án, quy ước này được chuẩn hóa bằng tuyên bố sau:

> *"Since AI4I 2020 does not provide a natural concept-drift benchmark, the original sample ordering is retained as the base stream order, while controlled distribution changes are later injected to construct experimental concept-drift scenarios."*

---

## 4. Kết quả kiểm tra trong Notebook (`01_exploration.ipynb`)

Phần kiểm tra đã được thêm vào cuối notebook `notebooks/01_exploration.ipynb` tại mục **10. Experimental Data Protocol** với 3 code cell cụ thể:

### 4.1. Cell 1 — Kiểm tra đầu và cuối của cột `UDI`
```python
display(df["UDI"].head(10))
display(df["UDI"].tail(10))
```
- **Kết quả đầu luồng (head 10)**: Giá trị `UDI` chạy từ `1` đến `10` tương ứng với các index từ `0` đến `9`.
- **Kết quả cuối luồng (tail 10)**: Giá trị `UDI` chạy từ `9991` đến `10000` tương ứng với các index từ `9990` đến `9999`.

### 4.2. Cell 2 — Kiểm tra tính đơn điệu của `UDI`
```python
df["UDI"].is_monotonic_increasing
```
- **Kết quả**: `True`.
- **Ý nghĩa**: Cột `UDI` được kiểm tra có thứ tự tăng đơn điệu. Kết hợp với việc kiểm tra các giá trị đầu/cuối và cấu trúc dataset, thứ tự `UDI = 1 → 10000` được sử dụng làm experimental stream order.. Dữ liệu hoàn toàn đủ điều kiện để mô hình hóa luồng dữ liệu tuần tự $x_1 \to x_2 \to x_3 \to \dots \to x_{10000}$.

### 4.3. Cell 3 — Kiểm tra kích thước phân đoạn
```python
n = len(df)

train_end = int(n * 0.6)
val_end = int(n * 0.8)

print("Total:", n)
print("Train:", train_end)
print("Validation:", val_end - train_end)
print("Test:", n - val_end)
```
- **Kết quả in ra**:
  - `Total`: 10.000 mẫu
  - `Train`: 6.000 mẫu
  - `Validation`: 2.000 mẫu
  - `Test`: 2.000 mẫu

---

## 5. Thiết kế phân chia dữ liệu: Train / Validation / Test

Dữ liệu được phân chia tuần tự theo tỉ lệ **60% / 20% / 20%** dựa trên experimental stream order:

```text
Dataset: 10,000 samples (UDI: 1 -> 10000, Index: 0 -> 9999)

┌────────────────────────────┬──────────────────────┬────────────────────────────┐
│           TRAIN            │      VALIDATION      │            TEST            │
│            60%             │         20%          │            20%             │
│        6,000 samples       │    2,000 samples     │       2,000 samples        │
│    (UDI: 1 -> 6,000)       │ (UDI: 6,001 -> 8,000)│   (UDI: 8,001 -> 10,000)   │
└────────────────────────────┴──────────────────────┴────────────────────────────┘
0                          6000                   8000                        10000
```

| Phân đoạn | Kích thước (mẫu) | Tỷ lệ (%) | Phạm vi Index | Phạm vi `UDI` |
| :--- | :---: | :---: | :---: | :---: |
| **Train** | 6.000 | 60% | `0` đến `5.999` | `1` đến `6.000` |
| **Validation** | 2.000 | 20% | `6.000` đến `7.999` | `6.001` đến `8.000` |
| **Test** | 2.000 | 20% | `8.000` đến `9.999` | `8.001` đến `10.000` |

### Thống kê bổ sung về nhãn lỗi (`Machine failure`) trên từng tập

| Phân đoạn | Tổng số mẫu | Số mẫu bình thường (0) | Số mẫu lỗi (1) | Tỷ lệ lỗi (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Train** | 6.000 | 5.745 | 255 | 4,25% |
| **Validation** | 2.000 | 1.955 | 45 | 2,25% |
| **Test** | 2.000 | 1.961 | 39 | 1,95% |
| **Toàn bộ dataset** | 10.000 | 9.661 | 339 | 3,39% |

Nhận xét: Mỗi tập phân đoạn đều có sự xuất hiện của các điểm bất thường (`Machine failure = 1`). Tập Train nắm giữ 255 mẫu lỗi đủ lớn để hỗ trợ định hình tri thức mờ ban đầu; tập Validation có 45 mẫu lỗi để tinh chỉnh ngưỡng phân loại; và tập Test có 39 mẫu lỗi đóng vai trò kiểm thử độc lập cho chuỗi luồng bất thường.

---

## 6. Mục đích sử dụng chi tiết của từng phân vùng

### 6.1. Tập Train (6.000 mẫu đầu)
Dùng độc quyền cho việc xây dựng hệ mờ tĩnh ban đầu:
- Xác định miền giá trị (range), min, max và phân bố thống kê để xây dựng các hàm thuộc tính (Membership Functions - MFs).
- Xây dựng hệ thống mờ tĩnh cơ sở (Static Fuzzy System).
- Thiết kế cơ sở tri thức / tập luật mờ ban đầu (Initial Fuzzy Rule Base).

### 6.2. Tập Validation (2.000 mẫu tiếp theo)
Dùng để tối ưu tham số tĩnh trước khi kiểm thử stream:
- Kiểm tra năng lực suy luận của Static Fuzzy System trên dữ liệu chưa học.
- Tinh chỉnh và lựa chọn ngưỡng bất thường tối ưu (Anomaly Threshold Tuning).

### 6.3. Tập Test (2.000 mẫu cuối)
**Nghiêm cấm dùng để thiết kế hoặc tinh chỉnh hệ thống**. Tập Test được đóng băng và giữ nguyên cho giai đoạn thực nghiệm luồng:
- Đánh giá Static Baseline.
- Đánh giá Evolving Fuzzy System.
- Thử nghiệm trên các kịch bản luồng có kiểm soát:
  - Kịch bản **No Drift** (luồng cảm biến nguyên bản).
  - Kịch bản **Sudden Drift** (đột biến phân bố cảm biến).
  - Kịch bản **Gradual Drift** (trôi dạt phân bố dần dần qua thời gian).
- Đưa ra kết luận và so sánh hiệu năng cuối cùng giữa các phương pháp.

---

## 7. Nguyên tắc: Không sử dụng Random `train_test_split`

Một nguyên tắc mang tính then chốt trong dự án này: **Tuyệt đối không sử dụng `train_test_split(df, shuffle=True)` hay bất kỳ hình thức xáo trộn ngẫu nhiên nào cho pipeline chính của bài toán**.

**Lý do khoa học và thực nghiệm:**
1. **Bảo toàn theo thứ tự stream ($x_1 \to x_2 \to \dots \to x_n$):** Xáo trộn dữ liệu ngẫu nhiên sẽ phá hủy hoàn toàn mối liên hệ tuần tự giữa các điểm dữ liệu.
2. **Khả năng diễn giải khi tiêm Concept Drift:** Trong các pha sau, hiện tượng drift sẽ được tạo ra tại các vị trí/mốc thời gian cụ thể trên luồng (ví dụ tiêm drift từ mẫu $x_k$). Nếu dữ liệu bị shuffle, khái niệm "thời điểm bắt đầu drift" và "sự thích ứng theo thời gian của hệ mờ" sẽ không còn ý nghĩa.
3. **Tránh sử dụng thông tin từ các mẫu ở phần sau của stream trong quá trình xây dựng hệ thống:** Nếu lấy mẫu ngẫu nhiên, các mẫu ở tương lai sẽ lọt vào tập huấn luyện, làm méo mó bản chất của bài toán streaming anomaly detection.

---

## 8. Khung đánh giá thử nghiệm công bằng (Fair Benchmark Framework)

Với cấu trúc chia phân đoạn tuần tự như trên, thực nghiệm ở Phase 4 và Phase 5 sẽ được tiến hành theo mô hình:

```text
                     CÙNG MỘT TEST STREAM (SAME TEST STREAM)
                     (2,000 samples: No Drift / Sudden / Gradual)
                                        │
                    ┌───────────────────┴───────────────────┐
                    ↓                                       ↓
           STATIC FUZZY SYSTEM                     EVOLVING FUZZY SYSTEM
         (Cố định hàm thuộc & luật)              (Tự thích nghi hàm thuộc/luật)
                    │                                       │
                    └───────────────────┬───────────────────┘
                                        ↓
                                 SO SÁNH ĐỐI ĐẦU
                     (Precision, Recall, F1, PR-AUC, Latency)
```

Đây là phép so sánh cốt lõi chứng minh giá trị của hệ mờ tự tiến hóa (Evolving Fuzzy Reasoning System): cùng đứng trước một luồng dữ liệu kiểm thử biến đổi, hệ nào thích nghi tốt hơn và duy trì được độ chính xác phát hiện bất thường cao hơn.

---

## 9. Kết luận Phase 1.5

- Đã xác định rõ ràng và chuẩn hóa **Experimental Data Protocol**.
- Đã xác minh tính tăng đơn điệu của `UDI` và phân chia chính xác kích thước 6.000 / 2.000 / 2.000 mẫu trong notebook `01_exploration.ipynb`.
- Đã thống nhất văn phong học thuật giải thích lý do giữ nguyên thứ tự luồng trên tập dữ liệu AI4I 2020.
- Phase 1.5 đã hoàn tất 100%, sẵn sàng làm nền tảng vững chắc để bước sang **Phase 2: Thiết kế Static Fuzzy Inference System**.
