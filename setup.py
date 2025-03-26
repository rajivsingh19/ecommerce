from setuptools import setup, find_packages
setup(
    name="ecommerce",  
    version="0.1.0",
    description="A simple e-commerce application using FastAPI, SQLAlchemy, JWT, and Streamlit",
    author="Rajiv Singh",
    author_email="rajivsinghrajput19@gmail.com",
    packages=find_packages(include=["backend", "backend.*", "forntend", "forntend.*"]),  # Include both backend and frontend
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "cryptography",
        "pyjwt",
        "streamlit",
        "requests"
    ],
)
