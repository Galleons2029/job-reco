"""
RAG业务模块
"""

# from qwak_inference import RealTimeClient
from langchain_openai import ChatOpenAI

from app.services.evaluation import evaluate_llm
from app.llm.prompt_templates import InferenceTemplate
from app.services.monitoring import PromptMonitoringManager
from app.rag.retriever import VectorRetriever
from app.config import settings

from app.utils.logging import get_logger
logger = get_logger(__name__)


class WEYON_LLM:
    def __init__(self) -> None:
        # self.qwak_client = RealTimeClient(
        #     model_id=settings.QWAK_DEPLOYMENT_MODEL_ID,
        #     model_api=settings.QWAK_DEPLOYMENT_MODEL_API,
        # )
        self._client = ChatOpenAI(
            model="Qwen/Qwen2.5-7B-Instruct",
            openai_api_key=settings.Silicon_api_key1,
            openai_api_base=settings.Silicon_base_url,
        )
        # self._client = OpenAI(
        #     api_key=settings.Silicon_api_key1,
        #     base_url=settings.Silicon_base_url,
        # )
        self.template = InferenceTemplate()
        self.prompt_monitoring_manager = PromptMonitoringManager()

    def generate(
        self,
        query: str,
        enable_rag: bool = False,
        enable_evaluation: bool = False,
        enable_monitoring: bool = False,
    ) -> dict:
        prompt_template = self.template.create_template(enable_rag=enable_rag)
        prompt_template_variables = {
            "question": query,
        }

        if enable_rag is True:
            retriever = VectorRetriever(query=query)
            hits = retriever.retrieve_top_k(
                k=settings.TOP_K, to_expand_to_n_queries=settings.EXPAND_N_QUERY
            )
            context = retriever.rerank(hits=hits, keep_top_k=settings.KEEP_TOP_K)  # list
            prompt_template_variables["context"] = context

            prompt = prompt_template.format(question=query, context=context)
        else:
            prompt = prompt_template.format(question=query)

        # input_ = pd.DataFrame([{"instruction": prompt}]).to_json()

        # response: list[dict] = self.qwak_client.predict(input_)
        # answer = response[0]["content"][0]
        # response = self._client.chat.completions.create(
        #     model='Qwen/Qwen2.5-7B-Instruct',
        #     messages=[{
        #         'role': 'user',
        #         'content': "抛砖引玉是什么意思呀"
        #     }],
        #     stream=False
        # )
        # answer = response.choices[0].message.content
        answer = self._client.invoke(prompt).content

        if enable_evaluation is True:
            evaluation_result = evaluate_llm(query=query, output=answer)
        else:
            evaluation_result = None

        if enable_monitoring is True:
            if evaluation_result is not None:
                metadata = {"llm_evaluation_result": evaluation_result}
            else:
                metadata = None

            self.prompt_monitoring_manager.log(
                prompt=prompt,
                prompt_template=prompt_template.template,
                prompt_template_variables=prompt_template_variables,
                output=answer,
                metadata=metadata,
            )
            self.prompt_monitoring_manager.log_chain(
                query=query, response=answer, eval_output=evaluation_result
            )

        return {"answer": answer, "llm_evaluation_result": evaluation_result}
