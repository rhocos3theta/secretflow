# Copyright 2023 Ant Group Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Union

from secretflow.device import PYU, HEUObject, PYUObject, proxy

from ..component import Component, Devices
from .node_bucket_sum_cache_internal import NodeCache


# consists of worker bucket sum caches (HEUObject or PYUObject)
# and a single label holder's split info caches
class NodeWiseCache(Component):
    def __init__(self):
        self.worker_caches = {}

    def show_params(self):
        return

    def set_params(self, _: dict):
        return

    def get_params(self, _: dict):
        return

    def set_devices(self, devices: Devices):
        self.worker_caches = {
            worker: NodeCache()
            for worker in devices.workers
            if worker != devices.label_holder
        }
        self.worker_caches[devices.label_holder] = proxy(PYUObject)(NodeCache)(
            device=devices.label_holder
        )

    def reset(self):
        for device in self.worker_caches:
            self.worker_caches[device].reset()

    def reset_node(self, node_index: int):
        for device in self.worker_caches:
            self.worker_caches[device].reset_node(node_index)

    def collect_node_bucket_sum(
        self, worker: PYU, node_index: int, bucket_sum: Union[HEUObject, PYUObject]
    ):
        self.worker_caches[worker].collect_node_bucket_sum(node_index, bucket_sum)

    def batch_collect_node_bucket_sums(
        self,
        worker: PYU,
        node_indices: List[int],
        bucket_sums: List[Union[HEUObject, PYUObject]],
    ):
        self.worker_caches[worker].batch_collect_node_bucket_sums(
            node_indices, bucket_sums
        )

    def get_node_bucket_sum(self, worker: PYU, node_index: int) -> PYUObject:
        return self.worker_caches[worker].get_node(node_index)

    def batch_get_node_bucket_sum(
        self, worker: PYU, node_indices: List[int]
    ) -> List[PYUObject]:
        return [
            self.get_node_bucket_sum(worker, node_index) for node_index in node_indices
        ]
