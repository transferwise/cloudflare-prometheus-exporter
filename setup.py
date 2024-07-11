#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

requirements = [
    "click",
    "requests",
    "pyyaml",
    "prometheus_client",
    "python-json-logger",
    "schedule",
]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="Wise::Observability",
    author_email="observability@transferwise.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    description="Prometheus exporter powered by Cloudflare GraphQL API.",
    entry_points={"console_scripts": ["cfexpose=cloudflare_exporter.cli:main"]},
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="cloudflare_exporter",
    name="cloudflare-prometheus-exporter",
    packages=find_packages(include=["cloudflare_exporter", "cloudflare_exporter.gql"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/transferwise/cloudflare-exporter",
    version="0.4.0",
    zip_safe=False,
)
