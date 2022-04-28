from setuptools import setup, find_packages

VERSION = '0.1'
DESCRIPTION = 'Processing of Lung CT'
LONG_DESCRIPTION = 'A module with functionalities for processing Lung CT in DICOM format.'

# Setting up
setup(
    name="lungctproc",
    version=VERSION,
    author="Victor Nani",
    author_email="<victornani07@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pydicom', 'matplotlib', 'numpy', 'scipy', 'skimage', 'opencv-python', 'ipywidgets', 'plotly', 'shapely', 'Pillow', 'mpl-toolkits'],
    keywords=['python', 'lung', 'ct', 'processing'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Healthcare Industry",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ]
)