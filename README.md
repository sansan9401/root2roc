# Quick start
* Try
```
python root2roc.py -h
ls -1 root/|xargs -i python root2roc.py root/{} roc/{}.txt
```

* It determine the 'flavor', 'type', and 'charge' using file name.
If it is not correct, export config, edit manually, and rerun using new config file.  
```
## Example
python root2roc.py root/medium_electron_2016 /dev/null --export-config config.json
vi config.json ## edit
python root2roc.py config.json out.txt
```
