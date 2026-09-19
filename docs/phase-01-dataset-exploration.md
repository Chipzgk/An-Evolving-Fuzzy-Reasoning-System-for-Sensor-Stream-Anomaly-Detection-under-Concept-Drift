# Phase 1 - Khám phá và hiểu dữ liệu

## 1. Mục tiêu

Phase 1 có mục tiêu kiểm tra cấu trúc, chất lượng và đặc điểm ban đầu của
AI4I 2020 Predictive Maintenance Dataset trước khi xây dựng bất kỳ thành phần
fuzzy nào.

Nguồn dữ liệu chính thức:
<https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset>

Lưu ý quan trọng: AI4I 2020 là bộ dữ liệu predictive maintenance tổng hợp. Bản
thân bộ dữ liệu này không phải là benchmark concept drift tự nhiên. Vì vậy,
concept drift sẽ được thiết kế thành kịch bản streaming có kiểm soát ở các
phase sau.

## 2. Tài nguyên và cách chạy

- Tệp dữ liệu: `data/ai4i2020.csv`
- Notebook: `notebooks/01_exploration.ipynb`
- Môi trường đã dùng: Python 3.11.15, NumPy 2.1.3, Pandas 2.2.3,
  Matplotlib 3.11.0, Seaborn 0.13.2.

## 3. Cấu trúc dữ liệu

Dataset có **10.000 dòng và 14 cột**.

| Nhóm | Cột |
| --- | --- |
| Định danh | `UDI`, `Product ID` |
| Phân loại sản phẩm | `Type` (L, M, H) |
| Biến cảm biến/vận hành | `Air temperature [K]`, `Process temperature [K]`, `Rotational speed [rpm]`, `Torque [Nm]`, `Tool wear [min]` |
| Nhãn mục tiêu | `Machine failure` |
| Nhãn chế độ lỗi | `TWF`, `HDF`, `PWF`, `OSF`, `RNF` |

`Machine failure` là nhãn nhị phân: giá trị 1 nghĩa là máy bị lỗi, giá trị 0
nghĩa là máy không bị lỗi.

## 4. Kiểm tra chất lượng dữ liệu

- Giá trị thiếu: **0** trên tất cả 14 cột.
- Dòng trùng lặp hoàn toàn: **0**.
- Kiểu dữ liệu phù hợp: các biến cảm biến là số (`int64`/`float64`), còn
  `Type` và `Product ID` là text.

Kết luận: Phase 2 không cần đặt trọng tâm vào xử lý missing value hoặc loại bỏ
duplicate, vì dữ liệu đầu vào đã sạch ở mức cơ bản.

## 5. Phân bố nhãn và ý nghĩa

| Lớp `Machine failure` | Số mẫu | Tỷ lệ |
| --- | ---: | ---: |
| 0 - bình thường | 9.661 | 96,61% |
| 1 - lỗi máy | 339 | 3,39% |

Dữ liệu bị lệch lớp mạnh. Vì vậy, accuracy đơn thuần không nên được dùng làm
metric chính ở phase đánh giá sau. Các metric phù hợp hơn gồm precision,
recall, F1, PR-AUC hoặc các metric chuyên cho anomaly detection.

Số lần xuất hiện của các chế độ lỗi:

| Chế độ lỗi | Số dòng được đánh dấu |
| --- | ---: |
| HDF | 115 |
| OSF | 98 |
| PWF | 95 |
| TWF | 46 |
| RNF | 19 |

Các cột `TWF`, `HDF`, `PWF`, `OSF`, `RNF` là thông tin nhãn hoặc nguyên nhân
lỗi, không phải tín hiệu cảm biến có sẵn tại thời điểm suy luận. Vì vậy, không
được đưa các cột này vào input của mô hình, nếu không sẽ gây label leakage.

Kiểm tra bổ sung:

- 348 dòng có ít nhất một chế độ lỗi được đánh dấu.
- 24 dòng có hơn một chế độ lỗi.
- 9 dòng có `Machine failure = 1` nhưng không có chế độ lỗi nào được đánh dấu.
- 18 dòng có chế độ lỗi được đánh dấu nhưng `Machine failure = 0`.

Do đó, tổng số lần xuất hiện của các chế độ lỗi không cần và không nên bằng
tổng số mẫu có `Machine failure = 1`.

## 6. Thống kê mô tả các tín hiệu cảm biến

| Đặc trưng | Mean | Std | Min | Median | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| Air temperature [K] | 300,00 | 2,00 | 295,3 | 300,1 | 304,5 |
| Process temperature [K] | 310,01 | 1,48 | 305,7 | 310,1 | 313,8 |
| Rotational speed [rpm] | 1538,78 | 179,28 | 1168 | 1503 | 2886 |
| Torque [Nm] | 39,99 | 9,97 | 3,8 | 40,1 | 76,6 |
| Tool wear [min] | 107,95 | 63,65 | 0 | 108 | 253 |

Hai biến nhiệt độ có biên độ dao động khá hẹp. Trong khi đó, tốc độ quay,
torque và tool wear có biên độ rộng hơn, nên có tiềm năng tạo ra các miền
fuzzy dễ diễn giải hơn.

## 7. Liên hệ với nhãn lỗi

Tương quan Pearson giữa 5 biến cảm biến và `Machine failure`:

| Đặc trưng | Tương quan |
| --- | ---: |
| Torque [Nm] | 0,1913 |
| Tool wear [min] | 0,1054 |
| Air temperature [K] | 0,0826 |
| Process temperature [K] | 0,0359 |
| Rotational speed [rpm] | -0,0442 |

Các hệ số tương quan đơn biến đều không lớn, nên không nên loại bỏ đặc trưng
chỉ dựa vào bảng này. Hệ fuzzy có thể khai thác tương tác giữa nhiệt độ, tốc
độ quay, torque và độ mòn dụng cụ.

Quan sát theo lớp cho thấy các mẫu lỗi có torque trung bình 50,17 Nm, trong
khi các mẫu bình thường có torque trung bình 39,63 Nm. Tool wear trung bình ở
mẫu lỗi là 143,78 phút, cao hơn mức 106,69 phút ở mẫu bình thường. Đây là hai
tín hiệu ban đầu đáng chú ý, nhưng chưa phải là fuzzy rule.

## 8. Quyết định đầu vào cho phase tiếp theo

Giữ lại 5 biến sau làm ứng viên đầu vào fuzzy:

1. `Air temperature [K]`
2. `Process temperature [K]`
3. `Rotational speed [rpm]`
4. `Torque [Nm]`
5. `Tool wear [min]`

Không dùng làm đầu vào mô hình:

- `Machine failure`: nhãn mục tiêu.
- `TWF`, `HDF`, `PWF`, `OSF`, `RNF`: nhãn chế độ lỗi; đưa vào input sẽ gây
  label leakage.
- `UDI`, `Product ID`: biến định danh, không mang ý nghĩa cảm biến.

`Type` tạm thời không đưa vào fuzzy core ban đầu. Đây là biến phân loại sản
phẩm, có thể đánh giá sau như một biến bối cảnh. Tỷ lệ lỗi quan sát theo
`Type` là L 3,92%, M 2,77%, H 2,09%.

## 9. Kết luận Phase 1

Phase 1 **đã hoàn thành**. Dataset sạch, có nhãn anomaly rõ ràng, và 5 biến
cảm biến đã được chốt làm bộ ứng viên đầu vào. Trong phase này chưa xây dựng
fuzzy rule, streaming pipeline hay cơ chế concept drift.

Phase tiếp theo chỉ nên bắt đầu sau khi xác định rõ quy ước chia dữ liệu và
thứ tự stream để tránh leakage theo thời gian.
