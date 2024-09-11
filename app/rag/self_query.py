from langchain_openai import ChatOpenAI
from app.llm.chain import GeneralChain
from app.llm.prompt_templates import SelfQueryTemplate
from app.config import settings


class SelfQuery:
    @staticmethod
    def generate_response(query: str) -> str | None:
        prompt = SelfQueryTemplate().create_template()
        model = ChatOpenAI(model=settings.OPENAI_MODEL_ID, temperature=0)

        chain = GeneralChain().get_chain(
            llm=model, output_key="metadata_filter_value", template=prompt
        )

        response = chain.invoke({"question": query})
        result = response.get("metadata_filter_value", "none")

        if result.lower() == "none":
            return None

        return result
