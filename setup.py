#!/usr/bin/env python
import os
import fnmatch
from setuptools import setup

package_data_dirs = (
    'django_snippify/media/',
    'django_snippify/templates/'
)
package_data_files = []
for dir in package_data_dirs:
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            failed = False
            for pattern in ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*'):
                if fnmatch.fnmatchcase(filename, pattern):
                    failed = True
                    break
            if failed:
                continue
            package_data_files.append(os.path.join(*filepath.split(os.sep)[1:]))
setup(
    name='django-timetrack',
    version='0.1',
    description='Django app that collets snippets, allows comments and following users',
    author='Alexandru Plugaru',
    author_email='alexandru.plugaru@gmail.com',
    url='http://github.com/humanfromearth/django-snippify',
    license='GPLv3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    packages=['django_snippify'],
    package_data={'django_snippify': package_data_dirs},
    requires=[
        'django (>=1.2)',
        'piston',
        'django_whoosh',
    ],
)
