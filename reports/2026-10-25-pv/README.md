# مجموعه اعتبارسنجی PV — 2026-10-25

این بسته شامل گزارش جامع، خلاصه ماشین‌خوان، ماتریس پذیرش، فایل‌های CSV و نمودارهای ارجاع‌شده است. فایل‌های گزارش و داده‌های جدول‌بندی‌شده در این مخزن نگهداری می‌شوند؛ نمودارهای SVG اصلی به منبع WindFarm پیوند دارند.

## فایل‌های این مخزن
- [گزارش جامع](report.md)
- [خلاصه ماشین‌خوان](component_yield_summary.json)
- [ماتریس پذیرش](acceptance_matrix.csv)
- [مقایسه GHI/DNI/DHI](component_source_comparison.csv)
- [اختلاف ماهانه مؤلفه‌ها و POA](monthly_component_bias.csv)
- [مقایسه مدل‌های POA](poa_model_comparison.csv)
- [مقایسه مدل تولید سالانه و مرز DC/AC](annual_yield_model_comparison.csv)
- [هم‌ترازی زمانی](time_alignment.csv)

## نمودارهای SVG منبع
- [Monthly component bias](https://github.com/Japharzadeh/WindFarm/blob/feature/pv-validation-desktop-ui/validations/results/component_yield_2026-10-25/monthly_component_bias.svg)
- [Monthly POA bias](https://github.com/Japharzadeh/WindFarm/blob/feature/pv-validation-desktop-ui/validations/results/component_yield_2026-10-25/monthly_poa_bias.svg)
- [PVGIS transposition bias at 32°](https://github.com/Japharzadeh/WindFarm/blob/feature/pv-validation-desktop-ui/validations/results/component_yield_2026-10-25/monthly_pvgis_transposition_bias_32deg.svg)
- [Time alignment MAE](https://github.com/Japharzadeh/WindFarm/blob/feature/pv-validation-desktop-ui/validations/results/component_yield_2026-10-25/time_alignment_mae.svg)

## منبع و سابقه اجرا
- منبع: [WindFarm validation outputs](https://github.com/Japharzadeh/WindFarm/tree/feature/pv-validation-desktop-ui/validations/results/component_yield_2026-10-25)
- [اجرای GitHub Actions](https://github.com/Japharzadeh/WindFarm/actions/runs/40231005334)
- [آرتیفکت اجرای CI](https://github.com/Japharzadeh/WindFarm/actions/runs/40231005334/artifacts/12613650207)

**محدودیت بایگانی:** داده‌های ساعتی خام/میانی کامل در این commit به‌صورت فایل محلی کپی نشده‌اند؛ فعلاً از آرتیفکت CI قابل دسترسی‌اند. برای بایگانی بلندمدت باید آرتیفکت دانلود و در مخزن/فضای آرشیو مناسب نگهداری شود، پس از بررسی مجوز و حجم.
