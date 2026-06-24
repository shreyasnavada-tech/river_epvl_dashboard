package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

var credentials = map[string]string{
	"username": "nagendrar@rideriver.com",
	"password": "H0cdmthHB4",
}

var tokenRequestBody = map[string]any{
	"user":      credentials,
	"logintype": "password",
	"impersReq": true,
}

func marshallJson(body any) []byte {
	value, err := json.Marshal(body)
	if err != nil {
		fmt.Printf("The following error occured %v\n", err)
	}
	return value
}

func rcvIntellicarRequests(requestApi string, requestType string, requestBody ...any) (any, any) {

	var request *http.Request
	var err error

	client := &http.Client{}
	switch requestType {
	case "GET":
		request, err = http.NewRequest(requestType, requestApi, nil)
		request.Header.Add("Accept", "application/json")
		request.Header.Add("Content-Type", "application/json")
		if err != nil {
			fmt.Printf("The following error occured %v\n", err)
		}

	case "POST":
		requestBody := marshallJson(requestBody)
		request, err = http.NewRequest(requestType, requestApi, bytes.NewBuffer(requestBody))
		request.Header.Add("Accept", "application/json")
		request.Header.Add("Content-Type", "application/json")
		if err != nil {
			fmt.Printf("The following error occured %v\n", err)
		}
	}
	fmt.Println(request)
	resp, err := client.Do(request)
	fmt.Println(resp)
	if err != nil {
		return resp, err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	return string(body), err
}

func main() {
	fmt.Println(("The value of pointer"))
	body, err := rcvIntellicarRequests("https://apiplatform.intellicar.in/sso/gettokensinglesignon", "POST", tokenRequestBody)
	fmt.Println(body, err)
}
