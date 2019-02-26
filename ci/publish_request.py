import requests
import nbformat 

def main(nb):
    return requests.get(f"http://localhost:8888/api/bookstore/clone/{nb}")


if __name__ == "__main__":
    res = main("published/whateverwewant.json")
    print(res.json())
