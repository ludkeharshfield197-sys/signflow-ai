import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error

# 设置中文和负号
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 模拟数据生成 ---
np.random.seed(42)
n_samples = 100
obs = np.random.uniform(0.12, 0.4, n_samples)

# 1. LightGBM (拟合稍差，两端有水平截断感)
pred_lgb = 0.6 * obs + 0.1 + np.random.normal(0, 0.01, n_samples)
pred_lgb = np.clip(pred_lgb, 0.19, 0.27)  # 模拟原图中那种水平分布的特征

# 2. RandomForest (拟合非常好)
pred_rf = obs + np.random.normal(0, 0.003, n_samples)

# 3. SVR (拟合非常好，略有偏移)
pred_svr = 1.02 * obs + np.random.normal(0, 0.004, n_samples)

models = [
    {"name": "LightGBM", "obs": obs, "pred": pred_lgb, "pos": 221},
    {"name": "RandomForest", "obs": obs, "pred": pred_rf, "pos": 222},
    {"name": "SVR", "obs": obs, "pred": pred_svr, "pos": 223}
]

fig = plt.figure(figsize=(14, 12))
plt.suptitle("模型 B 训练-验证关系 (a→b 外推)", fontsize=16, y=0.95)

for m in models:
    ax = fig.add_subplot(m["pos"])
    o, p = m["obs"], m["pred"]

    # 计算指标
    rmse = np.sqrt(mean_squared_error(o, p))
    r2 = r2_score(o, p)

    # 散点图
    ax.scatter(o, p, alpha=0.5, edgecolors='none', s=40)

    # 1:1 参考线
    lims = [np.min([o, p]) * 0.9, np.max([o, p]) * 1.1]
    ax.plot(lims, lims, 'r--', label='1:1 线', linewidth=2)

    # 拟合线
    z = np.polyfit(o, p, 1)
    plot_fn = np.poly1d(z)
    ax.plot(lims, plot_fn(lims), 'g-', label='拟合线', linewidth=2)

    # 设置标题和标签
    ax.set_title(f"{m['name']}\nRMSE={rmse:.3f}, $R^2$={r2:.3f}")
    ax.set_xlabel("TRI_a (观测值)")
    ax.set_ylabel("TRI_b (预测值)")
    ax.legend(loc='upper left')
    ax.grid(True, linestyle=':', alpha=0.6)

plt.subplots_adjust(hspace=0.3, wspace=0.25)
plt.show()