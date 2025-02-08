import os

import pytest
from django.conf import settings
from pytest_docker_tools import container

# We only modify the database settings for the test suite if TEST_USE_EXTERNAL_DATABASE is not set
# to a non-empty value.
if os.environ.get("TEST_USE_EXTERNAL_DATABASE", "") == "":
    postgres_container = container(
        scope="session",
        image="postgres",
        environment={
            "POSTGRES_USER": "pytest-user",
            "POSTGRES_PASSWORD": "pytest-pass",
            "POSTGRES_DB": "pytest-db",
        },
        ports={
            "5432/tcp": None,
        },
    )

    @pytest.fixture(scope="session")
    def django_db_modify_db_settings(
        django_db_modify_db_settings_parallel_suffix, postgres_container
    ):
        """
        Modify database settings based on the postgres docker container we spun up.
        """
        host, port = postgres_container.get_addr("5432/tcp")
        db_settings = {
            "HOST": host,
            "PORT": port,
            "NAME": "pytest-db",
            "USER": "pytest-user",
            "PASSWORD": "pytest-pass",
        }

        for db_item in settings.DATABASES.values():
            db_item.update(db_settings)
            db_item.get("TEST", {}).update(db_settings)
