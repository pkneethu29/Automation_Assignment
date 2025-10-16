*** Settings ***
Resource    ../resources/http_keywords.robot


*** Test Cases ***
Health endpoint returns 200
    ${resp}=    Get    /status/200
    Should Be Equal As Integers    ${resp}.status_code    200

Dynamic Delay Endpoint Response
    ${resp}=    Get    /delay/1
    Should Be Equal As Integers    ${resp}.status_code    200