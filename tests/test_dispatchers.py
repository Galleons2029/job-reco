# -*- coding: utf-8 -*-
# @Time    : 2024/9/17 17:43
# @Author  : Galleons
# @File    : test_dispatchers.py

"""
这里是文件说明
"""


import unittest
from unittest.mock import patch, MagicMock

from app.feature_pipeline.data_logic.dispatchers import ChunkingDispatcher
from app.feature_pipeline.models.raw import ArticleRawModel, PostsRawModel, RepositoryRawModel
from app.feature_pipeline.models.base import DataModel

class TestChunkingDispatcher(unittest.TestCase):

    @patch('app.feature_pipeline.data_logic.chunking_data_handlers.PostChunkingHandler')
    @patch('app.feature_pipeline.data_logic.chunking_data_handlers.ArticleChunkingHandler')
    @patch('app.feature_pipeline.data_logic.chunking_data_handlers.RepositoryChunkingHandler')
    def test_dispatch_chunker(self, MockRepoHandler, MockArticleHandler, MockPostHandler):
        # Mock chunk methods to return a list of DataModel instances
        mock_post_handler_instance = MockPostHandler.return_value
        mock_post_handler_instance.chunk.return_value = [
            PostsRawModel(platform="Twitter", content={"text": "This is a post"}, author_id="author1",  type="posts"),
            PostsRawModel(platform="Twitter", content={"text": "Another post"}, author_id="author2", type="posts")
        ]


        # Test with PostsRawModel
        post_data = PostsRawModel(platform="Twitter", content={"text": "Test post"}, author_id="author1", type="posts")
        post_chunks = ChunkingDispatcher.dispatch_chunker(post_data)
        self.assertIsInstance(post_chunks, list, "Returned object should be a list")
        self.assertGreater(len(post_chunks), 0, "List should not be empty")
        self.assertTrue(all(isinstance(chunk, DataModel) for chunk in post_chunks), "All items in the list should be instances of DataModel")

if __name__ == '__main__':
    unittest.main()
