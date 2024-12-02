from fastapi import FastAPI
from .pypi.json_scraper import get_package_data
from .conda.scrape_conda import get_conda_package_data

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/pypi/{package_name}")
async def pypi(package_name):
    data = get_package_data(package_name)
    return {"ecosystem": "pypi", "package_name": package_name, "data": data}


@app.get("/conda/{channel}/{package_name}")
async def conda(channel, package_name):
    data = get_conda_package_data(channel, package_name)
    return {
        "ecosystem": "conda",
        "channel": channel,
        "package_name": package_name,
        "data": data,
    }


@app.get("/git/{git_url}")
async def git(git_url):
    data = get_package_data(package_name)
    # return {"ecosystem": "pypi", "package_name": package_name, "data": data}
