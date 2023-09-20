import inspect
import jinja2
from loguru import logger


def render_description(file_name_or_path: str, *args, **kwargs) -> str | None:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(''))
    exc = None

    # function to return content of file
    def _get_content_of_file(path: str) -> str:
        template = env.get_template(path)
        b = template.render(*args, **kwargs)
        return b

    # Trying load directly
    try:
        return _get_content_of_file(file_name_or_path)

    except Exception as error:
        # Set exception
        exc = error

    try:
        # Translate path from "/src/routes/v1/order_router.py" to "/docs/routes/v1/order_router/get_order.md"
        router_file = inspect.stack()[1].frame.f_locals['__name__']
        result_path = router_file.replace('src', 'docs').replace('.', '/') + "/" + file_name_or_path + ".md"
        return _get_content_of_file(result_path)

    except Exception as error:
        # Set exception
        exc = error

    if exc:
        logger.error(f"Error in render_description, file_name_or_path={file_name_or_path}, exception: {exc}")

    return None
