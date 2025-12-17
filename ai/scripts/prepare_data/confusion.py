import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Dữ liệu confusion matrix
labels = ['battery', 'glass', 'metal', 'organic', 'cardboard', 'other', 'paper', 'plastic', 'textile', 'background']

# Ma trận 10x10 với dữ liệu phù hợp
data = np.array([
    [0.94, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.12],
    [0.00, 0.84, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.10],
    [0.00, 0.00, 0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.21],
    [0.00, 0.00, 0.00, 0.75, 0.00, 0.00, 0.00, 0.00, 0.00, 0.14],
    [0.00, 0.00, 0.00, 0.00, 0.78, 0.00, 0.01, 0.00, 0.00, 0.16],
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.81, 0.00, 0.00, 0.00, 0.14],
    [0.00, 0.00, 0.00, 0.00, 0.01, 0.00, 0.85, 0.01, 0.00, 0.14],
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.82, 0.00, 0.15],
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.77, 0.13],
    [0.06, 0.16, 0.23, 0.24, 0.20, 0.19, 0.34, 0.47, 0.23, 0.00]
])

# Tạo figure và axis với kích thước lớn hơn
fig, ax = plt.subplots(figsize=(12, 10))

# Vẽ heatmap với màu xanh navy như hình gốc
sns.heatmap(data, 
            annot=True,  # Hiển thị số
            fmt='.2f',   # Format 2 chữ số thập phân
            cmap='Blues',  # Bảng màu xanh
            xticklabels=labels,
            yticklabels=labels,
            cbar_kws={'label': ''},  # Thanh màu
            linewidths=0,  # Không có đường viền
            linecolor='white',
            vmin=0,
            vmax=1,
            ax=ax,
            annot_kws={'size': 16, 'weight': 'normal'})  # Tăng kích thước chữ số

# Thiết lập tiêu đề
ax.set_title('Confusion Matrix Normalized', fontsize=18, pad=20, weight='normal')

# Thiết lập nhãn trục
ax.set_xlabel('True', fontsize=16, weight='normal')
ax.set_ylabel('Predicted', fontsize=16, weight='normal')

# Tăng kích thước chữ cho labels
ax.set_xticklabels(labels, fontsize=14, rotation=45, ha='right')
ax.set_yticklabels(labels, fontsize=14, rotation=0)

# Điều chỉnh colorbar
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(labelsize=12)

# Điều chỉnh layout để không bị cắt chữ
plt.tight_layout()

# Hiển thị
plt.show()