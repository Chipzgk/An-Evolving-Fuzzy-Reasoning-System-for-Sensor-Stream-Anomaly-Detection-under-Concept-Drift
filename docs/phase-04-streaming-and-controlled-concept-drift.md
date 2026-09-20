# Phase 4 — Thiết kế Luồng Dữ liệu và Các Kịch bản Trôi dạt Cảm biến có Kiểm soát (Streaming & Controlled Drift Scenarios)

## 1. Mục tiêu và Tóm tắt Khoa học

### 1.1. Mục tiêu Cốt lõi
Phase 4 đóng vai trò xây dựng một **giao thức luồng dữ liệu thực nghiệm sạch (Clean Experimental Streaming Protocol)**, nhằm chuẩn bị môi trường đối chuẩn công bằng (fair benchmark) cho giai đoạn so sánh giữa hệ mờ tĩnh (**Static Fuzzy Baseline**) và hệ mờ thích nghi (**Evolving Fuzzy System**). 

Mục tiêu cụ thể:
1. **Thiết lập Base Stream** từ phân vùng Test độc lập ($UDI: 8001 \to 10000$, 2.000 mẫu) theo đúng Giao thức Dữ liệu Thử nghiệm đã xác lập tại Phase 1.5.
2. **Định nghĩa kịch bản Control (No Injected Drift)** làm mốc đối chứng nguyên bản, phản ánh đúng đặc tính phân phối tự nhiên của tập dữ liệu.
3. **Thiết kế kịch bản Sudden Drift (Trôi dạt đột ngột)** có kiểm soát, xác định thời điểm và cường độ dịch chuyển dựa trên cơ sở thống kê thực nghiệm.
4. **Thiết kế kịch bản Gradual Drift (Trôi dạt tiệm tiến)** với cùng cường độ dịch chuyển cực đại và cùng trạng thái biên ổn định, nhưng chuyển tiếp tuyến tính qua một cửa sổ thời gian xác định.
5. **Xác thực toàn vẹn và kiểm định thống kê đa mức** nhằm bảo đảm:
   - Nhãn thực tế (`Machine failure`) và thứ tự tuần tự (`UDI`) được bảo toàn nguyên vẹn $100\%$ trên mọi kịch bản.
   - Chỉ có các kênh cảm biến được chỉ định bị can thiệp, không gây rò rỉ hay sai lệch ngoài ý muốn sang các kênh cảm biến khác.

> [!IMPORTANT]
> **Phạm vi phương pháp luận của Phase 4:**
> - Trong Phase 4, hệ thống **chưa kích hoạt cơ chế tự tiến hóa (Evolving Fuzzy)** và **chưa tích hợp bộ phát hiện trôi dạt (Drift Detector)**. 
> - Toàn bộ trọng tâm là tạo ra các bản sao luồng dữ liệu chuẩn hóa từ Test stream gốc để phục vụ kiểm thử đối đầu ở các giai đoạn sau.
> - Tuyệt đối không can thiệp hay chỉnh sửa tệp dữ liệu gốc `data/ai4i2020.csv`.

---

### 1.2. Tuyên bố Tổng kết Khoa học (Executive Scientific Summary)

> *"Dựa trên kết quả khảo sát dịch chuyển phân phối tự nhiên ở Phase 3, ba kịch bản luồng dữ liệu kiểm thử độc lập đã được thiết kế từ phân vùng Test tuần tự ($UDI: 8001 \to 10000$, 2.000 mẫu): Control (No Injected Drift), Sudden Drift và Gradual Drift.*
> 
> *Để cô lập tác động của trôi dạt nhân tạo khỏi các biến thiên môi trường vốn có của bộ dữ liệu, hai cảm biến cơ học gồm Rotational speed và Torque được lựa chọn làm kênh tiêm trôi dạt. Kịch bản Sudden Drift áp dụng mức dịch chuyển đột ngột $-150\text{ rpm}$ ($\approx 0.91\sigma$) và $+8\text{ Nm}$ ($\approx 0.83\sigma$) tại mốc index 1000. Kịch bản Gradual Drift áp dụng cùng mức dịch chuyển cực đại nhưng chuyển tiếp tuyến tính qua cửa sổ 400 mẫu (index 800 đến 1199).*
> 
> *Kiểm định Kolmogorov-Smirnov (KS-test) hai mẫu xác nhận sự khác biệt phân phối có ý nghĩa thống kê của không gian đặc trưng đầu vào $P(X)$ đối với RPM ($D \approx 0.43, p < 10^{-65}$) và Torque ($D \approx 0.31, p < 10^{-36}$) qua ranh giới trôi dạt trên cả hai kịch bản, trong khi cảm biến đối chứng Tool wear không quan sát thấy sự khác biệt phân phối có ý nghĩa thống kê ($p > 0.70$). Toàn bộ nhãn mục tiêu Machine failure (39 ca lỗi) và chỉ số UDI được bảo toàn đồng nhất 100% giữa ba kịch bản, thiết lập nền tảng đối chuẩn khách quan cho các thực nghiệm thích nghi tiếp theo."*

---

## 2. Kiến trúc Phân nhánh Kịch bản Dữ liệu (Scenario Branching Architecture)

Để đảm bảo tính khách quan và khả năng tái lập, các kịch bản luồng được sinh ra theo sơ đồ phân nhánh độc lập:

```text
                       ORIGINAL TEST STREAM
                     (UDI: 8001 → 10000, 2000 mẫu)
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
   Phase 4.2:                Phase 4.3:                Phase 4.4:
CONTROL STREAM           SUDDEN DRIFT STREAM       GRADUAL DRIFT STREAM
(No Injected Drift)      (Đột biến tại t = 1000)   (Chuyển tiếp t = 800 → 1200)
- Giữ nguyên 100%        - RPM: -150 rpm           - RPM: 0 → -150 rpm
- Label gốc (39 lỗi)     - Torque: +8 Nm           - Torque: 0 → +8 Nm
- Clipping: N/A          - Label gốc (39 lỗi)      - Label gốc (39 lỗi)
                         - Clipped theo Universe   - Clipped theo Universe
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                                   ▼
                             Phase 4.5:
                 CROSS-SCENARIO INTEGRITY CHECK
           (Bảo toàn UDI, Label, Sensor Isolation)
```

---

## 3. Chi tiết Triển khai Từng Giai đoạn

### 3.1. Phase 4.1 — Tạo Base Stream (`stream_df`)

Base stream được trích xuất tuần tự từ 2.000 dòng cuối của tệp dữ liệu `data/ai4i2020.csv` và đặt lại chỉ số index về dải liên tục `0 → 1999`:

```python
# Trích xuất Test set theo Sequential Split Protocol (Phase 1.5)
test_df = df.iloc[8000:].copy()
stream_df = test_df.copy().reset_index(drop=True)
```

**Kết quả xác thực thực nghiệm (Cell 4.1):**
- **Tổng số mẫu:** $2.000$ mẫu.
- **Phạm vi `UDI`:** $8001 \to 10000$.
- **Phạm vi `index`:** $0 \to 1999$.
- **Tính đơn điệu:** `stream_df["UDI"].is_monotonic_increasing = True`.
- **5 biến cảm biến đầu vào:** `Air temperature [K]`, `Process temperature [K]`, `Rotational speed [rpm]`, `Torque [Nm]`, `Tool wear [min]`.

---

### 3.2. Phase 4.2 — Kịch bản Control (`control_stream`)

#### 3.2.1. Chuẩn hóa thuật ngữ học thuật
Dự án thống nhất sử dụng tên gọi **Control (No Injected Drift)** thay vì "No Drift" đơn thuần. Lý do khoa học:
- Tại Phase 3, các kiểm định Kolmogorov-Smirnov đã chứng minh phân đoạn Test gốc tự thân mang một số khác biệt phân phối nhiệt độ tự nhiên ($T_{\text{air}}$ trung bình $298.40\text{ K}$ ở Test so với $300.32\text{ K}$ ở Train, $p < 10^{-5}$).
- Thuật ngữ "Control (No Injected Drift)" phản ánh chính xác rằng đây là nhóm đối chứng không bị can thiệp trôi dạt nhân tạo, bảo vệ tính trung thực của báo cáo nghiên cứu.

#### 3.2.2. Kết quả thực thi (Cell 4.2)
- Bản sao độc lập: `control_stream = stream_df.copy()`.
- Xác nhận tương đồng dữ liệu: `control_stream.equals(stream_df) = True`.
- Phân bố nhãn `Machine failure`:
  - Lớp `0` (Bình thường): **1.961 mẫu** ($98,05\%$).
  - Lớp `1` (Hỏng hóc): **39 mẫu** ($1,95\%$).

---

### 3.3. Phase 4.3 — Kịch bản Sudden Drift (`sudden_drift_stream`)

#### 3.3.1. Cơ sở khảo sát thống kê lựa chọn cảm biến (Cell 4.3.1)
Khảo sát 3 biến cơ học ứng viên trên 2.000 mẫu của Test stream:

| Cảm biến ứng viên | Mean | Std ($\sigma$) | Min | Q1 | Median | Q3 | Max |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Rotational speed [rpm]** | 1534.493 | 165.329 | 1181.0 | 1425.75 | 1504.0 | 1609.0 | 2636.0 |
| **Torque [Nm]** | 40.025 | 9.656 | 12.1 | 33.30 | 40.10 | 46.40 | 75.4 |
| **Tool wear [min]** | 106.246 | 63.124 | 0.0 | 51.00 | 106.0 | 161.0 | 246.0 |

**Quyết định thiết kế:**
1. **Lựa chọn kênh tác động:** Chọn kết hợp cặp biến cơ học liên kết chặt chẽ là **`Rotational speed [rpm]`** và **`Torque [Nm]`**. 
2. **Loại trừ `Tool wear` khỏi can thiệp:** `Tool wear` là biến số tích lũy đơn điệu theo chu kỳ gia công thực tế; việc cộng trừ nhân tạo trên biến này dễ làm biến dạng cấu trúc thời gian tự nhiên của hao mòn cơ khí.
3. **Mốc thời gian trôi dạt (Drift Point):** Chọn `index = 1000` (chia đôi luồng thành hai nửa cân bằng: 1.000 mẫu trước và 1.000 mẫu sau).
4. **Cường độ dịch chuyển (Shift Magnitudes):**
   - **RPM shift:** **$-150\text{ rpm}$** ($\approx 0.91\sigma_{\text{test}}$). Đủ mạnh để kéo kích hoạt từ tập mờ $MEDIUM$ sang $LOW$, nhưng không quá cực đoan làm sụp đổ toàn bộ hệ thống.
   - **Torque shift:** **$+8\text{ Nm}$** ($\approx 0.83\sigma_{\text{test}}$). Đẩy tải vận hành tiệm cận biên trên của tập mờ $HIGH$.
5. **Cơ chế kiểm soát biên (Clipping):** Bắt buộc sử dụng `np.clip` theo miền vũ luận của FIS (`RPM: [1168, 2886]`, `Torque: [3.8, 76.2]`) để ngăn chặn việc sinh ra các giá trị vượt ra ngoài không gian tính toán của hàm thuộc tính mờ.

#### 3.3.2. Triển khai và Kiểm tra biên (Cell 4.3.2)
- Áp dụng trên phân đoạn `index >= 1000`:
  $$\text{RPM}_{\text{drift}} = \text{clip}(\text{RPM} - 150, \, 1168, \, 2886)$$
  $$\text{Torque}_{\text{drift}} = \text{clip}(\text{Torque} + 8, \, 3.8, \, 76.2)$$
- Dải giá trị sau can thiệp:
  - `Rotational speed`: $1168 \to 2617\text{ rpm}$ (cận dưới chạm ngưỡng clip an toàn $1168\text{ rpm}$).
  - `Torque`: $12.1 \to 76.2\text{ Nm}$ (cận trên chạm ngưỡng clip an toàn $76.2\text{ Nm}$).
- Nhãn lỗi và `UDI`: `Labels unchanged = True`, `UDI unchanged = True`.

#### 3.3.3. Xác thực thống kê hai nửa chuỗi (Cell 4.3.3)
So sánh giữa phân đoạn Trước drift (`0 → 999`) và Sau drift (`1000 → 1999`):

| Biến cảm biến | Before Mean | After Mean | Mean Shift | Before Med | After Med | Median Shift | KS Statistic ($D$) | KS $p$-value |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Rotational speed [rpm]** | 1528.022 | 1391.699 | **−136.323** | 1501.0 | 1357.0 | **−144.0** | **0.4300** | $2.32 \times 10^{-83}$ |
| **Torque [Nm]** | 40.253 | 47.789 | **+7.536** | 40.05 | 48.10 | **+8.05** | **0.3080** | $2.79 \times 10^{-42}$ |
| **Tool wear [min]** (Đối chứng) | 105.255 | 107.237 | +1.982 | 104.5 | 108.0 | +3.5 | 0.0240 | 0.9358 |

> [!NOTE]
> **Quy chuẩn diễn giải thống kê:**
> - Sự sai khác giữa mức shift trung bình thực tế ($-136.32\text{ rpm}$, $+7.54\text{ Nm}$) so với mức danh định ($-150\text{ rpm}$, $+8\text{ Nm}$) xuất phát từ hiệu ứng chặn biên (clipping) và dao động tự nhiên giữa hai nửa chuỗi.
> - Kết quả kiểm định KS xác nhận sự thay đổi phân phối không gian thuộc tính đầu vào $P(X)$ (**covariate / feature distribution drift**), không phải bằng chứng khẳng định sự thay đổi hay bất biến của phân phối có điều kiện $P(Y \mid X)$.
> - Cảm biến Tool wear có $p = 0.9358 > 0.05$, cho thấy không quan sát thấy sự khác biệt phân phối có ý nghĩa thống kê trong kiểm định KS.

---

### 3.4. Phase 4.4 — Kịch bản Gradual Drift (`gradual_drift_stream`)

#### 3.4.1. Thiết kế Hàm Chuyển tiếp Tuyến tính (Linear Transition Function)
Để so sánh năng lực thích nghi giữa Sudden và Gradual, kịch bản trôi dạt tiệm tiến được thiết kế với cùng mức độ dịch chuyển cực đại ($-150\text{ rpm}$ và $+8\text{ Nm}$), nhưng phân bổ qua một cửa sổ chuyển tiếp có độ rộng 400 mẫu ($W = 400$):

```text
Hệ số alpha (α)
  1.0 ─────────────────────────────────────────┌─────────────── (Stable After)
                                              /│
                                             / │
                                            /  │
  0.5 ─────────────────────────────────────/───┼                (t = 1000)
                                          /    │
                                         /     │
  0.0 ──────────────────────────────────┘      │                (Stable Before)
      ├─────────────────────────────────┼──────┼───────────────┤
      0                                800    1200            1999 (Sample Index)
```

Hệ số trọng số trôi dạt $\alpha(i)$ tại mẫu thứ $i$ được định nghĩa:
$$\alpha(i) = \begin{cases} 0.0 & \text{nếu } i < 800 \\ \dfrac{i - 800}{1200 - 800} & \text{nếu } 800 \le i < 1200 \\ 1.0 & \text{nếu } i \ge 1200 \end{cases}$$

- Tại $i = 800$: $\alpha = 0.0$ (bắt đầu chuyển tiếp).
- Tại $i = 1000$: $\alpha = 0.5$ (tương ứng đúng điểm trôi dạt của Sudden Drift).
- Tại $i = 1199$: $\alpha = 0.9975$.
- Tại $i \ge 1200$: $\alpha = 1.0$ (trôi dạt hoàn toàn).

#### 3.4.2. Triển khai Kịch bản (Cell 4.4.1)
Tín hiệu sau biến đổi tại từng bước thời gian:
$$\text{RPM}(i) = \text{clip}\left(\text{RPM}_{\text{orig}}(i) + \alpha(i) \cdot (-150), \, 1168, \, 2886\right)$$
$$\text{Torque}(i) = \text{clip}\left(\text{Torque}_{\text{orig}}(i) + \alpha(i) \cdot (+8), \, 3.8, \, 76.2\right)$$

Kết quả xác nhận: `UDI unchanged: True`, `Labels unchanged: True` (39 lỗi).

#### 3.4.3. Xác thực thống kê giữa hai trạng thái ổn định (Cell 4.4.2)
Kiểm tra đối chứng giữa trạng thái trước chuyển tiếp (`0 → 799`, 800 mẫu) và trạng thái sau chuyển tiếp hoàn toàn (`1200 → 1999`, 800 mẫu), tách biệt vùng quá độ (`800 → 1199`):

| Biến cảm biến | Before Mean | After Mean | Mean Shift | Before Med | After Med | Median Shift | KS Statistic ($D$) | KS $p$-value |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Rotational speed [rpm]** | 1527.561 | 1388.809 | **−138.753** | 1500.0 | 1353.0 | **−147.0** | **0.4288** | $2.29 \times 10^{-66}$ |
| **Torque [Nm]** | 40.174 | 47.972 | **+7.797** | 40.00 | 48.35 | **+8.35** | **0.3212** | $6.68 \times 10^{-37}$ |
| **Tool wear [min]** (Đối chứng) | 105.154 | 108.981 | +3.828 | 104.0 | 109.5 | +5.5 | 0.0350 | 0.7116 |

**Nhận xét đối sánh định lượng giữa Sudden và Gradual:**
- Khoảng cách phân bố KS ($D$) của hai trạng thái biên trên Gradual Drift ($D_{\text{RPM}} = 0.4288$, $D_{\text{Torque}} = 0.3212$) có độ tương đồng chặt chẽ với Sudden Drift ($D_{\text{RPM}} = 0.4300$, $D_{\text{Torque}} = 0.3080$).
- Điều này chứng minh hai kịch bản có **cùng trạng thái phân phối trước và sau trôi dạt**, tạo điều kiện lý tưởng để đánh giá khả năng thích ứng của mô hình trước hai tốc độ biến thiên luồng khác nhau.

---

### 3.5. Phase 4.5 — Kiểm tra Toàn diện Tính Nhất quán và Biệt hóa

#### 3.5.1. Kiểm tra tính toàn vẹn đa luồng (Cell 4.5.1)

| Tiêu chuẩn kiểm tra | Control Stream | Sudden Drift Stream | Gradual Drift Stream | Kết luận |
| :--- | :---: | :---: | :---: | :---: |
| **Số lượng mẫu** | 2.000 | 2.000 | 2.000 | Đồng nhất $100\%$ |
| **Dải UDI** | $8001 \to 10000$ | $8001 \to 10000$ | $8001 \to 10000$ | Đồng nhất $100\%$ |
| **Tính đơn điệu UDI** | `True` | `True` | `True` | Bảo toàn trật tự luồng |
| **Số ca lỗi (`Machine failure = 1`)** | 39 | 39 | 39 | Không mất mát nhãn |
| **Nhất quán nhãn chéo (Cross-consistency)** | — | Khớp Control (`True`) | Khớp Control (`True`) | Ground truth bất biến |

#### 3.5.2. Kiểm tra tính biệt hóa và cô lập cảm biến (Cell 4.5.2)
Xác minh xem việc tiêm trôi dạt có vô tình làm biến đổi các kênh cảm biến không nằm trong diện can thiệp hay không:

| Cảm biến kiểm tra | Kịch bản Control | Kịch bản Sudden Drift | Kịch bản Gradual Drift | Đánh giá độ cô lập |
| :--- | :---: | :---: | :---: | :--- |
| **Air temperature [K]** | UNCHANGED | UNCHANGED | UNCHANGED | ✅ Cô lập hoàn hảo |
| **Process temperature [K]** | UNCHANGED | UNCHANGED | UNCHANGED | ✅ Cô lập hoàn hảo |
| **Rotational speed [rpm]** | UNCHANGED | **CHANGED** | **CHANGED** | ✅ Can thiệp đúng thiết kế |
| **Torque [Nm]** | UNCHANGED | **CHANGED** | **CHANGED** | ✅ Can thiệp đúng thiết kế |
| **Tool wear [min]** | UNCHANGED | UNCHANGED | UNCHANGED | ✅ Cô lập hoàn hảo |

---

## 4. Bảng Tổng hợp Tham số Thực nghiệm Phase 4

| Tham số / Thuộc tính | Control (No Injected Drift) | Sudden Drift Scenario | Gradual Drift Scenario |
| :--- | :---: | :---: | :---: |
| **Nguồn dữ liệu cơ sở** | Test stream ($UDI: 8001 \to 10000$) | Test stream ($UDI: 8001 \to 10000$) | Test stream ($UDI: 8001 \to 10000$) |
| **Kênh cảm biến can thiệp** | Không can thiệp | `Rotational speed`, `Torque` | `Rotational speed`, `Torque` |
| **Điểm bắt đầu drift ($t_{\text{start}}$)** | N/A | `index = 1000` | `index = 800` |
| **Điểm kết thúc drift ($t_{\text{end}}$)** | N/A | `index = 1000` (ngay lập tức) | `index = 1200` (400 mẫu) |
| **Dạng hàm chuyển tiếp** | N/A | Hàm bước nhảy (Step function) | Tuyến tính (Linear ramp $\alpha$) |
| **Mức dịch chuyển RPM** | $0\text{ rpm}$ | $-150\text{ rpm}$ ($\approx 0.91\sigma$) | Tuyến tính $0 \to -150\text{ rpm}$ |
| **Mức dịch chuyển Torque** | $0\text{ Nm}$ | $+8\text{ Nm}$ ($\approx 0.83\sigma$) | Tuyến tính $0 \to +8\text{ Nm}$ |
| **Miền clipping RPM** | N/A | $[1168, 2886]$ | $[1168, 2886]$ |
| **Miền clipping Torque** | N/A | $[3.8, 76.2]$ | $[3.8, 76.2]$ |
| **Bảo toàn nhãn mục tiêu** | 39 mẫu lỗi ($1.95\%$) | 39 mẫu lỗi ($1.95\%$) | 39 mẫu lỗi ($1.95\%$) |

---

## 5. Kết luận và Định hướng Chuyển tiếp sang Phase 5

### 5.1. Đóng Phase 4
- Toàn bộ 5 phân đoạn của Phase 4 (`4.1` $\to$ `4.5`) đã được triển khai hoàn chỉnh, độc lập trong notebook [`notebooks/04_controlled_concept_drift.ipynb`](file:///notebooks/04_controlled_concept_drift.ipynb).
- Toàn bộ các file cũ từ Phase 1 đến Phase 3 được giữ nguyên vẹn 100%.
- Giao thức 3 luồng thử nghiệm đối đầu (**Control**, **Sudden Drift**, **Gradual Drift**) đã sẵn sàng và được niêm phong cho các giai đoạn kế tiếp.

### 5.2. Định hướng Chuyển tiếp sang Phase 5
Với nền tảng 3 luồng kiểm thử sạch đã được thiết lập, Phase 5 sẽ tiến hành:
1. **Đánh giá phản ứng của Static Fuzzy Baseline** trên từng kịch bản luồng (đo lường sự suy giảm hiệu năng khi có drift).
2. **Nghiên cứu cơ chế Phát hiện Trôi dạt (Drift Detection):** Khảo sát các thuật toán giám sát luồng trực tuyến (như ADWIN, CUSUM hoặc phân tích trôi dạt phân bố điểm bất thường $A(X)$).
3. **Thiết kế Động cơ Mờ Thích nghi (Evolving Fuzzy Reasoning System):** Cơ chế điều chỉnh tham số hàm thuộc tính và cập nhật luật mờ khi nhận được tín hiệu cảnh báo drift.
