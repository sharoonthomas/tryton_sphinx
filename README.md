A Tryton ERP module to enable Sphinx Search Server integration

This is a work in progress, more information can be found at:
http://trytonsearch.blogspot.com

**THIS IS A WORK IN PROGRESS.**

## Installation of the Sphinx Search Server - THE EASY WAY
**If you have an Ubuntu Server >= 10.04 , YOU ARE LUCKY:**

### ASSUMPTIONS
* I assume that have a clean Ubuntu machine version >= 10.04
* I assume that you want to use PostgreSQL 9 as you Database
* I assume that you don't have postgres install
* I assume that you already have Tryton installed
* I assume that you sudo (or root) access on the target machine
* I will install PostgreSQL from a ppa
* I will use `python fabric` to make the installation
* I assume that you have backed up you data

**If you understood the assumptions, then you can proceed:**
        
    easy-install pip
    pip install fabric 
    wget http://github.com/dfamorato/tryton_sphinx/extras/fabfile.py 
    fab -u `username` -H `target_machine` install_sphinx_search install_tryton_sphinx

## Installation requirements

* TrytonSphinx module requires you to have either a `PostgreSQL` or a `MySQL` database.
* You will need the `build-essentials` package in order to compile Sphinx Search Server
from the source code.


## TODO:

### Installation of the Sphinx Search Server - THE HARD WAY

    DOCUMENTATION TO BE DONE
    
### Building Sphinx Search Config File  

    FUNCTIONALITY EXISTS, DOCUMENTATION TO BE DONE

### Building Sphinx Search Index
    
    FUNCTIONALITY EXISTS, DOCUMENTATION  TO BE DONE
      
### Examples on how to query the search index

    WORK TO BE DONE
    
### Regenerate Sphinx Search Server configuration
   
    FUNCTIONALITY EXISTS, DOCUMENTATION  TO BE DONE
