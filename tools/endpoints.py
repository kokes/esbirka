import json

if __name__ == "__main__":
    with open("openapi.json") as f:
        data = json.load(f)

    endpoints = []
    for path, v in data["paths"].items():
        for method, det in v.items():
            qparams, responses = [], []
            for param in det["parameters"]:
                if param["in"] == "query":
                    qparams.append(param["name"])
            for status, resp in det["responses"].items():
                responses.append(status)
            endpoints.append((method, path, responses, qparams))

    endpoints.sort(key=lambda x: "{" not in x[1] and len(x[3]) == 0, reverse=True)
    print(f"Found {len(endpoints)} endpoints.")
    for method, path, responses, qparams in endpoints:
        print(f"{method.upper()} {path} {qparams}")
        # print(f"{method.upper()} {path} {responses} {qparams}")
