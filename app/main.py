import litserve as ls

class SimpleLitAPI(ls.LitAPI):
    def setup(self, device):
        self.model = None

    def predict(self, prompt):
        # `prompt` is a list of dictionary containing role and content
        # example: [{'role': 'user', 'content': 'How can I help you today?'}]
        yield "This is a sample generated output"

if __name__ == "__main__":
    # Enable the OpenAISpec in LitServer
    api = SimpleLitAPI()
    server = ls.LitServer(api, spec=ls.OpenAISpec())
    server.run(port=9000)
