# Description 
This reposetory contain classes for parse sites:
- www.ufcstats.com.
- www.consultant.ru
- www.yurist-online.net

# Requirements
You should have ```chromedriver.exe``` in folder with ```Stroller.py```

# Usage
If you want use parser and to save data in same foldaer in csv format then just write in console:
```
python run_parser.py
```
Another configurations of using is shown in block ```Configuration```

# Configuration
## Flags
When you use running `run_parser.py`, the following flags are available:

    - `-p`,  `--parsers`, use for choose cite which you want parse and chose from ['ufcstats', 'consult', 'yurist-online']
    - `-c`, `--config`, link to file with configuration for each parser
If you want to see all settings, then check [config](./config) folder

By default:
```
-p = ufcstats
-c = './config/config.yaml'
```