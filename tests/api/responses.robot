*** Settings ***
Resource    ../resources/http_keywords.robot
Suite Setup  Log      Starting responses suite


*** Test Cases ***
Get JSON Response And Validate
    [Documentation]    Validate GET /get returns expected structure and args propagation
    ${params}=    Create Dictionary    q=test    lang=en
    ${resp}=    Get    /get    params=${params}
    ${json}=    ${resp}.json()
    Should Be True    '${json["url"]}' != ''
    Should Contain    ${json["args"]}    q
    Should Contain    ${json["args"]}    lang

Post JSON And Inspect Request
    [Documentation]    Send dynamic JSON and ensure httpbin reflects it in 'json'
    ${payload}=    Generate User
    ${resp}=    Post Json    /post    json_payload=${payload}
    ${json}=    ${resp}.json()
    Should Be Equal As Strings    ${json["json"]["email"]}    ${payload["email"]}