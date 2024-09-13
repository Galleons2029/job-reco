# server.py
import litserve as ls

# STEP 1: DEFINE YOUR MODEL API
class SimpleLitAPI(ls.LitAPI):
    def setup(self, device):
        self.model = lambda x: x**2

    def decode_request(self, request):
        return request["input"]

    def predict(self, x):
        return self.model(x)

    def encode_response(self, output):
        return {"output": output}


# STEP 2: START THE SERVER
if __name__ == "__main__":
    api = SimpleLitAPI()
    server = ls.LitServer(api, accelerator="gpu")
    server.run(port=9000)