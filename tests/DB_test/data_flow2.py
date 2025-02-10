import random
from typing import Optional, Tuple
import numpy as np
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
from bytewax.inputs import DynamicSource, StatelessSourcePartition

"""设置一个数据流以处理数字流中的缺失数据。

本示例演示如何使用 bytewax 库创建一个数据流
处理一系列数字，其中每第 5 个数字缺失（用 np.nan 表示）。
数据流使用有状态操作符来使用窗口均值插补策略填补缺失值。
"""

# 开始导入

import bytewax.operators as op

# 结束导入

# 开始随机数据
class RandomNumpyData(StatelessSourcePartition):
    """生成带有缺失值的随机数字序列。

    数据源生成一个序列
    包含 100 个数字，其中每第 5 个数字
    缺失（用 np.nan 表示），
    其余是 0 到 10 之间的随机整数。
    """

    def __init__(self):
        """初始化数据源。"""
        self._it = enumerate(range(100))

    def next_batch(self):
        """生成下一批数据。

        Returns:
            list: 包含数据的元组列表。
                如果项目的索引能被 5 整除，
                数据为 np.nan，否则为随机数。
        """
        i, item = next(self._it)
        if i % 5 == 0:
            return [("data", np.nan)]
        else:
            return [("data", random.randint(0, 10))]

class RandomNumpyInput(DynamicSource):
    """根据工作器分布生成随机数据。

    封装基于分布式处理中的工作器分布的动态数据生成类。
    """

    def build(self, step_id, _worker_index, _worker_count):
        """构建数据源。"""
        return RandomNumpyData()

# 结束随机数据

# 开始数据流
flow = Dataflow("map_eg")
input_stream = op.input("input", flow, RandomNumpyInput())
# 结束数据流

# 开始窗口数组
class WindowedArray:
    """窗口化的 Numpy 数组。

    创建一个 Numpy 数组以运行窗口统计。
    """

    def __init__(self, window_size: int) -> None:
        """初始化窗口数组。

        参数:
            window_size (int): 窗口的大小。
        """
        self.last_n = np.empty(0, dtype=float)
        self.n = window_size

    def push(self, value: float) -> None:
        """将值推入窗口数组。

        参数:
            value (float): 要推入数组的值。
        """
        if np.isscalar(value) and np.isreal(value):
            self.last_n = np.insert(self.last_n, 0, value)
            try:
                self.last_n = np.delete(self.last_n, self.n)
            except IndexError:
                pass

    def impute_value(self) -> float:
        """在窗口数组中插补下一个值。

        返回:
            tuple: 包含原始值和插补值的元组。
        """
        return np.nanmean(self.last_n)

# 结束窗口数组

# 开始有状态插补器
class StatefulImputer:
    """在维护状态的同时插补值。

    这个类是一个有状态对象，封装了一个
    WindowedArray，并提供一个方法来使用这个
    数组插补值。
    该对象的 impute_value 方法被传递给
    op.stateful_map，因此状态在
    调用此方法时保持不变。
    """

    def __init__(self, window_size):
        """初始化有状态插补器。

        参数:
            window_size (int): 窗口的大小。
        """
        self.windowed_array = WindowedArray(window_size)

    def impute_value(self, key, value):
        """在窗口数组中插补值。"""
        return self.windowed_array.impute_value(value)

# 结束有状态插补器

# 开始数据流插补
def mapper(
    window: Optional[WindowedArray], orig_value: float
) -> Tuple[Optional[WindowedArray], Tuple[float, float]]:
    """在数字流中插补缺失值。"""
    if window is None:
        window = WindowedArray(10)
    if not np.isnan(orig_value):
        window.push(orig_value)
        new_value = orig_value
    else:
        new_value = window.impute_value()  # 计算派生值。

    return (window, (orig_value, new_value))

imputed_stream = op.stateful_map("impute", input_stream, mapper)
# 结束数据流插补

# 开始输出
op.output("output", imputed_stream, StdOutSink())
# 结束输出
