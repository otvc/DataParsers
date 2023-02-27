This folder is contained file with configuration of parsers.
Let's introduce in settings fields:

    - `save_to_mongo`: check if you want saving parsed data into mongo
    - `dbname`: name of database in which you want upload data
    - `connection`: connection string to database (if you select csv that it path to folder in which files should be saved)
    - `viewed_pages_path`: path to folder in which save page which parser saw (not tested on this moment)
    - `saved`: boolean value which check that viewed pages were saved or not
    - `collections`: name of collections in which data will save 

ufcstats settings:

    - `base_source` - particular source on page with fights (http://www.ufcstats.com/statistics/events/completed?page=2)
    from which you want start parse (until last page)

consult settings:

    - `base_source` - particular url on page which have pattern like this (https://www.consultant.ru/popular/).
    If you want parse not popular codes you can change this url
    - `graph` - contain graph on which we should stroll and extract information. See `Stroller` about for understanding

yurist-online settings:

    - `base_source` - pattern source page to walking on which containing many questions.
    I'm change numeber in this pattern to check another page 
    - `first_page_number` - page from which we start to walking 
    - `last_page_number` - number page on which we will end parse. 