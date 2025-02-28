from setuptools import setup, find_packages

setup(
    name="bazi",
    version="1.3.5",
    # packages=find_packages(),
    packages=["bazi"],  # Explicitly include the 'app' package
    package_dir={"bazi": "app"},  # Map the 'app' package to the 'app' directory
    install_requires=[
        # Add any dependencies your package needs here
        "lunarcalendar",
        "uvicorn",
        "fastapi",
        "ephem",
        "pandas",
        "tqdm",
        'pytz',
        "numpy",
        "yfinance",
        "yahooquery",
        "scikit-learn",
        "Flask",
        "google-cloud-bigquery",
        "python-dotenv",
        "db-dtypes",
        "ib_insync",
        "google-cloud-secret-manager",
        "functions-framework",
        "numba",
    ],
    description="A package for Bazi calculations",
    author="Gary Lam",
    author_email="garylamj@gmail.com",
    url="https://github.com/gazaay/four-pillars",
)