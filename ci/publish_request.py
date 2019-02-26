import requests
import nbformat 
# from nbformat.v4 import new_notebook

def main():
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(source="Hello"))
    requests.post("http://localhost:8888/api/bookstore/clone/pathy", json=nbformat.writes(nb))

if __name__ == "__main__":
    main()
