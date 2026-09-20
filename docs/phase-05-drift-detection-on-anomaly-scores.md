# Phase 5 — Phát hiện Trôi dạt trên Luồng Điểm Bất thường của Hệ Mờ (Drift Detection on Anomaly Scores)

## 1. Mục tiêu và Tóm tắt Khoa học

### 1.1. Mục tiêu Cốt lõi
Phase 5 là bước bản lề trong toàn bộ đề tài nghiên cứu, trả lời câu hỏi khoa học mang tính quyết định: 
> *"Liệu hệ thống có khả năng tự phát hiện trực tuyến rằng luồng dữ liệu cảm biến đã bị trôi dạt (concept drift) thông qua chuỗi điểm bất thường của hệ mờ mà không cần sử dụng bất kỳ nhãn giám sát nào hay không?"*

Để bảo đảm tính chặt chẽ và nhất quán của kiến trúc nghiên cứu, Phase 5 thiết lập chuỗi xử lý (pipeline):
```text
Sensor Stream → Static Fuzzy → Anomaly Score A(t) → Drift Detector (ADWIN) → Drift Signal → Evolving Fuzzy → Adaptation
```

Mục tiêu cụ thể:
1. **Lựa chọn tín hiệu giám sát trôi dạt:** Sử dụng trực tiếp chuỗi điểm bất thường $A(t) \in [0, 1]$ sinh ra từ hệ mờ tĩnh Mamdani (đã đóng băng ở Phase 2 và Phase 3) làm tín hiệu duy nhất đưa vào bộ phát hiện trôi dạt.
2. **Thiết kế cơ chế giám sát phi giám sát (Unsupervised Streaming Detection):** Tuyệt đối không sử dụng nhãn mục tiêu `Machine failure` hay thông tin về thời điểm/vùng tiêm trôi dạt trong quá trình phát hiện. Ground truth chỉ được sử dụng ở khâu hậu kiểm để đo lường độ trễ và đánh giá hành vi.
3. **Cách ly môi trường và lựa chọn thuật toán chuẩn mực:** Thiết lập môi trường Python độc lập (`drift_env`, Python 3.11) để tích hợp thuật toán **ADWIN (Adaptive Windowing)** từ thư viện chuẩn `River`, giữ nguyên trạng các phase trước trên môi trường gốc.
4. **Kiểm tra độ tin cậy kỹ thuật (Implementation Sanity Check):** Xác thực ADWIN trên luồng đồ chơi nhân tạo (Toy Test) trước khi đưa vào dữ liệu thực tế.
5. **Đánh giá thực nghiệm đối chứng trên 3 kịch bản luồng (Phase 4):**
   - **Control Stream (No Injected Drift):** Đánh giá tần suất cảnh báo giả (false alarms).
   - **Sudden Drift Stream (Tiêm tại $t = 1000$):** Đo lường độ trễ phát hiện ($\text{Detection Delay}$).
   - **Gradual Drift Stream (Chuyển tiếp $t = 800 \to 1200$):** Khảo sát thời điểm kích hoạt tương quan với cửa sổ chuyển tiếp trôi dạt.
6. **Thiết lập tín hiệu trôi dạt (Drift Signal):** Tạo tiền đề chính thức để kích hoạt cơ chế thích nghi (adaptation) của hệ mờ tự tiến hóa (**Evolving Fuzzy System**) ở các giai đoạn tiếp theo.

> [!IMPORTANT]
> **Nguyên tắc phương pháp luận của Phase 5:**
> - Hệ mờ Static Fuzzy Mamdani (12 luật, hàm thuộc tính và thông số giải mờ) cùng ngưỡng phân loại $\tau = 0.67$ được giữ nguyên vẹn từ Phase 2 & Phase 3.
> - Anomaly Score của cả 3 kịch bản phải được tính toán độc lập từ giá trị cảm biến thực tế của từng luồng; tuyệt đối không tái sử dụng điểm số của Control hay chỉnh sửa điểm số bằng tay.
> - Toàn bộ các file cũ từ Phase 1 đến Phase 4 được niêm phong, không chỉnh sửa hay xóa bỏ.

---

### 1.2. Tuyên bố Tổng kết Khoa học (Executive Scientific Summary)

> *"Sự dịch chuyển phân phối của không gian thuộc tính đầu vào (feature drift trên hai kênh Rotational speed và Torque) đã được chứng minh là lan truyền thành công qua tầng suy luận mờ Mamdani, làm dịch chuyển phân phối điểm bất thường $A(t) \in [0, 1]$ từ mức trung vị danh định $\approx 0.225$ lên mức cảnh báo trung gian $\approx 0.500$ trên cả hai kịch bản Sudden và Gradual Drift mà không xảy ra hiện tượng bão hòa biên.*
> 
> *Thuật toán thích nghi cửa sổ ADWIN (Adaptive Windowing) từ thư viện River được triển khai trên môi trường độc lập (Python 3.11) để theo dõi luồng $A(t)$ theo cơ chế phi giám sát hoàn toàn. Trên luồng đối chứng Control (2.000 mẫu không tiêm trôi dạt), ADWIN không ghi nhận bất kỳ cảnh báo nào (0 detections). Trên kịch bản Sudden Drift, ADWIN kích hoạt tín hiệu trôi dạt tại index 1183, tương ứng với độ trễ phát hiện là 183 mẫu so với điểm tiêm trôi dạt ($t=1000$). Trên kịch bản Gradual Drift, ADWIN kích hoạt tín hiệu phát hiện tại index 1247, tức 47 mẫu sau khi khoảng chuyển tiếp trôi dạt 400 mẫu ($t = 800 \to 1200$) kết thúc.*
> 
> *Kết quả khẳng định tính khả thi của kiến trúc tích hợp: hệ suy diễn mờ đóng vai trò bộ tiền xử lý suy luận không gian đa chiều về một tín hiệu vô hướng $A(t)$, cho phép detector thống kê trực tuyến nhận diện sự thay đổi trạng thái vận hành mà không cần nhãn giám sát lỗi, cung cấp xung kích hoạt tin cậy (Drift Signal) cho động cơ mờ tự tiến hóa."*

---

## 2. Kiến trúc Luồng Xử lý và Phương pháp luận

### 2.1. Sơ đồ Pipeline Tổng thể

```text
       ┌────────────────────────────────────────────────────────┐
       │     SENSOR DATA STREAM (Test partition: 2,000 mẫu)     │
       │     5 biến cảm biến: Air Temp, Process Temp, RPM,      │
       │                      Torque, Tool Wear                 │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │             STATIC MAMDANI FUZZY SYSTEM                │
       │  - 5 biến đầu vào × 3 terms (LOW, MEDIUM, HIGH)        │
       │  - 12 compact rules (4 HIGH, 5 MEDIUM, 3 LOW)          │
       │  - Continuous analytical fuzzification + Min-Max Centroid│
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                ANOMALY SCORE STREAM                    │
       │                   A(t) ∈ [0, 1]                        │
       │      (Unsupervised scalar anomaly representation)       │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │             ONLINE DRIFT DETECTOR: ADWIN               │
       │          - Hoeffding-bound statistical test            │
       │          - Dynamic sliding window maintenance          │
       │          - Không phụ thuộc nhãn Machine failure        │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
                     DRIFT SIGNAL: TRIGGER / NO TRIGGER
                                   │
                                   ▼
                 [ Chuẩn bị cho Evolving Fuzzy Adaptation ]
```

### 2.2. Quyết định Phương pháp luận: Dùng Anomaly Score làm Tín hiệu Giám sát

Thay vì triển khai 5 bộ phát hiện trôi dạt riêng biệt cho từng kênh cảm biến đơn lẻ (dễ dẫn đến xung đột tín hiệu cảnh báo và tăng độ phức tạp tính toán), dự án quyết định đưa trực tiếp chuỗi điểm số **$A(t) \in [0, 1]$** vào ADWIN.

**Ưu điểm khoa học của quyết định này:**
1. **Gắn kết chặt chẽ với bản chất đề tài:** Đề tài tập trung vào hệ mờ suy luận chẩn đoán bất thường. Do đó, việc theo dõi sự thay đổi trong nhận thức trạng thái của hệ mờ phản ánh trực tiếp sự suy giảm hoặc biến thiên trong miền làm việc của hệ thống.
2. **Nén thông tin có ngữ nghĩa (Semantic Dimensionality Reduction):** Hệ mờ 12 luật đã tổng hợp mối tương quan phi tuyến và đa biến giữa 5 kênh cảm biến thành một chỉ số vô hướng mang ý nghĩa vật lý rõ rệt: mức độ rủi ro/bất thường của thiết bị.
3. **Tính phi giám sát thực tế (Zero Supervision):** Trong môi trường công nghiệp thực tế, nhãn hỏng hóc (`Machine failure`) chỉ xuất hiện rất hiếm hoặc có độ trễ lớn sau khi máy đã hư hỏng nặng. Bằng cách chỉ quan sát $A(t)$, hệ thống hoàn toàn tự chủ trong việc phát hiện sự trôi dạt của luồng.

---

## 3. Quản lý Môi trường Thực nghiệm và Cách ly Dependency

### 3.1. Hiện trạng Môi trường Gốc và Rào cản Kỹ thuật
- Toàn bộ Phase 1 đến Phase 4 được phát triển trên môi trường **Anaconda `base` (Python 3.13.9)** trên nền tảng **Windows 11 Build 26200**.
- Khi tiến hành cài đặt thư viện luồng `river` (phiên bản `0.26.1`) trên Python 3.13, module mở rộng biên dịch Rust `_river_rust.pyd` đã bị chính sách bảo mật hệ thống **Windows Defender Application Control (WDAC) / Smart App Control** chặn thực thi với thông báo:
  ```text
  ImportError: DLL load failed while importing _river_rust: An Application Control policy has blocked this file.
  ```

### 3.2. Giải pháp Cách ly Môi trường (`drift_env`)
Để tuân thủ tuyệt đối nguyên tắc **không làm thay đổi hay gây rủi ro cho các phase trước**, dự án quyết định không can thiệp vào policy bảo mật của hệ điều hành, mà khởi tạo một môi trường Conda độc lập:

```text
Anaconda base (Python 3.13) ────────► [ ĐÓNG BĂNG, GIỮ NGUYÊN ] ────► Phase 1 – 4
                                                                          │
Conda drift_env (Python 3.11) ──────► [ MÔI TRƯỜNG ĐỘC LẬP MỚI ] ───► Phase 5
  - Python 3.11.16
  - NumPy 2.4.6, SciPy 1.17.1, Pandas 3.0.6, Scikit-Fuzzy 0.5.0
  - River 0.26.1 (ADWIN chuẩn)
  - Kernelspec: Python (drift_env)
```

- **Kết quả kiểm tra kernel Phase 5 (Cell 5.2.0):**
  - Python executable: `C:\Users\vinhv\anaconda3\envs\drift_env\python.exe`
  - Phiên bản: `Python 3.11.16`
  - Thư viện: `River 0.26.1`, `NumPy 2.4.6`, `ADWIN` nạp và khởi tạo thành công 100%, không bị policy chặn.

---

## 4. Chi tiết Triển khai và Kết quả Thực nghiệm Từng Phân đoạn

### 4.1. Phase 5.1 — Chuẩn bị Anomaly-Score Stream (Cell 5.1.1)

#### 4.1.1. Triển khai Tính toán
Hàm tính toán điểm số tĩnh được áp dụng trên toàn bộ 2.000 mẫu của cả 3 kịch bản:
```python
def score_stream(df):
    return np.array([
        mamdani_inference(row)
        for _, row in df.iterrows()
    ])
```

#### 4.1.2. Kết quả Thực nghiệm Định lượng
```text
Control:      Number of scores: 2000 | Min: 0.0000 | Max: 0.6898 | Mean: 0.315161
Sudden Drift: Number of scores: 2000 | Min: 0.1944 | Max: 0.6898 | Mean: 0.381982
Gradual Drift:Number of scores: 2000 | Min: 0.1944 | Max: 0.6898 | Mean: 0.382425
```

#### 4.1.3. Khảo sát Phân phối Chi tiết và Hiện tượng Lan truyền Drift

Khảo sát sâu phân phối điểm số trước và sau mốc trôi dạt:

| Kịch bản Luồng | Tỷ lệ $A(t) = 0$ | Vùng đáy ($\le 0.20$) | Vùng đỉnh ($\ge 0.68$) | Phân đoạn Trước Drift | Phân đoạn Sau Drift |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Control** | 1 mẫu ($0.05\%$) | 165 mẫu ($8.25\%$) | 31 mẫu ($1.55\%$) | Mean = $0.3152$, Med = $0.2249$ | *(Toàn chuỗi đối chứng)* |
| **Sudden Drift** | 0 mẫu ($0.00\%$) | 120 mẫu ($6.00\%$) | 93 mẫu ($4.65\%$) | **Mean = 0.3159, Med = 0.2249** | **Mean = 0.4480, Med = 0.5000** |
| **Gradual Drift** | 0 mẫu ($0.00\%$) | 120 mẫu ($6.00\%$) | 90 mẫu ($4.50\%$) | **Mean = 0.3200, Med = 0.2251** | **Mean = 0.4535, Med = 0.5000** |

> [!NOTE]
> **Diễn giải Khoa học:**
> 1. **Không nghẽn biên (No Saturation):** Điểm số trải dài từ $0.1944$ đến $0.6898$, tỷ lệ dồn sát hai biên cực đoan rất nhỏ ($<10\%$).
> 2. **Bằng chứng lan truyền trôi dạt (Drift Propagation):** Trước drift, điểm số nằm ổn định tại vùng danh định ($Med \approx 0.225$). Sau khi trôi dạt cơ học diễn ra, giá trị trung vị nhảy vọt lên đúng mức **$0.5000$** (kích hoạt mức đỉnh của tập mờ Anomaly $MEDIUM$), làm giá trị trung bình tăng từ $\approx 0.316$ lên $\approx 0.450$. Điều này chứng minh trôi dạt cảm biến đã chuyển hóa thành sự dịch chuyển phân phối có ý nghĩa trong không gian điểm bất thường.

---

### 4.2. Phase 5.2 — Kiểm định Kỹ thuật: ADWIN Toy Test (Cell 5.2.1)

Trước khi đưa vào luồng dữ liệu thực tế AI4I, thuật toán `ADWIN` từ `River` được kiểm định độ tin cậy thông qua một chuỗi điểm số nhân tạo gồm 1.000 mẫu:
- **500 mẫu đầu ($0 \to 499$):** Phân phối chuẩn $\mathcal{N}(\mu=0.20, \, \sigma=0.02)$.
- **500 mẫu sau ($500 \to 999$):** Bước nhảy phân phối lên $\mathcal{N}(\mu=0.60, \, \sigma=0.02)$.

```python
detector = ADWIN()
detections = []
for i, score in enumerate(toy_stream):
    detector.update(score)
    if detector.drift_detected:
        detections.append(i)
```

**Kết quả thực nghiệm:**
```text
Toy stream length: 1000
Expected drift region: around index 500
Detected drift indices: [543]
```
- **Nhận xét:** ADWIN không phát ra bất kỳ cảnh báo giả nào trong 500 mẫu đầu, và kích hoạt phát hiện trôi dạt tại mẫu **`543`** khi thu thập đủ mẫu thống kê. Thử nghiệm này xác nhận việc cài đặt và giao tiếp thuật toán của ADWIN hoàn toàn hợp lệ.

---

### 4.3. Phase 5.3 — ADWIN trên Kịch bản Control Stream (Cell 5.3.1)

Kịch bản Control gồm 2.000 mẫu gốc của phân vùng Test, phản ánh phân phối tự nhiên của tập dữ liệu và không bị tiêm bất kỳ trôi dạt nhân tạo nào.

```python
control_detector = ADWIN()
control_detections = []
for i, score in enumerate(control_scores):
    control_detector.update(float(score))
    if control_detector.drift_detected:
        control_detections.append(i)
```

**Kết quả thực nghiệm:**
```text
Scenario: Control
========================================
Stream length: 2000
Detected drift indices: []
Number of detections: 0
```

> [!TIP]
> **Đánh giá Phương pháp luận:**
> - Trong suốt 2.000 mẫu của kịch bản Control, ADWIN ghi nhận **0 lần phát hiện** (`Detections: []`).
> - Kết quả này chứng minh rằng trên kịch bản Control cụ thể của bài toán, các biến động ngẫu nhiên và nhiễu nội tại của chuỗi điểm $A(t)$ không vượt qua ngưỡng chặn thống kê của ADWIN, không làm phát sinh cảnh báo giả ngoài ý muốn.

---

### 4.4. Phase 5.4 — ADWIN trên Kịch bản Sudden Drift (Cell 5.4.1)

Kịch bản Sudden Drift áp dụng mức dịch chuyển tức thời $-150\text{ rpm}$ và $+8\text{ Nm}$ bắt đầu từ mốc $t = 1000$.

```python
sudden_detector = ADWIN()
sudden_detections = []
for i, score in enumerate(sudden_scores):
    sudden_detector.update(float(score))
    if sudden_detector.drift_detected:
        sudden_detections.append(i)
```

**Kết quả thực nghiệm:**
```text
Scenario: Sudden Drift
========================================
Stream length: 2000
True injected drift index: 1000
Detected drift indices: [1183]
Number of detections: 1
```

> [!NOTE]
> **Đánh giá Định lượng:**
> 1. **Tính đơn nhất:** ADWIN chỉ kích hoạt duy nhất **1 lần** trong toàn bộ chuỗi 2.000 mẫu.
> 2. **Không có cảnh báo sớm:** Trong đoạn $0 \to 999$ trước mốc tiêm trôi dạt, không có tín hiệu cảnh báo nào xuất hiện.
> 3. **Độ trễ phát hiện (Detection Delay):**
>    $$\text{Detection Delay} = t_{\text{detected}} - t_{\text{true}} = 1183 - 1000 = 183 \text{ mẫu}$$
>    ADWIN cần quan sát 183 mẫu mang phân phối mới để tích lũy đủ độ lệch thống kê giữa hai cửa sổ con trước khi kích hoạt cờ trôi dạt. Sau mốc 1183, ADWIN tự thích nghi cửa sổ theo phân phối mới và không phát sinh thêm cảnh báo dư thừa nào.

---

### 4.5. Phase 5.5 — ADWIN trên Kịch bản Gradual Drift (Cell 5.5.1)

Kịch bản Gradual Drift biến đổi tuyến tính qua cửa sổ 400 mẫu từ $t = 800$ đến $t = 1200$, đạt mức trôi dạt cực đại tại $t = 1200$.

```python
gradual_detector = ADWIN()
gradual_detections = []
for i, score in enumerate(gradual_scores):
    gradual_detector.update(float(score))
    if gradual_detector.drift_detected:
        gradual_detections.append(i)
```

**Kết quả thực nghiệm:**
```text
Scenario: Gradual Drift
========================================
Stream length: 2000
Transition start: 800
Transition end: 1200
Detected drift indices: [1247]
Number of detections: 1
```

> [!NOTE]
> **Đánh giá Định lượng:**
> 1. **Tính đơn nhất:** Kích hoạt duy nhất **1 lần** trong toàn chuỗi.
> 2. **Không có cảnh báo sớm:** Không phát hiện trôi dạt trước mốc $t = 800$.
> 3. **Thời điểm kích hoạt tương quan:** 
>    ADWIN kích hoạt tín hiệu tại index **`1247`**, tức **47 mẫu sau khi khoảng chuyển tiếp trôi dạt kết thúc** ($1247 - 1200 = 47$). 
>    Do đặc tính trôi dạt tiệm tiến, trong khoảng $800 \to 1200$, phân phối dịch chuyển từ từ khiến chênh lệch kỳ vọng giữa các cửa sổ con tích lũy chậm hơn so với cú nhảy đột ngột. Chỉ khi trạng thái phân phối mới định hình đầy đủ sau mốc 1200, thử nghiệm thống kê mới đạt mức ý nghĩa để kích hoạt tín hiệu.

---

### 4.6. Phase 5.6 — Tổng hợp và Đối chiếu Toàn diện (Cell 5.6.1)

Bảng tổng hợp kết quả chính thức của Phase 5:

| Kịch bản Thực nghiệm | Đặc tả Vùng Trôi dạt Ground Truth | Danh sách Index Phát hiện | Số lần Phát hiện | Quan hệ Thời gian Thực nghiệm |
| :--- | :---: | :---: | :---: | :--- |
| **Control** | Không can thiệp (*None*) | `[]` | **0 lần** | Không có cảnh báo giả trong 2.000 mẫu đối chứng |
| **Sudden Drift** | Bước nhảy tại $t = 1000$ | `[1183]` | **1 lần** | Phát hiện trễ 183 mẫu so với điểm tiêm trôi dạt |
| **Gradual Drift** | Quá độ $t = 800 \to 1200$ | `[1247]` | **1 lần** | Phát hiện tại 1247 (47 mẫu sau khi kết thúc chuyển tiếp) |

---

## 5. Thảo luận Khoa học và Nhận xét Phương pháp luận

### 5.1. Cơ chế Lan truyền và Tính Bảo toàn Thông tin
Thực nghiệm xác nhận rằng quá trình suy diễn mờ Mamdani với 12 luật compact không làm triệt tiêu hay làm mờ đi các tín hiệu trôi dạt vật lý từ cảm biến. Trái lại, việc tổng hợp các kích hoạt luật thành một Anomaly Score liên tục đã tạo ra một tín hiệu theo dõi có độ phân giải cao, giúp thuật toán cửa sổ thích nghi nhận diện rõ ràng ranh giới phân phối.

### 5.2. Bản chất Phi giám sát (Unsupervised)
Trong toàn bộ quá trình chạy ADWIN:
- Không có bất kỳ nhãn `Machine failure` nào được đưa vào detector.
- ADWIN hoàn toàn không được lập trình trước về các mốc $t=1000$ hay khoảng $800 \to 1200$.
Việc thuật toán phát hiện trôi dạt hoàn toàn độc lập và khách quan chứng minh tính thực tiễn cao của kiến trúc khi triển khai trên các hệ thống quan trắc cảm biến công nghiệp thực tế.

### 5.3. Giới hạn Khoa học Cần Lưu ý
1. **Tính chất trên kịch bản cụ thể:** Các con số độ trễ 183 mẫu (Sudden) và 47 mẫu sau chuyển tiếp (Gradual) là kết quả quan sát được trên các kịch bản thực nghiệm cụ thể của bộ dữ liệu AI4I 2020 với cấu hình ADWIN mặc định, không phải là phát biểu khái quát cho mọi bài toán trôi dạt.
2. **Khác biệt về bản chất giữa Sudden và Gradual:** Không thể suy luận rằng "ADWIN phát hiện Gradual tốt hơn Sudden" chỉ vì con số 47 nhỏ hơn 183. Cơ chế trôi dạt tiệm tiến đã trải qua 400 mẫu quá độ trước khi chạm ngưỡng phát hiện, trong khi Sudden là một cú sốc phân phối tức thời. Hai cơ chế phản ánh hai bài toán động học khác nhau của môi trường vận hành.

---

## 6. Kết luận và Định hướng Chuyển tiếp sang Phase 6

### 6.1. Đóng Phase 5
- Phase 5 đã hoàn thành trọn vẹn toàn bộ 6 mục tiêu phương pháp luận (`5.1` $\to$ `5.6`) trong notebook độc lập [`notebooks/05_drift_detection.ipynb`](file:///notebooks/05_drift_detection.ipynb) trên môi trường chuẩn `Python (drift_env)`.
- Toàn bộ các tài nguyên và mã nguồn cũ từ Phase 1 đến Phase 4 được bảo toàn nguyên vẹn 100%.
- Câu hỏi cốt lõi của Phase 5 đã được giải quyết: **Hệ thống hoàn toàn có khả năng phát hiện sự thay đổi phân phối của luồng dữ liệu thông qua Anomaly Score của hệ mờ tĩnh theo cơ chế phi giám sát.**

### 6.2. Định hướng Chuyển tiếp sang Phase 6 (Evolving Fuzzy Reasoning System)
Với tín hiệu trôi dạt (**Drift Signal**) đã được kiểm chứng tin cậy từ ADWIN, Phase 6 sẽ chính thức kích hoạt cơ chế tự thích nghi (**Adaptation Mechanism**):
1. **Thiết kế Động cơ Mờ Tự tiến hóa (Evolving FIS Engine):**
   - Khi nhận được tín hiệu `drift_detected = True` tại mốc thời gian $t$, hệ thống chuyển sang chế độ thích nghi.
2. **Chiến lược Thích nghi Hàm Thuộc tính (MF Adaptation):**
   - Cập nhật lại tâm và biên của các hàm thuộc tính cho các biến cảm biến cơ học (Rotational speed và Torque) dựa trên thống kê cửa sổ dữ liệu mới.
3. **Cơ chế Điều chỉnh hoặc Bổ sung Luật Mờ (Rule Base Updating):**
   - Đánh giá lại mức độ kích hoạt và tái cấu trúc các luật mờ bị ảnh hưởng bởi trôi dạt.
4. **Đối chuẩn Hiệu năng Đối đầu (Static vs. Evolving Baseline):**
   - Đo lường mức độ phục hồi các chỉ số phân loại ($F_1$-score, Precision, Recall) của hệ mờ tự tiến hóa so với hệ mờ tĩnh bị suy giảm trên cả 3 kịch bản stream.
