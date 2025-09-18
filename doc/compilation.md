# Compilation

## General

miniPIC uses CMake as a build system.

```bash
mkdir build
cd build
cmake ../ 
make
```

<img title="Warning" alt="Warning" src="./doc/images/warning.png" height="20"> Building in the root directory is not supported.

<img title="Warning" alt="Warning" src="./doc/images/warning.png" height="20"> By default, the code is compiled in sequential mode.


## Options

CMake useful options:

- `-DCMAKE_CXX_COMPILER=<compiler choice>`: specify the compiler to use

Backends:

- `-DBACKEND`: enable to choose the backend

| CPU backends      | Description                         |
|-------------------|-------------------------------------|
| sequential        | Sequential CPU version              |
| openmp            | OpenMP CPU version                  |

| GPU backends            | Description                                          |
|-------------------------|------------------------------------------------------|
| kokkos                  | GPU-oriented Kokkos version using dual views         |
| kokkos_dualview_unified | Kokkos dualview using unified memory                 |
| kokkos_unified          | Kokkos using normal views and unified memory         |

Others:

- `-DDEBUG=ON/OFF`: enable/disable debug mode (`OFF` by default)
- `-DTEST=ON/OFF`: enable/disable tests mode (for CI, `OFF` by default)
- `-DWARNING=ON/OFF`: enable/disable warnings (`OFF` by default)

- `-DDEVICE`: enable to tune the code for a specific device (required for some backends)

| CPU devices   | Description                         |
|---------------|-------------------------------------|
| nvidia_grace  | Nvidia Grace CPU                    |
| amd_genoa     | AMD Genoa CPU                       |

| GPU devices   | Description                         |
|---------------|-------------------------------------|
| nvidia_v100   | Nvidia V100 GPU                     |
| nvidia_a100   | Nvidia A100 GPU                     |
| nvidia_h100   | Nvidia H100 GPU                     |
| nvidia_gh200  | Nvidia GH200 GPU                    |
| amd_mi250     | AMD MI250 GPU                       |
| amd_mi300     | AMD MI300 GPU                       |
| intel_pvc     | Intel Ponte Vecchio GPU             |

## Examples

- Sequential compilation

```bash
cmake ../ 
make
```

- OpenMP compilation using g++

```bash
cmake ../ -DCMAKE_CXX_COMPILER=g++ -DBACKEND=openmp
make
```

- Kokkos compilation using clang++ for CPU

```bash
cmake ../ -DCMAKE_CXX_COMPILER=clang++ -DBACKEND=kokkos 
make
```

- Kokkos compilation using nvcc for Nvidia V100

```bash
cmake ../ -DCMAKE_CXX_COMPILER=nvcc -DBACKEND=kokkos -DDEVICE=nvidia_v100
make
```