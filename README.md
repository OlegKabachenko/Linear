# Linear System Solver

A Python application for solving square systems of linear algebraic equations using iterative, stochastic, and matrix-based methods. The application includes parallel execution support and preprocessing strategies designed to improve the suitability of a system for numerical computation.

## Features

- Solving square systems of linear algebraic equations.
- Four numerical methods: Jacobi, Gauss–Seidel, Monte Carlo, and the matrix method.
- Parallel execution support for the Jacobi and matrix methods.
- Preprocessing strategies, including Jacobi preconditioning and spectral-radius-based preprocessing.
- Configurable solver parameters and convergence tolerances.
- Numerical computation using Python's scientific computing ecosystem.

## Numerical Methods

### Jacobi Method

An iterative method that calculates successive approximations using values from the previous iteration. The implementation supports parallel execution.

### Gauss–Seidel Method

An iterative method that updates the solution components sequentially, using the most recently computed values within each iteration.

### Monte Carlo Method

A stochastic method that estimates the solution by generating random trajectories associated with a representation of the linear system. The method supports fixed-length and dynamic-length trajectories.

### Matrix Method

A matrix-based method for computing the solution of a linear system. 

## Preprocessing Strategies

Preprocessing is applied before solving a system to improve its numerical properties or satisfy the requirements of the selected method.

### Jacobi Preconditioning

Uses diagonal scaling based on the diagonal elements of the coefficient matrix. When the diagonal elements are nonzero, the system can be scaled so that the coefficient matrix has unit diagonal entries.

This approach has low computational cost. However, it does not guarantee improved convergence for every matrix.

### Spectral-Radius-Based Preprocessing

Uses spectral properties of the iteration matrix to assess or adjust the system for iterative computation. The spectral radius is particularly important for convergence of iterative processes and the Neumann-series representation used by the Monte Carlo method.

### No Preprocessing

Allows the original system to be solved without applying a preprocessing transformation.

## Technologies

- **Python** — application logic and numerical algorithms.
- **NumPy** — matrix and vector operations.
- **SciPy** — scientific computing and numerical utilities.
- **Multiprocessing** — parallel execution using multiple processes.

