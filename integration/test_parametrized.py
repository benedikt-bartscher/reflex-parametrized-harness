from collections.abc import Generator
import time
import pytest
import functools

from reflex.testing import AppHarness
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


def ReflexApp(param: int) -> None:
    import reflex as rx

    # raise Exception(param)
    app = rx.App()

    def index() -> rx.Component:
        return rx.text(param, id="hello")

    app.add_page(index)


@pytest.fixture
def magic_number(request: pytest.FixtureRequest) -> int:
    return request.param


@pytest.fixture
def app(
    tmp_path_factory: pytest.TempPathFactory,
    magic_number: int,
) -> Generator[AppHarness, None, None]:
    app_source = functools.partial(ReflexApp, param=magic_number)
    with AppHarness.create(
        root=tmp_path_factory.mktemp("reflex_app"),
        app_source=app_source,  # pyright: ignore[reportArgumentType]
    ) as harness:
        yield harness


@pytest.fixture
def driver(app: AppHarness) -> Generator[WebDriver, None, None]:
    driver = app.frontend()
    try:
        yield driver
    finally:
        driver.quit()


@pytest.mark.parametrize("magic_number", [42, 43])
def test_app(
    driver: WebDriver,
    magic_number: int,
) -> None:
    time.sleep(1)

    txt = driver.find_element(By.ID, "hello")
    assert txt.text == str(magic_number)
