from setuptools import setup, find_packages

setup(
    name="imageeditor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "customtkinter>=5.0.0",
        "opencv-python>=4.7.0",
        "Pillow>=9.0.0",
        "numpy>=1.21.0",
    ],
    dependency_links=[
        "file:///Users/tinoue/Development.local/lib/image_gui_template#egg=image_gui_app"
    ],
    entry_points={
        "console_scripts": [
            "imageeditor=src.main:main",
        ]
    },
    author="Your Name",
    description="Professional Image Editor using image_gui_template library",
    python_requires=">=3.8",
)
