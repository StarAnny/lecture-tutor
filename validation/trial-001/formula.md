因为 \(H(s)U(s)\) 只给出**零初始条件下，由输入引起的输出**。电容原先已有 2 V，储存的能量也会影响后续电压，这部分必须另外保留。传递函数本身仍是讲义第 4 部分的 \(H(s)=1/(1+sRC)\)。

关键在对导数作拉普拉斯变换这一步。由讲义“课件第 2 页：建立方程”，

\[
RC\frac{dv_C}{dt}+v_C=u(t).
\]

记 \(V_C(s)=\mathcal L\{v_C(t)\}\)、\(U(s)=\mathcal L\{u(t)\}\)，并令 \(v_0=v_C(0^+)=2\,\mathrm V\)。由于

\[
\mathcal L\left\{\frac{dv_C}{dt}\right\}=sV_C(s)-v_0,
\]

所以

\[
RC[sV_C(s)-v_0]+V_C(s)=U(s).
\]

移项整理：

\[
(1+sRC)V_C(s)=U(s)+RCv_0,
\]

\[
\boxed{V_C(s)=\underbrace{\frac{U(s)}{1+sRC}}_{H(s)U(s)}
+\underbrace{\frac{RCv_0}{1+sRC}}_{\text{初始储能产生的响应}}.}
\]

初值项来自导数变换，不能略去。只有 \(v_0=0\) 时，第一项才等于总输出。这里第二项也可写成 \(v_0/(s+1/RC)\)，变回时间域就是 \(v_0e^{-t/(RC)}\)。

用讲义中的 \(R=2\,\mathrm{k\Omega}\)、\(C=100\,\mathrm{\mu F}\)、切换后输入 10 V 检查一下：\(RC=0.2\,\mathrm s\)，\(U(s)=10/s\)。两部分在时间域分别为

\[
v_{\text{输入}}(t)=10(1-e^{-t/(0.2\,\mathrm s)}),\qquad
v_{\text{初值}}(t)=2e^{-t/(0.2\,\mathrm s)}.
\]

相加得到

\[
v_C(t)=10-8e^{-t/(0.2\,\mathrm s)}\quad(\mathrm V).
\]

在 \(t=0^+\)，总输出是 2 V；若只取 \(H(s)U(s)\)，则算出的初始电压是 0 V，直接违背了题目的初始条件。这就是最直接的检查方法。
