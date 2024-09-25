from langchain_openai import ChatOpenAI

from app.llm.chain import GeneralChain
from app.llm.prompt_templates import QueryExpansionTemplate
from app.config import settings


class QueryExpansion:
    @staticmethod
    def generate_response(query: str, to_expand_to_n: int = 3) -> list[str]:
        query_expansion_template = QueryExpansionTemplate()
        prompt_template = query_expansion_template.create_template(to_expand_to_n)
        model = ChatOpenAI(
            model=settings.Silicon_model_v1,
            openai_api_key=settings.Silicon_api_key1,
            openai_api_base=settings.Silicon_base_url,
            temperature=0
        )

        chain = GeneralChain().get_chain(
            llm=model, output_key="expanded_queries", template=prompt_template
        )

        response = chain.invoke({"question": query})
        result = response["expanded_queries"]

        queries = result.strip().split(query_expansion_template.separator)
        stripped_queries = [
            stripped_item for item in queries if (stripped_item := item.strip())
        ]

        return stripped_queries
