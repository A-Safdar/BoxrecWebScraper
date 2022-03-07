# BoxrecWebScraper

Currently this project only supports Boxrec
TODO: Add support for different websites

## NOTE: Project will not work without a config file for the scraper

-  Please ensure that within the root director of the project, you add a json file called `config.json`
-  Within the file add the following structure:

```
{
   "url": "https://boxrec.com",
   "username": "<ENTER-YOUR-USERNAME>",
   "password": "<ENTER-YOUR-PASSWORD>",
   "loginButton": {
      "by": "<ENTER-BY-ATTRIBUTE-NAME>",
      "text": "<ENTER-BY-ATTRIBUTE-VALUE>"
   },
   "loginForm": {
      "usernameEntry": {
         "by": "<ENTER-BY-ATTRIBUTE-NAME>",
      "text": "<ENTER-BY-ATTRIBUTE-VALUE>"
      },
      "passwordEntry": {
         "by": "<ENTER-BY-ATTRIBUTE-NAME>",
      "text": "<ENTER-BY-ATTRIBUTE-VALUE>"
      },
      "submitCredentials": {
         "by": "<ENTER-BY-ATTRIBUTE-NAME>",
      "text": "<ENTER-BY-ATTRIBUTE-VALUE>"
      }
   },
   "cookies": {
      "container": {
         "by": "<ENTER-BY-ATTRIBUTE-NAME>",
      "text": "<ENTER-BY-ATTRIBUTE-VALUE>"
      },
      "button": {
         "by": "<ENTER-BY-ATTRIBUTE-NAME>",
      "text": "<ENTER-BY-ATTRIBUTE-VALUE>"
      }
   }
}
```
