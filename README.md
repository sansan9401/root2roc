# Efficiency
* Electron
  * [v15](roc/ElectronEff_v15)
  * [v13](roc/ElectronEff_v13)
  * [v12](roc/ElectronEff_v12)
  * [v11](roc/ElectronEff_v11)
  * [v9.2](roc/ElectronEff_v9_2)
  * [v9.1](roc/ElectronEff_v9_1)
  * [v9](roc/ElectronEff_v9)
  * [v8](roc/ElectronEff_v8)
  * [v7](roc/ElectronEff_v7)
  * [v4_1](roc/ElectronEff_v4_1)
  * [v4](roc/ElectronEff_v4)
* Muon
  * [v15](roc/MuonEff_v15)
  * [v14](roc/MuonEff_v14)
  * [v13](roc/MuonEff_v13)
  * [v11](roc/MuonEff_v11)
  * [v10.0](roc/MuonEff_v10_0)
  * [v9.2](roc/MuonEff_v9_2)
  * [v9.1](roc/MuonEff_v9_1)
  * [v8](roc/MuonEff_v8)
  * [v4](roc/MuonEff_v4)

# Quick start
* Try
```
usage: root2roc.py [-h] [--export-config CONFIG_OUT] [--debug] input [output]

Convert root file efficiency to Rochester txt format

positional arguments:
  input                 directory containing root files or json file
  output                output path

optional arguments:
  -h, --help            show this help message and exit
  --export-config CONFIG_OUT
                        export config as json format
  --debug               debug mode

## EXAMPLE
python root2roc.py root/ElectronEff_v7/electron_2018
### if you don't specify the output path, it will be same with the input path except root/->roc/
```

* It determine the 'flavor', 'type', and 'charge' using file name.
If it is not correct, export config, edit manually, and rerun using new config file.  
```
## Example
python root2roc.py root/medium_electron_2016 /dev/null --export-config config.json
vi config.json ## edit
python root2roc.py config.json out.txt
```
