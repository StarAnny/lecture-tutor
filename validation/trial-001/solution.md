电容电压在 \(0.2\,\mathrm s\) 时约为 **\(3.16\,\mathrm V\)**。推导如下。

令 \(v_C(t)\) 为电容电压，电流正方向取从电源经电阻流入电容正极。由回路电压关系和电容关系，

\[
Ri+v_C=5,\qquad i=C\frac{dv_C}{dt}.
\]

所以切换后的方程为

\[
RC\frac{dv_C}{dt}+v_C=5,\qquad v_C(0)=0.
\]

先计算时间常数：

\[
\tau=RC=(2\times10^3\,\Omega)(100\times10^{-6}\,\mathrm F)
=0.2\,\mathrm s.
\]

为了求解，令 \(w(t)=5-v_C(t)\)，它表示距离稳态电压还差多少。原方程因此变成

\[
\frac{dw}{dt}=-\frac{w}{\tau}.
\]

分离变量并积分，得到 \(w(t)=Ae^{-t/\tau}\)。由于 \(w(0)=5-v_C(0)=5\,\mathrm V\)，常数 \(A=5\,\mathrm V\)，因此

\[
\boxed{v_C(t)=5\left(1-e^{-t/(0.2\,\mathrm s)}\right)\ \mathrm V.}
\]

代入 \(t=0.2\,\mathrm s=\tau\)：

\[
\boxed{v_C(0.2\,\mathrm s)=5(1-e^{-1})\,\mathrm V
\approx3.1606\,\mathrm V.}
\]

检查：\(t=0\) 时电压为 0，\(t\to\infty\) 时趋于 5 V；导数为正，电压单调上升。经过一个时间常数完成约 63.2% 的电压变化，与计算结果一致。
