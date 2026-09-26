# Phase 13 (Bonus) — Multistream và Cross-stream Knowledge Transfer

## 1. Kịch bản

- Notebook: [`notebooks/13_multistream_transfer.ipynb`](../notebooks/13_multistream_transfer.ipynb), module `src/multistream.py`
- Kết quả: `results/13_multistream.csv`. Hình: `figures/13_multistream_machine_c.png`

Một "đội" 3 máy được giám sát song song trên cùng đồng hồ. Mỗi máy có FIS, ADWIN và buffer riêng. Cả 3 chịu **cùng một thay đổi môi trường** (RPM −150, Torque +8) nhưng ở các thời điểm khác nhau. Knowledge base dùng chung lưu **vector độ dịch MF** (không nhãn) của máy đầu tiên thích nghi xong. Chế độ:

- `independent`: mỗi máy làm như Phase 7.
- `transfer`: khi máy tự phát hiện drift, nó áp dụng **ngay** vector của máy khác, rồi vẫn thu buffer 200 mẫu của mình để tinh chỉnh phần dư.
- `transfer_only`: chỉ áp dụng vector được chuyển (ablation).

> [!WARNING]
> **Giới hạn dữ liệu:** chỉ đoạn Test (UDI 8001–10000) là dữ liệu chưa thấy. Máy B dùng UDI 6001–8000 (Validation) và máy C dùng UDI 4001–6000 (Train, chứa toàn bộ lỗi HDF: 154 ca lỗi). Vì vậy **F1/FPR tuyệt đối của B và C lạc quan và không so được với A**. Chỉ so sánh **giữa các chế độ trên cùng một máy**. Kịch bản đội máy và drift lệch pha là **mô phỏng**, không có trong dữ liệu gốc.

## 2. Kết quả

### 2.1. Cùng drift, onset lệch nhau đủ xa (A = 800, B = 1100, C = 1400)

Máy A thích nghi xong ở t = 1127 và trở thành nguồn tri thức.

| Máy | Chế độ | Phát hiện | Thích nghi lần đầu | Onset → thích nghi | FP sau onset | TP sau onset | F1 | FPR |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B | independent | 1183 | 1383 | 283 | 56 | 7 | 0.178 | 0.040 |
| B | **transfer** | 1183 | **1183** | **83** | **46** | 7 | **0.192** | **0.035** |
| B | transfer_only | 1183 | 1183 | 83 | 65 | 10 | 0.204 | 0.045 |
| C | independent | 1503 | 1703 | 303 | 113 | 9 | 0.360 | 0.080 |
| C | **transfer** | 1503 | **1503** | **103** | **59** | 8 | **0.417** | **0.050** |
| C | transfer_only | 1503 | 1503 | 103 | 68 | 9 | 0.410 | 0.055 |

Máy A không đổi giữa các chế độ (F1 0.286, FPR 0.029), vì nó là máy thích nghi đầu tiên.

- Transfer rút ngắn thời gian từ onset đến lúc thích nghi **đúng W = 200 mẫu** (283 → 83; 303 → 103), vì không phải chờ buffer riêng.
- Số FP sau onset giảm 18% ở B (56 → 46) và 48% ở C (113 → 59), đổi lại C mất 1 TP (9 → 8).
- `transfer_only` bắt được nhiều TP hơn ở B nhưng FP cũng nhiều hơn so với `transfer`. Tinh chỉnh bằng buffer riêng giúp giảm FP.

### 2.2. Onset quá sát nhau (A = 1000, B = 1100, C = 1200)

B phát hiện ở t = 1183 và C ở t = 1279, **trước khi** A thích nghi xong (t = 1383). Knowledge base còn trống nên transfer **tự rơi về independent**, và kết quả ba chế độ trùng nhau. Lợi ích của transfer chỉ có khi các máy bị ảnh hưởng *lệch nhau hơn độ trễ phát hiện + W* của máy nguồn.

### 2.3. Thử negative transfer: C chỉ có drift Torque, RPM không đổi

| Máy C | Phát hiện | Thích nghi lần đầu | FP sau onset | TP sau onset | F1 | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| independent | 1631 | 1831 | 72 | 8 | 0.400 | 0.057 |
| transfer | 1631 | 1631 (ΔRPM sai ≈ −150 được áp dụng) | 40 | 7 | 0.438 | 0.040 |
| transfer_only | 1631 | 1631 | 38 | 7 | 0.441 | 0.039 |

**Kết quả trái trực giác, cần diễn giải cẩn thận:** tri thức chuyển sang C là *sai về RPM*, nhưng F1 lại tăng. Lý do: dịch MF RPM xuống khoảng 150 rpm khiến điều kiện "RPM is LOW" khó thỏa mãn hơn, nên các luật R1, R3–R6 kích hoạt ít đi. Hệ thống trở nên **kém nhạy hơn nói chung** (TP 8 → 7), và vì precision nền rất thấp nên giảm cảnh báo lại làm F1 tăng. Như vậy **không quan sát được tác hại về metric, nhưng tri thức vẫn sai về mặt ngữ nghĩa**: trong ít nhất 200 mẫu, khái niệm "RPM LOW" của máy C bị lệch. Không được diễn giải kết quả này thành "transfer luôn an toàn".

## 3. Kết luận Phase 13

1. Chia sẻ vector độ dịch không nhãn giữa các máy **rút ngắn thời gian thích nghi đúng bằng W** và giảm FP sau drift ở các máy nhận tri thức, trong kịch bản mô phỏng khi drift giống nhau.
2. Lợi ích phụ thuộc vào độ lệch thời gian giữa các máy. Khi drift đến gần như đồng thời, transfer không có tác dụng.
3. Khi drift giữa các máy khác nhau, tri thức chuyển sang có thể sai ngữ nghĩa mà metric không phản ánh. Cần một bước kiểm tra tương thích trước khi áp dụng (ví dụ so hướng dịch của buffer ngắn với vector được chuyển). Bước này chưa được cài đặt.
