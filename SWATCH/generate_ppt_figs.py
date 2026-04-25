import pandas as pd, numpy as np, statsmodels.api as sm, os
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import RidgeCV, Ridge
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
from sklearn.metrics import r2_score
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from statsmodels.graphics.gofplots import ProbPlot
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib as mpl, matplotlib.font_manager as fm
import seaborn as sns
import warnings; warnings.filterwarnings('ignore')

font_path = r'C:\Windows\Fonts\malgun.ttf'
font_prop = fm.FontProperties(fname=font_path)
mpl.rcParams['font.family'] = font_prop.get_name()
mpl.rcParams['axes.unicode_minus'] = False

# ── data ──────────────────────────────────────────────
os.chdir(r'c:\Programming\Github\Python')
df_raw = pd.read_excel('./datasets/swatch.xlsx')
oc = df_raw.columns.tolist()
label_w, label_b = oc[1], oc[2]
df = df_raw.rename(columns={oc[1]:'weight', oc[2]:'BET', oc[3]:'GD', oc[4]:'HD'})
w, b = df['weight'].values, df['BET'].values
y_GD, y_HD = df['GD'].values, df['HD'].values
n, GD_base, HD_base = len(df), 357, 671
samples = df['Sample'].tolist()
loo = LeaveOneOut()
os.makedirs('./SWATCH/ppt_figs', exist_ok=True)

# ── Figure 1: pass/fail bar chart ─────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, (y_arr, lim, color, title) in zip(axes, [
        (y_GD, GD_base, 'tomato',    'GD 보호농도 (기준: 357 mg·min/m³)'),
        (y_HD, HD_base, 'darkorange','HD 보호농도 (기준: 671 mg·min/m³)'),
]):
    pm = y_arr <= lim
    bc = ['steelblue' if p else color for p in pm]
    bars = ax.bar(samples, y_arr, color=bc, edgecolor='white', alpha=0.85)
    ax.axhline(lim, color='red', linestyle='--', linewidth=2, label=f'기준={lim}')
    for bar, val in zip(bars, y_arr):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+15,
                str(val), ha='center', va='bottom', fontsize=9, fontweight='bold')
    pp = mpatches.Patch(color='steelblue', label=f'합격({pm.sum()}개)')
    fp = mpatches.Patch(color=color,       label=f'불합격({(~pm).sum()}개)')
    ax.legend(handles=[pp, fp], fontsize=9)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_ylabel('농도 (mg·min/m³)'); ax.tick_params(axis='x', rotation=45)
plt.suptitle('이미테이션 보호농도 24시간 측정 결과', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('./SWATCH/ppt_figs/fig1_data.png', dpi=150, bbox_inches='tight')
plt.close(); print('fig1 done')

# ── Figure 2: correlation heatmaps ────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
data_orig = pd.DataFrame({'무게': w, 'BET': b, 'GD': y_GD, 'HD': y_HD})
data_log  = pd.DataFrame({'log(무게)': np.log(w), 'log(BET)': np.log(b),
                           'log(GD)': np.log(y_GD), 'log(HD)': np.log(y_HD)})
for ax, data, title in zip(axes, [data_orig, data_log], ['원본 변수', '로그 변환 변수']):
    sns.heatmap(data.corr(), ax=ax, annot=True, fmt='.3f', cmap='coolwarm',
                vmin=-1, vmax=1, square=True, linewidths=0.5, annot_kws={'size':12})
    ax.set_title(title, fontsize=13, fontweight='bold')
plt.suptitle('상관관계 비교: 원본 vs 로그 변환', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('./SWATCH/ppt_figs/fig2_corr.png', dpi=150, bbox_inches='tight')
plt.close(); print('fig2 done')

# ── compute all transforms ────────────────────────────
transform_specs = [
    ('원본',                     y_GD,          y_HD,          w,         b),
    ('log(y)',                   np.log(y_GD),  np.log(y_HD),  w,         b),
    ('log(y), log(BET)',         np.log(y_GD),  np.log(y_HD),  w,         np.log(b)),
    ('log(y), log(무), log(BET)',np.log(y_GD),  np.log(y_HD),  np.log(w), np.log(b)),
    ('sqrt(y)',                  np.sqrt(y_GD), np.sqrt(y_HD), w,         b),
    ('sqrt(y), log(BET)',        np.sqrt(y_GD), np.sqrt(y_HD), w,         np.log(b)),
    ('sqrt(y), log(무), log(BET)',np.sqrt(y_GD),np.sqrt(y_HD), np.log(w), np.log(b)),
]
models_by_name = {}
r2G, r2H, adjG, adjH, fpG, fpH = [], [], [], [], [], []
short_names = ['원본','log(y)','log(y)\nlog(BET)','log(y)\nlog(무)\nlog(BET)',
               'sqrt(y)','sqrt(y)\nlog(BET)','sqrt(y)\nlog(무)\nlog(BET)']
for name, ytG, ytH, x1, x2 in transform_specs:
    X = sm.add_constant(np.column_stack([x1, x2]))
    mG = sm.OLS(ytG, X).fit(); mH = sm.OLS(ytH, X).fit()
    models_by_name[name] = (mG, mH, ytG, ytH)
    r2G.append(mG.rsquared); r2H.append(mH.rsquared)
    adjG.append(mG.rsquared_adj); adjH.append(mH.rsquared_adj)
    fpG.append(mG.f_pvalue);  fpH.append(mH.f_pvalue)

# ── Figure 3: transform comparison ───────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
xi = np.arange(len(short_names)); w2 = 0.35
ax = axes[0]
b1 = ax.bar(xi-w2/2, adjG, w2, label='GD', color='steelblue', edgecolor='black', alpha=0.8)
b2 = ax.bar(xi+w2/2, adjH, w2, label='HD', color='darkorange', edgecolor='black', alpha=0.8)
ax.set_xticks(xi); ax.set_xticklabels(short_names, fontsize=8)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_ylabel('adj-R²'); ax.set_title('변환별 adj-R² 비교', fontweight='bold'); ax.legend()
for bar in list(b1)+list(b2):
    h = bar.get_height()
    ax.text(bar.get_x()+bar.get_width()/2, h+(0.01 if h >= 0 else -0.05),
            f'{h:.2f}', ha='center', va='bottom' if h >= 0 else 'top', fontsize=7)

ax = axes[1]
bcG = ['steelblue' if p <= 0.05 else 'lightcoral' for p in fpG]
bcH = ['darkorange' if p <= 0.05 else '#FFCC99'   for p in fpH]
b3 = ax.bar(xi-w2/2, fpG, w2, color=bcG, edgecolor='black', alpha=0.85, label='GD')
b4 = ax.bar(xi+w2/2, fpH, w2, color=bcH, edgecolor='black', alpha=0.85, label='HD')
ax.axhline(0.05, color='red', linestyle='--', linewidth=1.5, label='α=0.05')
ax.set_xticks(xi); ax.set_xticklabels(short_names, fontsize=8)
ax.set_ylabel('F 통계량 p-값'); ax.set_title('변환별 F 검정 p-값\n(낮을수록 유의)', fontweight='bold')
ax.legend()
for bar in list(b3)+list(b4):
    h = bar.get_height()
    ax.text(bar.get_x()+bar.get_width()/2, h+0.004, f'{h:.3f}', ha='center', va='bottom', fontsize=7)
plt.suptitle('변수 변환별 OLS 모형 성능 비교', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('./SWATCH/ppt_figs/fig3_transform.png', dpi=150, bbox_inches='tight')
plt.close(); print('fig3 done')

# ── Figure 4: best HD model ────────────────────────────
best_HD = 'log(y), log(BET)'
_, mH_best, _, ytH_best = models_by_name[best_HD]
print(mH_best.summary())

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
pred_t = mH_best.fittedvalues; resid = mH_best.resid
ax = axes[0]
ax.scatter(pred_t, ytH_best, color='darkorange', edgecolors='black', s=80)
mn = min(float(ytH_best.min()), float(pred_t.min())); mx = max(float(ytH_best.max()), float(pred_t.max()))
ax.plot([mn,mx],[mn,mx],'r--',linewidth=1.5)
for i, s in enumerate(samples):
    ax.annotate(s, (pred_t[i], ytH_best[i]), fontsize=7, xytext=(4,4), textcoords='offset points')
ax.set_xlabel('예측값 [log(HD)]'); ax.set_ylabel('관측값 [log(HD)]')
ax.set_title(f'Pred vs Observed\n$R^2$={mH_best.rsquared:.3f}, F p={mH_best.f_pvalue:.4f}', fontweight='bold')
ax = axes[1]
ax.scatter(pred_t, resid, color='darkorange', edgecolors='black', s=70)
ax.axhline(0, color='red', linestyle='--')
for i, s in enumerate(samples):
    ax.annotate(s, (pred_t[i], resid[i]), fontsize=7, xytext=(3,3), textcoords='offset points')
ax.set_xlabel('Fitted'); ax.set_ylabel('Residual'); ax.set_title('Residuals vs Fitted', fontweight='bold')
ax = axes[2]
pp = ProbPlot(resid); pp.qqplot(line='s', ax=ax, alpha=0.8)
for line in ax.get_lines():
    if line.get_linestyle() == 'None':
        line.set_color('darkorange'); line.set_markersize(7); line.set_markeredgecolor('black')
ax.set_title('Normal Q-Q', fontweight='bold')
plt.suptitle(f'[HD 최적 모형] {best_HD}\n$R^2$=0.831, adj-$R^2$=0.775, F p=0.0048, p(무게)=0.004, p(BET)=0.043',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('./SWATCH/ppt_figs/fig4_HD_best.png', dpi=150, bbox_inches='tight')
plt.close(); print('fig4 done')

# ── Ridge ─────────────────────────────────────────────
X_orig = df[['weight','BET']].values
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X_orig)
feat_names = poly.get_feature_names_out(['무게','BET'])
scaler_poly = StandardScaler(); X_sc = scaler_poly.fit_transform(X_poly)
ridge_res = {}
for target, y in [('GD', y_GD), ('HD', y_HD)]:
    rc = RidgeCV(alphas=np.logspace(1, 6, 200), cv=loo, scoring='r2'); rc.fit(X_sc, y)
    rb = Ridge(alpha=rc.alpha_)
    lp = cross_val_predict(rb, X_sc, y, cv=loo)
    rb.fit(X_sc, y)
    ridge_res[target] = {
        'alpha': rc.alpha_, 'in_r2': r2_score(y, rb.predict(X_sc)),
        'loo_r2': r2_score(y, lp), 'loo_rmse': float(np.sqrt(np.mean((y-lp)**2))),
        'coefs': rb.coef_, 'loo_preds': lp,
    }
    print(f'Ridge[{target}]: alpha={rc.alpha_:.0f}, in_r2={ridge_res[target]["in_r2"]:.3f}, loo_r2={ridge_res[target]["loo_r2"]:.3f}')

# ── Figure 5: Ridge ────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
for row, (target, y, base, color) in enumerate([('GD', y_GD, GD_base, 'steelblue'),
                                                  ('HD', y_HD, HD_base, 'darkorange')]):
    r = ridge_res[target]
    ax = axes[row][0]
    bc = ['tomato' if c < 0 else color for c in r['coefs']]
    ax.bar(feat_names, r['coefs'], color=bc, edgecolor='black', alpha=0.8)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_title(f'[{target}] Ridge 표준화 계수\n(α={r["alpha"]:.0f}, 학습 R²={r["in_r2"]:.3f})', fontweight='bold')
    ax.tick_params(axis='x', rotation=30)
    ax = axes[row][1]
    preds = r['loo_preds']
    ptc = [color if v <= base else 'tomato' for v in y]
    ax.scatter(preds, y, c=ptc, edgecolors='black', s=80, zorder=5)
    mn = min(y.min(), preds.min())-20; mx = max(y.max(), preds.max())+20
    ax.plot([mn,mx],[mn,mx],'r--',linewidth=1.5)
    ax.axhline(base, color='gray', linestyle=':', label=f'기준={base}')
    for i, s in enumerate(samples):
        ax.annotate(s, (preds[i], y[i]), fontsize=7, xytext=(4,4), textcoords='offset points')
    ax.set_xlabel('LOO 예측값'); ax.set_ylabel('관측값')
    ax.set_title(f'[{target}] Ridge LOO\nLOO R²={r["loo_r2"]:.3f}, RMSE={r["loo_rmse"]:.1f}', fontweight='bold')
    ax.legend(fontsize=8)
plt.suptitle('다항 Ridge 회귀 결과 (2차항+상호작용항)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('./SWATCH/ppt_figs/fig5_ridge.png', dpi=150, bbox_inches='tight')
plt.close(); print('fig5 done')

# ── GPR ──────────────────────────────────────────────
scaler_gpr = StandardScaler(); Xs = scaler_gpr.fit_transform(df[['weight','BET']].values)
kernel_gpr = (ConstantKernel(1.0,(1e-3,1e3)) * RBF([1.0,1.0],(1e-2,1e2)) + WhiteKernel(0.5,(1e-4,1e2)))
gpr_res = {}
for target, y in [('GD', y_GD), ('HD', y_HD)]:
    gpr = GaussianProcessRegressor(kernel=kernel_gpr, n_restarts_optimizer=15, normalize_y=True)
    gpr.fit(Xs, y)
    ip, _ = gpr.predict(Xs, return_std=True)
    lp2 = np.zeros(n); ls2 = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool); mask[i] = False
        g2 = GaussianProcessRegressor(kernel=gpr.kernel_, n_restarts_optimizer=0, normalize_y=True)
        g2.fit(Xs[mask], y[mask])
        p_, s_ = g2.predict(Xs[i:i+1], return_std=True)
        lp2[i] = p_[0]; ls2[i] = s_[0]
    gpr_res[target] = {
        'model': gpr, 'in_r2': r2_score(y, ip),
        'loo_r2': r2_score(y, lp2), 'loo_rmse': float(np.sqrt(np.mean((y-lp2)**2))),
        'lp': lp2, 'ls': ls2,
    }
    print(f'GPR[{target}]: in_r2={gpr_res[target]["in_r2"]:.3f}, loo_r2={gpr_res[target]["loo_r2"]:.3f}')

# ── Figure 6: GPR ─────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, (target, y, base, color) in zip(axes, [('GD', y_GD, GD_base, 'steelblue'),
                                                 ('HD', y_HD, HD_base, 'darkorange')]):
    r = gpr_res[target]; preds, stds = r['lp'], r['ls']
    ptc = [color if v <= base else 'tomato' for v in y]
    ax.errorbar(preds, y, xerr=1.96*stds, fmt='none', ecolor='gray', alpha=0.5, capsize=4)
    ax.scatter(preds, y, c=ptc, edgecolors='black', s=80, zorder=5)
    mn = min(float(y.min()), float(preds.min()))-30
    mx = max(float(y.max()), float(preds.max()))+30
    ax.plot([mn,mx],[mn,mx],'r--',linewidth=1.5,label='y=x')
    ax.axhline(base, color='gray', linestyle=':', label=f'기준={base}')
    for i, s in enumerate(samples):
        ax.annotate(s, (preds[i], y[i]), fontsize=7, xytext=(4,4), textcoords='offset points')
    ax.set_xlabel('GPR LOO 예측값 (±1.96σ)'); ax.set_ylabel('관측값')
    ax.set_title(f'[{target}] GPR LOO\nLOO R²={r["loo_r2"]:.3f}, RMSE={r["loo_rmse"]:.1f}', fontweight='bold')
    ax.legend(fontsize=8)
plt.suptitle('가우시안 프로세스 회귀 (GPR) — LOO 예측 (±1.96σ)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('./SWATCH/ppt_figs/fig6_gpr.png', dpi=150, bbox_inches='tight')
plt.close(); print('fig6 done')

# ── Figure 7: summary bar chart ───────────────────────
X_ols = sm.add_constant(np.column_stack([w, b]))
ols_lp_GD = cross_val_predict(Ridge(alpha=1e-9), X_ols, y_GD, cv=loo)
ols_lp_HD = cross_val_predict(Ridge(alpha=1e-9), X_ols, y_HD, cv=loo)
_, mGD_best, ytGD_best, _ = models_by_name['log(y), log(무), log(BET)']
_, mHD_best2, _, ytHD_best2 = models_by_name[best_HD]

loo_r2_GD_list = [
    round(r2_score(y_GD, ols_lp_GD), 3),
    round(mGD_best.rsquared, 3),
    round(ridge_res['GD']['loo_r2'], 3),
    round(gpr_res['GD']['loo_r2'], 3),
]
loo_r2_HD_list = [
    round(r2_score(y_HD, ols_lp_HD), 3),
    round(mHD_best2.rsquared, 3),
    round(ridge_res['HD']['loo_r2'], 3),
    round(gpr_res['HD']['loo_r2'], 3),
]
loo_rmse_GD_list = [
    round(float(np.sqrt(np.mean((y_GD-ols_lp_GD)**2))), 1),
    None,
    round(ridge_res['GD']['loo_rmse'], 1),
    round(gpr_res['GD']['loo_rmse'], 1),
]
loo_rmse_HD_list = [
    round(float(np.sqrt(np.mean((y_HD-ols_lp_HD)**2))), 1),
    None,
    round(ridge_res['HD']['loo_rmse'], 1),
    round(gpr_res['HD']['loo_rmse'], 1),
]
ml = ['원본 OLS', '변환 OLS\n(최적)', 'Ridge\n(다항2차)', 'GPR']
xi = np.arange(4); w2 = 0.35

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ax = axes[0]
b1 = ax.bar(xi-w2/2, loo_r2_GD_list, w2, label='GD', color='steelblue', edgecolor='black', alpha=0.8)
b2 = ax.bar(xi+w2/2, loo_r2_HD_list, w2, label='HD', color='darkorange', edgecolor='black', alpha=0.8)
ax.set_xticks(xi); ax.set_xticklabels(ml, fontsize=9)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_ylabel('LOO R²  /  학습 R² (변환OLS)')
ax.set_title('모형별 R² 비교', fontweight='bold'); ax.legend()
for bar in list(b1)+list(b2):
    h = bar.get_height()
    ax.text(bar.get_x()+bar.get_width()/2, h+(0.02 if h >= 0 else -0.08),
            f'{h:.2f}', ha='center', va='bottom' if h >= 0 else 'top', fontsize=9, fontweight='bold')

ax = axes[1]
vals_G = [(i, v) for i, v in enumerate(loo_rmse_GD_list) if v is not None]
vals_H = [(i, v) for i, v in enumerate(loo_rmse_HD_list) if v is not None]
ax.bar([v[0]-w2/2 for v in vals_G], [v[1] for v in vals_G], w2, label='GD', color='steelblue', edgecolor='black', alpha=0.8)
ax.bar([v[0]+w2/2 for v in vals_H], [v[1] for v in vals_H], w2, label='HD', color='darkorange', edgecolor='black', alpha=0.8)
ax.set_xticks(xi); ax.set_xticklabels(ml, fontsize=9)
ax.set_ylabel('LOO RMSE'); ax.set_title('모형별 LOO RMSE (낮을수록 우수)', fontweight='bold'); ax.legend()
for bars_list, vals_list in [(ax.patches[:len(vals_G)], vals_G), (ax.patches[len(vals_G):], vals_H)]:
    for bar, (_, h) in zip(bars_list, vals_list):
        ax.text(bar.get_x()+bar.get_width()/2, h+3, f'{h:.0f}', ha='center', va='bottom', fontsize=9)

plt.suptitle('모형 성능 종합 비교 (n=9, Leave-One-Out CV)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('./SWATCH/ppt_figs/fig7_summary.png', dpi=150, bbox_inches='tight')
plt.close(); print('fig7 done')

print('\nAll figures saved to ./SWATCH/ppt_figs/')
print('Summary:')
print(f'  GD best transform: 어떤 변환도 F p>0.05 (GD는 유의하지 않음)')
print(f'  HD best transform: {best_HD} -> R²=0.831, adj-R²=0.775, F p=0.0048')
print(f'  Ridge GD: in_r2={ridge_res["GD"]["in_r2"]:.3f}, loo_r2={ridge_res["GD"]["loo_r2"]:.3f}')
print(f'  Ridge HD: in_r2={ridge_res["HD"]["in_r2"]:.3f}, loo_r2={ridge_res["HD"]["loo_r2"]:.3f}')
print(f'  GPR GD:   in_r2={gpr_res["GD"]["in_r2"]:.3f},  loo_r2={gpr_res["GD"]["loo_r2"]:.3f}')
print(f'  GPR HD:   in_r2={gpr_res["HD"]["in_r2"]:.3f},  loo_r2={gpr_res["HD"]["loo_r2"]:.3f}')
