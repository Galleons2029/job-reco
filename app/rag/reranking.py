from langchain_openai import ChatOpenAI

from app.llm.chain import GeneralChain
from app.llm.prompt_templates import RerankingTemplate
from app.config import settings


class Reranker:
    @staticmethod
    def generate_response(
        query: str, passages: list[str], keep_top_k: int
    ) -> list[str]:
        reranking_template = RerankingTemplate()
        prompt_template = reranking_template.create_template(keep_top_k=keep_top_k)

        model = ChatOpenAI(
            model=settings.Silicon_model_v1,
            openai_api_key=settings.Silicon_api_key1,
            openai_api_base=settings.Silicon_base_url,
            temperature=0
        )
        chain = GeneralChain().get_chain(
            llm=model, output_key="rerank", template=prompt_template
        )

        stripped_passages = [
            stripped_item for item in passages if (stripped_item := item.strip())
        ]
        passages = reranking_template.separator.join(stripped_passages)
        response = chain.invoke({"question": query, "passages": passages})

        result = response["rerank"]
        reranked_passages = result.strip().split(reranking_template.separator)
        stripped_passages = [
            stripped_item
            for item in reranked_passages
            if (stripped_item := item.strip())
        ]

        return stripped_passages
