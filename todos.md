# i want to each endpoints block each other process, this is an example for better clarity:
- when person A hit /scrape/csv, process scraping happens, lets say process A
- while process A still ongoing person B hit /scrape/csv, and it will show message that scraping process still ongoing
- not just block the same endpoints, it will block all endpoints in this app except 1 endpoint (endpoint to check the process is finished yet)
- im using gunicorn so you can make adjustment to it if you need
- i want to add one more endpoint to check scraping process, it will return status and message of scraping process.
  status process: "ON PROGRESS" and "FINISHED" 
- find the best and effective mechanism to implement  
