import sys
import os
from pathlib import Path
from setuptools import Extension, setup, find_packages
from Cython.Build import cythonize
import numpy as np
import glob

# Get the absolute path of clib/
clib_dir = Path(__file__).resolve().parent

# Define build directory
BUILD_DIR = clib_dir / "build"
BUILD_DIR.mkdir(parents=True, exist_ok=True)

# Check if running on macOS
is_macos = sys.platform == "darwin"
# Define the directory for C source files
c_files = glob.glob(str(clib_dir / "src/c/*.c"))

# Define the directory for Cython files
# Check for DEBUG mode
DEBUG = os.getenv("DEBUG", "0") == "1"
if DEBUG:
    print("Running in DEBUG mode")
extra_compile_args = []
extra_link_args = []

if not DEBUG:
    extra_compile_args = [
        "-O3",
        "-march=native",
        "-mtune=native",
        "-mfpmath=sse",
        "-ffast-math",
        "-funroll-loops",
        "-flto",
        "-fopenmp",
        "-fno-plt",
        "-fvisibility=hidden",
        "-fdata-sections",
        "-ffunction-sections",
        "-fomit-frame-pointer",
        "-DNDEBUG",
        "-falign-functions=32",
        "-falign-loops=32",
    ]
    extra_link_args = ["-fopenmp", "-flto", "-Wl,-O1"]

    # Remove unsupported linker flags for macOS
    if not is_macos:
        extra_link_args.extend(
            ["-Wl,--gc-sections", "-Wl,--as-needed", "-Wl,-strip-all"]
        )

extensions = [
    Extension(
        "*",  # Specify actual module name
        ["src/cython_modules/*.pyx", *c_files],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        include_dirs=[np.get_include(), str(clib_dir / "src/include")],
    )
]

setup(
    name="clib",
    packages=find_packages(include=["clib", "clib.src", "clib.src.cython_modules"]),
    package_dir={
        "cython_modules": "src/cython_modules",
        "clib": str(BUILD_DIR),
        "clib.src": "src",
    },
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",
            "boundscheck": not DEBUG,
            "wraparound": not DEBUG,
            "initializedcheck": not DEBUG,
            "nonecheck": not DEBUG,
            "cdivision": not DEBUG,
            "embedsignature": not DEBUG,
            "infer_types": not DEBUG,
            "profile": DEBUG,
            "linetrace": DEBUG,
        },
        cache=True,
    ),
    include_dirs=[np.get_include(), str(clib_dir / "src/include")],
    zip_safe=False,
)
