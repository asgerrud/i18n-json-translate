# i18n JSON translate

A Python script that automatically translates a directory of i18n JSON files

## Getting started

Install dependencies

```bash
pip install –r requirements.txt
```

Run the script

```bash
$ python3 translate.py [directory] [from_language]
```

`directory` specifies directory containing the json files (default = `./` )  
`from_language` specifies the json language file to base translations on (default = `en`)

---

##  Run anywhere from terminal

(Optional) Find your python executable path, using `which python3`  
Replace the path on `line 1` in `translator.py` with the path outputted by the command

Add execute permission to file:
```
chmod +x translator.py
```

Add folder to path
```bash
# inside shell configuration file (~/.zshrc, ~/.bashrc etc.)
export I18N_JSON_TRANSLATE="$HOME/path/to/this/directory"
export PATH="$I18N_JSON_TRANSLATE:$PATH"

# (Optional) add command alias
command_name=$I18N_JSON_TRANSLATE"translator.py"
```

Run the command
```bash
$ translator.py [directory] [from_language]
```

