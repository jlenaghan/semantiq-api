# Installation 

Clone the repository: 

```zsh
git clone https://github.com/jlenaghan/semantiq-api
cd semantiq-api
```

Check your python version

```zsh
python --version
```

Set up virtualenv
```zsh
virtualenv --python <above_python_version> env
source ./env/bin/activate
pip install -r requirements.txt
brew install uvicorn
```

Run API

```zsh
uvicorn api.main:app --reload
```


