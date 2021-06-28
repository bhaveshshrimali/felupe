# Theory Guide

## Kinematics
...

## Constitution

### Mixed-field formulations
Felupe supports mixed-field formulations in a similar way it can handle (default) single-field variations. The definition of a mixed-field variation is shown for the hydrostatic-volumetric selective three-field-variation with independend fields for displacements $\bm{u}$, pressure $p$ and volume ratio $J$. The total potential energy for nearly-incompressible hyperelasticity is formulated with a determinant-modified deformation gradient.

### Total potential energy: variation and linearization

$$\Pi = \Pi_{int} + \Pi_{ext}$$

$$\Pi_{int} = \int_V \psi(\bm{F}) \ dV \qquad \rightarrow \qquad \Pi_{int}(\bm{u},p,J) = \int_V \psi(\overline{\bm{F}}) \ dV + \int_V p (J-\overline{J}) \ dV$$

$$\overline{\bm{F}} = \left(\frac{\overline{J}}{J}\right)^{1/3} \bm{F}$$

The variations of the total potential energy w.r.t. $(\bm{u},p,J)$ lead to the following expressions.

$$\delta_{\bm{u}} \Pi_{int} = \int_V \bm{f}_{\bm{u}} : \delta \bm{F} \ dV = \int_V \left( \frac{\partial \psi}{\partial \overline{\bm{F}}} : \frac{\partial \overline{\bm{F}}}{\partial \bm{F}} + p J \bm{F}^{-T} \right) : \delta \bm{F} \ dV$$

$$\delta_{p} \Pi_{int} = \int_V f_{p} \ \delta p \ dV = \int_V (J - \overline{J}) \ \delta p \ dV$$

$$\delta_{\overline{J}} \Pi_{int} = \int_V f_{\overline{J}} \ \delta \overline{J} \ dV = \int_V \left( \frac{\partial \psi}{\partial \overline{\bm{F}}} : \frac{\partial \overline{\bm{F}}}{\partial \overline{J}} - p \right) : \delta \overline{J} \ dV$$

The projection tensors from the variations lead the following results.

$$\frac{\partial \overline{\bm{F}}}{\partial \bm{F}} = \left(\frac{\overline{J}}{J}\right)^{1/3} \left( \bm{I} \overset{ik}{\odot} \bm{I} - \frac{1}{3} \bm{F} \otimes \bm{F}^{-T} \right)$$

$$\frac{\partial \overline{\bm{F}}}{\partial \overline{J}} = \frac{1}{3 \overline{J}} \overline{\bm{F}}$$

The double-dot products from the variations are now evaluated.

$$\overline{\bm{P}} = \frac{\partial \psi}{\partial \overline{\bm{F}}} = \overline{\overline{\bm{P}}} - \frac{1}{3} \left(  \overline{\overline{\bm{P}}} : \bm{F} \right) \bm{F}^{-T} \qquad \text{with} \qquad \overline{\overline{\bm{P}}} = \left(\frac{\overline{J}}{J}\right)^{1/3} \frac{\partial \psi}{\partial \overline{\bm{F}}}$$

$$\frac{\partial \psi}{\partial \overline{\bm{F}}} : \frac{1}{3 \overline{J}} \overline{\bm{F}} = \frac{1}{3 \overline{J}} \overline{\overline{\bm{P}}} : \bm{F}$$

We now have three formulas; one for the first Piola Kirchhoff stress and two additional control equations.

$$\bm{f}_{\bm{u}} (= \bm{P}) = \overline{\overline{\bm{P}}} - \frac{1}{3} \left(  \overline{\overline{\bm{P}}} : \bm{F} \right) \bm{F}^{-T} $$

$$f_p = J - \overline{J} $$

$$f_{\overline{J}} =  \frac{1}{3 \overline{J}} \left( \overline{\overline{\bm{P}}} : \bm{F} \right) - p$$

A linearization of the above formulas gives six equations (only results are given here).

$$\mathbb{A}_{\bm{u},\bm{u}} =  \overline{\overline{\mathbb{A}}} + \frac{1}{9} \left(  \bm{F} : \overline{\overline{\mathbb{A}}} : \bm{F} \right) \bm{F}^{-T} \otimes \bm{F}^{-T} - \frac{1}{3} \left( \bm{F}^{-T} \otimes \left( \overline{\overline{\bm{P}}} + \bm{F} : \overline{\overline{\mathbb{A}}} \right) + \left( \overline{\overline{\bm{P}}} + \overline{\overline{\mathbb{A}}} : \bm{F} \right) \otimes \bm{F}^{-T} \right)$$

$$+\left( p J + \frac{1}{9} \overline{\overline{\bm{P}}} : \bm{F} \right) \bm{F}^{-T} \otimes \bm{F}^{-T} - \left( p J - \frac{1}{3} \overline{\overline{\bm{P}}} : \bm{F} \right) \bm{F}^{-T} \overset{il}{\odot} \bm{F}^{-T} $$

$$A_{p,p} = 0 $$

$$A_{\overline{J},\overline{J}} = \frac{1}{9 \overline{J}^2} \left( \bm{F} : \overline{\overline{\mathbb{A}}} : \bm{F} \right) - 2 \left( \overline{\overline{\bm{P}}} : \bm{F} \right) $$

$$\bm{A}_{\bm{u},p} = \bm{A}_{p, \bm{u}} = J \bm{F}^{-T} $$

$$\bm{A}_{\bm{u},\overline{J}} = \bm{A}_{\overline{J}, \bm{u}} = \frac{1}{3 \overline{J}} \left( \bm{P}' + \bm{F} : \overline{\overline{\mathbb{A}}} - \frac{1}{3} \left( \bm{F} : \overline{\overline{\mathbb{A}}} : \bm{F} \right) \bm{F}^{-T} \right) $$

$$A_{p,\overline{J}} = A_{\overline{J}, p} = -1 $$

with $$ \overline{\overline{\mathbb{A}}} = \left(\frac{\overline{J}}{J}\right)^{1/3} \frac{\partial^2 \psi}{\partial \overline{\bm{F}} \partial \overline{\bm{F}}} \left(\frac{\overline{J}}{J}\right)^{1/3}$$

as well as

$$\bm{P}' = \bm{P} - p J \bm{F}^{-T}$$

## Kinetics
...

## Supported Finite Elements
FElupe supports lagrangian line, quad and hexaeder elements with arbitrary order polynomial basis functions. However, FElupe's mesh generation module is designed for linear and constant order elements only. For simulations with arbitrary order elements a user-defined mesh has to be provided.

| Description | Order | Nodes | Mesh module compatible | save as VTK |
|---|---|---|---|---|
| Constant Hexahedron | 0 | 1 | yes | yes |
| Linear Hexahedron | 1 | 8 | yes | yes |
| Quadratic Serendipity Hexahedron | 2 | 20 | no | yes |
| Lagrange Hexahedron | $p$ | $(p+1)^3$ | no | yes |

## Arbitrary Order Lagrange Elements
A complete lagrange polynomial $h(r)$ of order $p$ results from a sum of products of curve parameters $a_i$ associated to the normalized i-th power of a variable $\frac{r^i}{i!}$. For the determination of the curve parameters $a_i$ a total number of $n=p+1$ evaluation points are necessary.

$$h(r) = \sum_{i=0}^p a_i \frac{r^i}{i!} = \bm{a}^T \bm{r}(r)$$

### Polynomial basis functions
The basis function vector is generated with row-stacking of the individual lagrange polynomials. Each polynomial defined in the interval $[-1,1]$ is a function of the parameter $r$. The curve parameters matrix $\bm{A}$ is of symmetric shape due to the fact that for each evaluation point $r_j$ exactly one basis function $h_j(r)$ is needed.

$$\bm{h}(r) = \bm{A}^T \bm{r}(r)$$

### Curve parameter matrix
The evaluation of the curve parameter matrix $\bm{A}$ is carried out by boundary conditions. Each basis function $h_i$ has to take the value of one at the associated nodal coordinate $r_i$ and zero at all other nodal coordinates.

$$\bm{A}^T \bm{R} = \bm{I} \qquad \text{with} \qquad \bm{R} = \begin{bmatrix}\bm{r}(r_1) & \bm{r}(r_2) & \dots & \bm{r}(r_p)\end{bmatrix}$$

$$\bm{A}^T = \bm{R}^{-1}$$

### Interpolation and partial derivatives
The approximation of nodal unknowns $\hat{\bm{u}}$ as a function of the parameter $r$ is evaluated as

$$\bm{u}(r) \approx \hat{\bm{u}}^T \bm{h}(r)$$

For the calculation of the partial derivative of the interpolation field w.r.t. the parameter $r$ a simple shift of the entries of the parameter vector is enough. This shifted parameter vector is denoted as $\bm{r}^-$. A minus superscript indices the negative shift of the vector entries by $-1$.

$$\frac{\partial \bm{u}(r)}{\partial r} \approx \hat{\bm{u}}^T \frac{\partial \bm{h}(r)}{\partial r}$$

$$\frac{\partial \bm{h}(r)}{\partial r} = \bm{A}^T \bm{r}^-(r) \qquad \text{with} \qquad r_0^- = 0 \qquad \text{and} \qquad r_i^- = \frac{r^{(i-1)}}{(i-1)!} \qquad \text{for} \qquad  i=(1 \dots p)$$

### n-dimensional basis functions
Multi-dimensional basis function matrices $\bm{H}_{2D}, \bm{H}_{3D}$ are simply evaluated as dyadic (outer) vector products of one-dimensional basis function vectors. The multi-dimensional basis function vector is a one-dimensional representation (flattened version) of the multi-dimensional basis function matrix.

$$ \bm{H}_{2D}(r,s) = \bm{h}(r) \otimes \bm{h}(s)$$

$$ \bm{H}_{3D}(r,s,t) = \bm{h}(r) \otimes \bm{h}(s) \otimes \bm{h}(t)$$

### Node numbering
A linear hexahedron has nodes arranged in a way that the connectivity starts at `[-1,-1,-1]` where nodes are connected counterclockwise at`z=-1` in a first step. Finally the same applies for `z=1`. For arbitrary order elements the first axis goes from `-1` to `1`, then the second axis  from `-1` to `1` and finally the third axis  from `-1` to `1`.

```python
# Linear hexahedron with eight nodes

nodes = np.array([
    [-1,-1,-1], #0
    [ 1,-1,-1], #1
    [ 1, 1,-1], #2
    [-1, 1,-1], #3
    [-1,-1, 1], #4
    [ 1,-1, 1], #5
    [ 1, 1, 1], #6
    [-1, 1, 1], #7
])

connectivity = np.array([[0,1,2,3,4,5,6,7]])
```