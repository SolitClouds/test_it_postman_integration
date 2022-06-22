# Test IT Postman integration
This set of scripts was initially developed by Solit Clouds Test Automation team 
in order to be able to upload structure of postman collections in Test-It and execute them in future

PLease note that it is just MVP to prove the hypothesis that we can create AT first 
and then sync it with TMS system and get all advantages of it.

Detailed showcase and explanation you can find in video https://www.youtube.com/watch?v=B7YevcWveYc&t=10749s

## Usage

Provided scripts could be used with collections of following structure, where the case is presented as a folder 
that contains specific requests. 
Other levels of folder will represent section in Test IT
PLease note that the scripts were debuged only on structure with two levels of sections

![image](https://user-images.githubusercontent.com/89986347/145394023-bc5734a6-004d-4a82-adfe-96c243d97aab.png)


For reporting please use also https://www.npmjs.com/package/json-summary 

### collections_parser.py
This script is intended to transform you postman collections to single collections that contains only one case

### sync_collections_with_test_it.py
You can use this script to upload you collections in Test IT

### set_result_of_test.py
You can incorporate this script to you pipeline in order to parse output of json-summary report to Test IT
