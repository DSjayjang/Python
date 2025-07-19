from distutils.core import setup
from Cython.Build import cythonize

# setup(ext_modules = cythonize('cythonfn.pyx', compiler_directives = {'language_level': '3'}))
# setup(ext_modules = cythonize('cythonfn2.pyx', compiler_directives = {'language_level': '3'}))
# setup(ext_modules = cythonize('cythonfn3.pyx', compiler_directives = {'language_level': '3'}))

import numpy as np
setup(ext_modules=cythonize("cythonfn4.pyx", compiler_directives={"language_level": "3"}),
        include_dirs=[np.get_include()])

