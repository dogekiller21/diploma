from typing import Any

from fastapi import datastructures
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

templates = Jinja2Templates(directory="app/templates")


@pass_context
def https_url_for(context: dict, name: str, **path_params: Any) -> datastructures.URL:
    """
    https://stackoverflow.com/questions/70521784/fastapi-links-created-by-url-for-in-jinja2-template-use-http-instead-of-https

    """
    request = context.get("request")
    http_url = request.url_for(name, **path_params)

    # Replace 'http' with 'https'
    return http_url.replace(scheme="https")


templates.env.globals["https_url_for"] = https_url_for
