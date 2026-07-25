from fastapi import FastAPI

app = FastAPI(title="Basic API")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the basic FastAPI app!"}


@app.get("/greet/{name}")
def greet_name(name: str) -> dict[str, str]:
    return {"message": f"Hello, {name}!"}


@app.get("/greet")
def greet_query(name: str = "friend") -> dict[str, str]:
    return {"message": f"Hello, {name}!"}
