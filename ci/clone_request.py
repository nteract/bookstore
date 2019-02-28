import requests
import nbformat


def main(queries):
    return requests.get(f"http://localhost:8888/api/bookstore/clone{queries}")


if __name__ == "__main__":
    res = main("?s3_bucket=nteract-notebooks&s3_key=published/whateverwewant.json")
    print(res.json())
    res = main("/?s3_bucket=nteract-notebooks&s3_key=published/whateverwewant.json")
    print(res.json())
