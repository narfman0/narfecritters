from setuptools import setup, find_packages

setup(
    name="pokeclone",
    version="0.0.1",
    description=("Ingest video data to render smb3 eh manip stimuli"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="pokeclone",
    author="Jon Robison",
    author_email="narfman0@blastedstudios.com",
    license="LICENSE",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "dataclass_wizard",
        "pygame",
        "pygame_gui",
        "pytmx",
    ],
    test_suite="tests",
)
