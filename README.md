
# Command Line Password manager

A simple password manager which is encrypted digital vault that stores secure login credential information of your app or sites.

## Features

all the password are stored in **encrypted form**.

- [x]  insert credential
- [x]  update credential
- [x]  generate Master Password
- [x]  display Password of specfic app
- [x]  display All data
- [ ]  update Master password


## Used Module

| Library |  Purpose                |
| :-------- | :------------------------ |
| `passlib` |  use for **Master** password ([reference](https://passlib.readthedocs.io/en/stable/narr/hash-tutorial.html)) |
| `sqlite3` |  light-weight **database**   |
| `prettytable` | to **decorate** output text  |
| `getpass` | **hide** input password |
| `cryptography` | to **encrypt** password |


## How to use

```bash
git clone https://github.com/kumresh/cli_password_manager.git
```

### Install requirement module

```bash
pip install prettytable cryptography
```

### pyhton version

- > python 3.10 

### run program

```bash 
cd cli_password_manager
```

```bash
python password_manager.py
```



